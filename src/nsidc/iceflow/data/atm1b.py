from __future__ import annotations

import collections
import datetime as dt
import logging
import re
from enum import Enum
from pathlib import Path
from typing import cast

import h5py
import numpy as np
import pandas as pd
import pandera as pa
from gps_timemachine.gps import leap_seconds
from loguru import logger
from numpy.typing import DTypeLike

from nsidc.iceflow.data.models import ATM1BDataFrame

"""
The dtypes used to read any of the input ATM1B input files.

The ATM1B QFIT format:
https://nsidc.org/sites/nsidc.org/files/files/ReadMe_qfit.txt
"""
ATM1B_DTYPE_10_BE = np.dtype(
    [
        ("rel_time", ">i4"),
        ("latitude", ">i4"),
        ("longitude", ">i4"),
        ("elevation", ">i4"),
        ("xmt_sigstr", ">i4"),
        ("rcv_sigstr", ">i4"),
        ("azimuth", ">i4"),
        ("pitch", ">i4"),
        ("roll", ">i4"),
        ("gps_time", ">i4"),
    ]
)
ATM1B_DTYPE_10_LE = ATM1B_DTYPE_10_BE.newbyteorder("<")

ATM1B_DTYPE_12_BE = np.dtype(
    [
        ("rel_time", ">i4"),
        ("latitude", ">i4"),
        ("longitude", ">i4"),
        ("elevation", ">i4"),
        ("xmt_sigstr", ">i4"),
        ("rcv_sigstr", ">i4"),
        ("azimuth", ">i4"),
        ("pitch", ">i4"),
        ("roll", ">i4"),
        ("gps_pdop", ">i4"),
        ("pulse_width", ">i4"),
        ("gps_time", ">i4"),
    ]
)
ATM1B_DTYPE_12_LE = ATM1B_DTYPE_12_BE.newbyteorder("<")

ATM1B_DTYPE_14_BE = np.dtype(
    [
        ("rel_time", ">i4"),
        ("latitude", ">i4"),
        ("longitude", ">i4"),
        ("elevation", ">i4"),
        ("xmt_sigstr", ">i4"),
        ("rcv_sigstr", ">i4"),
        ("azimuth", ">i4"),
        ("pitch", ">i4"),
        ("roll", ">i4"),
        ("passive_signal", ">i4"),
        ("passive_footprint_latitude", ">i4"),
        ("passive_footprint_longitude", ">i4"),
        ("passive_footprint_synthesized_elevation", ">i4"),
        ("gps_time", ">i4"),
    ]
)
ATM1B_DTYPE_14_LE = ATM1B_DTYPE_14_BE.newbyteorder("<")


class Endian(Enum):
    LITTLE = 1
    BIG = 2


def _data_dtype(endianness: Endian, field_count: int) -> DTypeLike:
    """Return the appropriate QFIT dtype based on the given endianness and
    number of fields in the file."""
    return {
        Endian.LITTLE: {
            10: ATM1B_DTYPE_10_LE,
            12: ATM1B_DTYPE_12_LE,
            14: ATM1B_DTYPE_14_LE,
        },
        Endian.BIG: {
            10: ATM1B_DTYPE_10_BE,
            12: ATM1B_DTYPE_12_BE,
            14: ATM1B_DTYPE_14_BE,
        },
    }[endianness][field_count]


def _file_dtype(filepath: Path) -> DTypeLike:
    """Return the dtype for the given file."""
    data_endianness = Endian.BIG

    record_size = np.fromfile(filepath, dtype=">i4", count=1)[0]
    if record_size >= 100:
        record_size = np.fromfile(filepath, dtype="<i4", count=1)[0]
        if record_size >= 100:
            raise ValueError("invalid record size found")
        data_endianness = Endian.LITTLE

    field_count = int(record_size / 4)

    dtype = _data_dtype(data_endianness, field_count)

    return dtype


