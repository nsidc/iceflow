import datetime as dt
from enum import Enum
import glob
import logging
import os
import re
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
from gps_timemachine.gps import leap_seconds

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


def _data_dtype(endianness, field_count):
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


def _file_metadata(fn):
    """Return the dtype for the given file."""
    data_endianness = Endian.BIG

    record_size = np.fromfile(fn, dtype=">i4", count=1)[0]
    if record_size >= 100:
        record_size = np.fromfile(fn, dtype="<i4", count=1)[0]
        if record_size >= 100:
            raise ValueError("invalid record size found")
        data_endianness = Endian.LITTLE

    field_count = int(record_size / 4)

    dtype = _data_dtype(data_endianness, field_count)

    return dtype


def _blatm1bv1_date(fn):
    """Return the date from the given BLATM1B filename."""
    fn_date = None

    m = re.search(r"BLATM1B_(\d{8})", fn)
    if m:
        fn_date = m.group(1)
    else:
        m = re.search(r"BLATM1B_(\d{6})", fn)
        if m:
            fn_date = m.group(1)
            if int(fn_date[:2]) > 9:
                fn_date = "19" + fn_date
            else:
                fn_date = "20" + fn_date

    if fn_date:
        fn_date = dt.datetime.strptime(fn_date, "%Y%m%d")

    return fn_date


def _ilatm1b_date(fn: str):
    """Return the date from the given ILATM1B filename."""
    m = re.search(r"_(\d{8})_", fn)
    fn_date = m.group(1)
    return dt.datetime.strptime(fn_date, "%Y%m%d")


def _shift_lon(lon):
    """Shifts longitude values from [0,360] to [-180,180]"""
    if lon >= 180.0:
        return lon - 360.0
    return lon


def _augment_with_optional_values(df, original_shape):
    """Add columns (w/ zeros) to the dataframe depending on what fields
    the original data did not include."""
    rows, cols = original_shape
    zeros = np.zeros((rows,), dtype=np.int32)

    if cols == 10:
        df["gps_pdop"] = zeros
        df["pulse_width"] = zeros
        df["passive_signal"] = zeros
        df["passive_footprint_latitude"] = zeros
        df["passive_footprint_longitude"] = zeros
        df["passive_footprint_synthesized_elevation"] = zeros
    elif cols == 12:
        df["passive_signal"] = zeros
        df["passive_footprint_latitude"] = zeros
        df["passive_footprint_longitude"] = zeros
        df["passive_footprint_synthesized_elevation"] = zeros
    elif cols == 14:
        df["gps_pdop"] = zeros
        df["pulse_width"] = zeros
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


def _utc_datetime(gps_time, file_date):
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

    ls = int(leap_seconds(file_date))
    utc = pd.to_datetime(tdf).values - np.timedelta64(ls, "s")

    return pd.Series(np.datetime_as_string(utc).astype("|S"))


def _atm1b_qfit_dataframe(fn):
    """Read an ATM1B QFIT file into a DataFrame, stripping bad data if
    necessary.
    """
    dtype = _file_metadata(fn)

    raw_data = np.fromfile(fn, dtype=dtype)
    raw_data = _strip_header(raw_data)

    if dtype == ATM1B_DTYPE_14_LE or dtype == ATM1B_DTYPE_14_BE:
        # Ignore records with invalid data (this occurs in the 14-word
        # format records containing passive brightness data)
        logging.info("Before filter. Data shape: {}".format(raw_data.shape))
        raw_data = raw_data[
            (raw_data["latitude"] != 0) & (raw_data["elevation"] != -9999)
        ]
        logging.info("After filter. Data shape: {}".format(raw_data.shape))

        if raw_data.shape[0] == 0:
            logging.warning("After removal of bad data, file contains no valid data.")
            return pd.DataFrame()

    return pd.DataFrame(raw_data)


def _atm1b_qfit_data(fn, file_date):
    """Returns an ATM1B DataFrame read from a QFIT file, performing all
    necessary conversions on the data.
    """
    df = _atm1b_qfit_dataframe(fn)
    original_shape = df.shape

    df["latitude"] = df["latitude"] * 1e-6
    df["longitude"] = df["longitude"] * 1e-6
    df["longitude"] = df["longitude"].apply(_shift_lon)
    df["elevation"] = df["elevation"] * 1e-3
    df["elevation"] = df["elevation"].astype(np.float32)
    df["utc_datetime"] = _utc_datetime(df["gps_time"], file_date)
    _augment_with_optional_values(df, original_shape)

    return df


def _ilatm1bv2_dataframe(fn):
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
    with h5py.File(fn, "r") as atmv2:
        for key, name, scale_factor, dtype in variables:
            if scale_factor and dtype:
                df[key] = (atmv2[name][:] * scale_factor).astype(dtype)
            else:
                df[key] = atmv2[name][:]

    return df


def _ilatm1bv2_data(fn, file_date):
    """Returns an ATM1B DataFrame, performing all necessary conversions /
    augmentation on the data.
    """
    df = _ilatm1bv2_dataframe(fn)
    original_shape = df.shape

    df["longitude"] = df["longitude"].apply(_shift_lon)
    df["utc_datetime"] = _utc_datetime(df["gps_time"], file_date)
    _augment_with_optional_values(df, original_shape)

    return df


def df_columns(df):
    """Return a list of column names corresponding to the data encoded and
    returned by the `row_values` function. This should be the database
    column names corresponding to the values returned by that
    function.

    Parameters
    ----------
    df
        Unused. For ATM1B, the list of columns is the same regardless of
        the source file.

    Returns
    -------
        The list of column names for the data frame.
    """
    return [
        "utc_datetime",
        "point",
        "gps_time",
        "rel_time",
        "azimuth",
        "pitch",
        "roll",
        "xmt_sigstr",
        "rcv_sigstr",
        "gps_pdop",
        "pulse_width",
        "passive_signal",
        "passive_footprint_latitude",
        "passive_footprint_longitude",
        "passive_footprint_synthesized_elevation",
    ]


def row_values(row):
    """Return a bytestring containing comma-delimited values for a given
    row in the dataset. This string can be used in a SQL statement to
    insert the data into a matching database table.

    Parameters
    ----------
    row
        The row tuple from a pandas.DataFrame that was obtained by calling
        atm1b_data and augmented with `utc_datetime`.

    Returns
    -------
    row
        The row as a comma-delimited bytestring (`bytes`).
    """
    return b"%s,SRID=4326;POINT(%f %f %f),%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n" % (
        row.utc_datetime,
        row.longitude,
        row.latitude,
        row.elevation,
        row.gps_time,
        row.rel_time,
        row.azimuth,
        row.pitch,
        row.roll,
        row.xmt_sigstr,
        row.rcv_sigstr,
        row.gps_pdop,
        row.pulse_width,
        row.passive_signal,
        row.passive_footprint_latitude,
        row.passive_footprint_longitude,
        row.passive_footprint_synthesized_elevation,
    )


def atm1b_data(filepath: Path) -> pd.DataFrame:
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
    filename = filepath.name

    # Find the date, which corresponds to the product version.
    match = re.search(r".*_(\d{4})\d{4}_.*", filename)
    if not match:
        raise RuntimeError(f"Failed to recognize {filename} as ATM1B data.")

    year = int(match.group(1))

    if year >= 2013:
        return _ilatm1bv2_data(filepath, _ilatm1b_date(filename))
    elif year >= 2009:
        return _atm1b_qfit_data(filepath, _ilatm1b_date(filename))
    else:
        return _atm1b_qfit_data(filepath, _blatm1bv1_date(filename))