def _blatm1bv1_date(fn) -> dt.date:
    """Return the date from the given BLATM1B filename."""
    fn_date = None

    m = re.search(r"BLATM1B_(\d{8})", fn)
    if m:
        fn_date_str = m.group(1)
    else:
        m = re.search(r"BLATM1B_(\d{6})", fn)
        if not m:
            err_msg = f"Failed to extract date from BLATM1B v1 file: {fn}"
            raise RuntimeError(err_msg)

        fn_date_str = m.group(1)
        if int(fn_date_str[:2]) > 9:
            fn_date_str = "19" + fn_date_str
        else:
            fn_date_str = "20" + fn_date_str

    fn_date = dt.datetime.strptime(fn_date_str, "%Y%m%d").date()

    return fn_date


def _ilatm1b_date(fn: str) -> dt.date:
    """Return the date from the given ILATM1B filename."""
    m = re.search(r"_(\d{8})_", fn)
    if not m:
        err = f"Failed to extract date from filepath: {fn}"
        raise RuntimeError(err)
    fn_date = m.group(1)
    return dt.datetime.strptime(fn_date, "%Y%m%d").date()


def _shift_lon(lon):
    """Shifts longitude values from [0,360] to [-180,180]"""
    if lon >= 180.0:
        return lon - 360.0
    return lon


def _augment_with_optional_values(df, original_shape):
    """Add columns (w/ `np.nan`) to the dataframe depending on what fields
    the original data did not include.
    """
    rows, cols = original_shape
    missing = np.full(shape=(rows,), fill_value=np.nan)

    if cols == 10:
        df["gps_pdop"] = missing
        df["pulse_width"] = missing
        df["passive_signal"] = missing
        df["passive_footprint_latitude"] = missing
        df["passive_footprint_longitude"] = missing
        df["passive_footprint_synthesized_elevation"] = missing
    elif cols == 12:
        df["passive_signal"] = missing
        df["passive_footprint_latitude"] = missing
        df["passive_footprint_longitude"] = missing
        df["passive_footprint_synthesized_elevation"] = missing
    elif cols == 14:
        df["gps_pdop"] = missing
        df["pulse_width"] = missing
    else:
        raise ValueError("Unknown number of columns: cannot augment")


def _strip_header(data):
    """Slice the header from the given data; skip the first row because we
    know it's a valid header; any rows with negative first elements
    are also header rows.
    """
    idx = 1
    while data[idx][0] < 0:
        idx += 1

    return data[idx:]


def _utc_datetime(
    gps_time: pd.Series[int], file_date: dt.date
) -> pd.Series[pd.Timestamp]:
    """Return `utc_datetime` Series, with values calculated from the given
    date and the GPS time values, with a leap second adjustment to the GPS
    times.
    """
    tdf = pd.DataFrame()
    tdf["hour"] = (gps_time / 1e7).astype(np.uint8)
    tdf["minute"] = ((gps_time % 1e7) / 1e5).astype(np.uint8)
    tdf["second"] = ((gps_time % 1e5) / 1e3).astype(np.uint8)
    tdf["millisecond"] = (gps_time % 1e3).astype(np.uint16)
    tdf["year"] = file_date.year
    tdf["month"] = file_date.month
    tdf["day"] = file_date.day

    ls = int(leap_seconds(dt.datetime(file_date.year, file_date.month, file_date.day)))
    utc = pd.to_datetime(tdf).to_numpy() - np.timedelta64(ls, "s")

    return pd.Series(utc)


def _atm1b_qfit_dataframe(filepath: Path) -> pd.DataFrame:
    """Read an ATM1B QFIT file into a DataFrame, stripping bad data if
    necessary.
    """
    dtype = _file_dtype(filepath)

    raw_data = np.fromfile(filepath, dtype=dtype)
    raw_data = _strip_header(raw_data)

    if dtype in (ATM1B_DTYPE_14_LE, ATM1B_DTYPE_14_BE):
        # Ignore records with invalid data (this occurs in the 14-word
        # format records containing passive brightness data)
        logging.info("Before filter. Data shape: %s", raw_data.shape)
        raw_data = raw_data[
            (raw_data["latitude"] != 0) & (raw_data["elevation"] != -9999)
        ]
        logging.info("After filter. Data shape: %s", raw_data.shape)

        if raw_data.shape[0] == 0:
            logging.warning("After removal of bad data, file contains no valid data.")
            return pd.DataFrame()

    return pd.DataFrame(raw_data)


def _atm1b_qfit_data(filepath: Path, file_date: dt.date) -> pd.DataFrame:
    """Returns an ATM1B DataFrame read from a QFIT file, performing all
    necessary conversions on the data.
    """
    df = _atm1b_qfit_dataframe(filepath)
    original_shape = df.shape

    df["latitude"] = df["latitude"] * 1e-6
    df["longitude"] = df["longitude"] * 1e-6
    df["longitude"] = df["longitude"].apply(_shift_lon)
    # elevation values are natively stored as Meters 10**-3. We convert them
    # back to meters here.
    df["elevation"] = df["elevation"] * 1e-3
    df["elevation"] = df["elevation"].astype(np.float32)
    df["utc_datetime"] = _utc_datetime(df["gps_time"], file_date)
    _augment_with_optional_values(df, original_shape)

    return df


# TODO: extract this for reuse with other data products.
def _normalize_itrf_str(itrf_str: str) -> str:
    """Normalizes common ITRF strings into ones recognizable by proj.

    E.g., "ITRF2020" is common, but proj only recognizes "ITRF20".
    """
    itrf_str = itrf_str.upper()
    try:
        itrf_str = {
            "ITRF05": "ITRF2005",
            "ITRF08": "ITRF2008",
            "ITRF2000": "ITRF20",
        }[itrf_str]
    except KeyError:
        pass

    return itrf_str


def _qfit_file_header(filepath: Path) -> str:
    """Return the header string from a QFIT file."""
    dtype = np.dtype([("record_type", ">i4"), ("header", ">S44")])

    record_size = np.fromfile(filepath, dtype=">i4", count=1)[0]
    if record_size >= 100:
        record_size = np.fromfile(filepath, dtype="<i4", count=1)[0]
        if record_size >= 100:
            raise ValueError("invalid record size found")
        dtype = np.dtype([("record_type", "<i4"), ("header", "<S44")])

    raw_data = np.fromfile(filepath, dtype=dtype)

    # In 'normal' files with headers, we skip the first two records
    # and only keep those whose record_type is negative.
    if len(raw_data) > 2:
        idx = 2
        while raw_data[idx]["record_type"] < 0:
            idx += 1
        header = raw_data[2:idx]
        return "".join([r["header"].decode("UTF-8") for r in header])

    err = "Failed to read qfit file header for {filepath}"
    raise RuntimeError(err)


# NOTE: it is unknown for sure how these ITRF date ranges were established. This
# is based on prior work in `valkyrie`, and no formal documentation exists. I
# think these were generated from reading the ITRF out of all of the ATM1B data
# files (some context here:
# https://nsidc.slack.com/archives/C4V5EFN1L/p1558544556037600). See the
# docstring of `_infer_qfit_itrf` for more context.
# TODO: a typed-dict might be better here.
GranuleItrfRange = collections.namedtuple("GranuleItrfRange", "start end itrf")
ATM1B_GRANULE_ITRFS = [
    GranuleItrfRange(dt.date(1993, 6, 23), dt.date(1996, 6, 5), "ITRF93"),
    GranuleItrfRange(dt.date(1997, 4, 25), dt.date(1997, 5, 28), "ITRF94"),
    GranuleItrfRange(dt.date(1998, 6, 27), dt.date(1999, 5, 25), "ITRF96"),
    GranuleItrfRange(dt.date(2000, 5, 12), dt.date(2001, 5, 27), "ITRF97"),
    GranuleItrfRange(dt.date(2001, 12, 18), dt.date(2002, 11, 21), "ITRF2000"),
    GranuleItrfRange(dt.date(2002, 11, 22), dt.date(2002, 11, 22), "ITRF97"),
    GranuleItrfRange(dt.date(2002, 11, 23), dt.date(2002, 12, 13), "ITRF2000"),
    GranuleItrfRange(dt.date(2002, 12, 14), dt.date(2002, 12, 14), "ITRF97"),
    GranuleItrfRange(dt.date(2002, 12, 15), dt.date(2007, 5, 11), "ITRF2000"),
    GranuleItrfRange(dt.date(2007, 9, 10), dt.date(2011, 5, 16), "ITRF2005"),
    GranuleItrfRange(dt.date(2011, 10, 12), dt.date(2018, 5, 1), "ITRF2008"),
]


def _qfit_itrf_from_date(date: dt.date) -> str:
    """Return a strting representing the ITRF for a qfit file based on date.

    This function should only be used for looking up the ITRF for qfit files that
    lack a header. It is based on a hard-coded list with no formal provenance.
    """

    def _find(gdt, i, lower, upper) -> str | None:
        # Binary search for the correct ITRF to make this fast. If we
        # do a naive linear search, it can run up to 10x longer.
        g = ATM1B_GRANULE_ITRFS[i]
        if gdt < g.start:
            if i > lower:
                return _find(gdt, (i - lower) // 2, lower, i)
            else:
                return None
        elif gdt <= g.end:
            itrf_str = g.itrf
            return cast(str, itrf_str)
        elif i < (upper - 1):
            return _find(gdt, (upper + i) // 2, i, upper)
        else:
            return None

    lower, upper = (0, len(ATM1B_GRANULE_ITRFS))
    i = (upper - lower) // 2
    result = _find(date, i, lower, upper)
    if result is None:
        err_msg = f"Failed to find ITRF for {date=}"
        raise RuntimeError(err_msg)

    return result


def _infer_qfit_itrf(filepath: Path, date: dt.date) -> str:
    """Takes an ILATM1B/BLATM1B qfit filepath and returns a string representing
    the ITRF.

    This function infers the ITRF based on the qfit file header, which is
    described here:
    https://nsidc.org/sites/nsidc.org/files/files/ReadMe_qfit.txt

    Failing that, this function falls back to a hard-coded ITRF based on the
    date.

    This function does its "best" based on prior work, and places trust in that
    prior work. However, this should be more closely reviewd. See
    https://github.com/nsidc/iceflow/issues/35.
    """
    header = _qfit_file_header(filepath)
    results = re.finditer(r"itrf\d{2,4}", header)
    itrfs = list({result.group() for result in results})

    itrf_for_date = _qfit_itrf_from_date(date)

    if len(itrfs) == 1:
        itrf_from_qfit_header = _normalize_itrf_str(itrfs[0])
        if itrf_for_date != itrf_from_qfit_header:
            warn_msg = (
                f"ITRF in qfit header for {filepath=} is inconsistent with expected ITRF for {date=}."
                f" qfit header has {itrf_from_qfit_header}. Expected {itrf_for_date}."
                f" Using the ITRF found in the header: {itrf_from_qfit_header}"
            )
            logger.warning(warn_msg)

        return itrf_from_qfit_header

    warn_msg = (
        f"Failed to find ITRF in qfit header file for {filepath}."
        f" Falling back on hard-coded ITRF for {date=}: {itrf_for_date}"
    )
    logger.warning(warn_msg)

    return itrf_for_date


def _extract_itrf_from_h5_file(filepath: Path) -> str:
    """Extract ITRF from the h5 filepath (ILATM1B v2)."""
    with h5py.File(filepath, "r") as ds:
        itrf = str(ds["ancillary_data"]["reference_frame"][:][0], encoding="utf8")
    itrf = _normalize_itrf_str(itrf)

    return itrf


def extract_itrf(filepath: Path, date: dt.date) -> str:
    ext = filepath.suffix

    if ext == ".qi":
        return _infer_qfit_itrf(filepath, date=date)
    elif ext == ".h5":
        return _extract_itrf_from_h5_file(filepath)

    err = f"Failed to read ITRF from unrecognized file: {filepath}"
    raise RuntimeError(err)


def _ilatm1bv2_dataframe(filepath: Path) -> pd.DataFrame:
    """Returns an ATM1B DataFrame read from an HDF5 file, performing all
    necessary scaling and type conversion.
    """
    variables = [
        ("rel_time", "instrument_parameters/rel_time", 1000, np.int32),
        ("latitude", "latitude", None, None),
        ("longitude", "longitude", None, None),
        ("elevation", "elevation", None, None),
        ("xmt_sigstr", "instrument_parameters/xmt_sigstr", None, None),
        ("rcv_sigstr", "instrument_parameters/rcv_sigstr", None, None),
        ("azimuth", "instrument_parameters/azimuth", 1000, np.int32),
        ("pitch", "instrument_parameters/pitch", 1000, np.int32),
        ("roll", "instrument_parameters/roll", 1000, np.int32),
        ("gps_pdop", "instrument_parameters/gps_pdop", 10, np.int32),
        ("pulse_width", "instrument_parameters/pulse_width", 1, np.uint32),
        ("gps_time", "instrument_parameters/time_hhmmss", 1000, np.uint32),
    ]
    df = pd.DataFrame()
    with h5py.File(filepath, "r") as atmv2:
        for key, name, scale_factor, dtype in variables:
            if scale_factor and dtype:
                df[key] = (atmv2[name][:] * scale_factor).astype(dtype)
            else:
                df[key] = atmv2[name][:]

    return df


def _ilatm1bv2_data(fn: Path, file_date: dt.date) -> pd.DataFrame:
    """Returns an ATM1B DataFrame, performing all necessary conversions /
    augmentation on the data.
    """
    df = _ilatm1bv2_dataframe(fn)
    original_shape = df.shape

    df["longitude"] = df["longitude"].apply(_shift_lon)
    df["utc_datetime"] = _utc_datetime(df["gps_time"], file_date)
    _augment_with_optional_values(df, original_shape)

    return df


@pa.check_types()
def atm1b_data(filepath: Path) -> ATM1BDataFrame:
    """
    Return the atm1b data given a filename.

    Parameters
    ----------
    filepath
        The filepath to read.

    Returns
    -------
    data
        The atm1b (pandas.DataFrame) data.
    """
    # Example filenames:
    # ILATM1B_20140430_110310.ATM4BT4.h5
    # ILATM1B_20111104_181304.ATM4BT4.qi
    # BLATM1B_20060522_145449.qi
    # BLATM1B_20041127atm2_210316jr.lutF.qi
    filename = filepath.name

    # Find the date, which corresponds to the product version.
    match = re.search(r".*_(\d{4})\d{4}.*", filename)
    if not match:
        err = f"Failed to recognize {filename} as ATM1B data."
        raise RuntimeError(err)

    year = int(match.group(1))

    if year >= 2013:
        file_date = _ilatm1b_date(filename)
        data = _ilatm1bv2_data(filepath, file_date)
    elif year >= 2009:
        file_date = _ilatm1b_date(filename)
        data = _atm1b_qfit_data(filepath, file_date)
    else:
        file_date = _blatm1bv1_date(filename)
        data = _atm1b_qfit_data(filepath, file_date)

    itrf = extract_itrf(filepath, date=file_date)
    data["ITRF"] = itrf

    data = data.set_index("utc_datetime")

    return ATM1BDataFrame(data)
