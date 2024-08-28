from __future__ import annotations

import datetime as dt
import glob
import os
import re
from collections import namedtuple

import numpy as np
import pandas as pd
import pandera as pa

from nsidc.iceflow.data.models import ILVIS2DataFrame

# The user guide indicates ILVIS2 data uses ITRF2000 as a reference frame:
# https://nsidc.org/sites/default/files/documents/user-guide/ilvis2-v001-userguide.pdf
ILVIS2_ITRF = "ITRF2000"

Field = namedtuple("Field", ["name", "type", "scale_factor"])

"""
See: https://lvis.gsfc.nasa.gov/Data/Data_Structure/DataStructure_LDS104.html

Note: The LVIS site (above) and NSIDC data files use different names
for the fields. The list of field tuples below matches the
documentation on the LVIS site. This is done to simplify the code and
ease the mental mapping of the v1.0.4 and v2.0.2b fields to the
database.  The mapping between the names used below (same as LVIS
docs) and the field names used in the NSIDC files is:


  CLON = LONGITUDE_CENTROID
  CLAT = LATITUDE_CENTROID
  ZC = ELEVATION_CENTROID
  GLON = LONGITUDE_LOW
  GLAT = LATITUDE_LOW
  ZG = ELEVATION_LOW
  HLON = LONGITUDE_HIGH
  HLAT = LATITUDE_HIGH
  ZH = ELEVATION_HIGH

"""
ILVIS2_V104_FIELDS = [
    Field("LFID", None, np.uint64),
    Field("SHOTNUMBER", None, np.uint64),
    Field("TIME", 10**6, np.uint64),
    Field("CLON", 10**6, np.int64),
    Field("CLAT", 10**6, np.int64),
    Field("ZC", 10**6, np.int64),
    Field("GLON", None, np.float64),
    Field("GLAT", None, np.float64),
    Field("ZG", None, np.float64),
    Field("HLON", 10**6, np.int64),
    Field("HLAT", 10**6, np.int64),
    Field("ZH", 10**6, np.int64),
]

"""
See: https://lvis.gsfc.nasa.gov/Data/Data_Structure/DataStructure_LDS202.html
Note: Version 2.0.2b was used for Greenland 2017
"""
ILVIS2_V202b_FIELDS = [
    Field("LFID", None, np.uint64),
    Field("SHOTNUMBER", None, np.uint64),
    Field("TIME", 10**6, np.uint64),
    Field("GLON", None, np.float64),
    Field("GLAT", None, np.float64),
    Field("ZG", None, np.float64),
    Field("HLON", 10**6, np.int64),
    Field("HLAT", 10**6, np.int64),
    Field("ZH", 10**6, np.int64),
    Field("TLON", 10**6, np.int64),
    Field("TLAT", 10**6, np.int64),
    Field("ZT", 10**6, np.int64),
    Field("RH10", 10**3, np.int64),
    Field("RH15", 10**3, np.int64),
    Field("RH20", 10**3, np.int64),
    Field("RH25", 10**3, np.int64),
    Field("RH30", 10**3, np.int64),
    Field("RH35", 10**3, np.int64),
    Field("RH40", 10**3, np.int64),
    Field("RH45", 10**3, np.int64),
    Field("RH50", 10**3, np.int64),
    Field("RH55", 10**3, np.int64),
    Field("RH60", 10**3, np.int64),
    Field("RH65", 10**3, np.int64),
    Field("RH70", 10**3, np.int64),
    Field("RH75", 10**3, np.int64),
    Field("RH80", 10**3, np.int64),
    Field("RH85", 10**3, np.int64),
    Field("RH90", 10**3, np.int64),
    Field("RH95", 10**3, np.int64),
    Field("RH96", 10**3, np.int64),
    Field("RH97", 10**3, np.int64),
    Field("RH98", 10**3, np.int64),
    Field("RH99", 10**3, np.int64),
    Field("RH100", 10**3, np.int64),
    Field("AZIMUTH", 10**3, np.int64),
    Field("INCIDENT_ANGLE", 10**3, np.int64),
    Field("RANGE", 10**3, np.int64),
    Field("COMPLEXITY", 10**3, np.int64),
    Field("CHANNEL_ZT", None, np.uint8),
    Field("CHANNEL_ZG", None, np.uint8),
    Field("CHANNEL_RH", None, np.uint8),
]

"""Names of fields that contain longitude values. The values in these
fields will be shifted to the range [-180,180)."""
ILVIS2_LONGITUDE_FIELD_NAMES = ["CLON", "GLON", "HLON", "TLON"]


def _file_date(fn):
    """Return the datetime from the ILVIS2 filename."""
    return dt.datetime.strptime(fn[9:18], "%Y_%m%d")


def _shift_lon(lon):
    """Shift longitude values from [0,360] to [-180,180]"""
    if lon >= 180.0:
        return lon - 360.0
    return lon


def _add_utc_datetime(df, file_date):
    """Add a `utc_datetime` column to the DataFrame, with values
    calculated from the given date and the `TIME` values in the
    dataset (seconds of the day).
    """
    df["utc_datetime"] = pd.to_datetime(file_date)
    df["utc_datetime"] = df["utc_datetime"] + pd.to_timedelta(df["TIME"], unit="s")
    df["utc_datetime"] = pd.Series(
        np.datetime_as_string(df["utc_datetime"]).astype("|S")
    )

    return df


def _scale_and_convert(df, fields):
    """For any column in the list of Field named tuples, optionally scale
    the corresponding column in the DataFrame and convert the column
    type.
    """
    for name, scale_factor, dtype in fields:
        if scale_factor is not None:
            df.loc[:, name] *= scale_factor
        if dtype != df.dtypes[name]:
            df[name] = df[name].astype(dtype)

    return df


def _ilvis2_data(filename, file_date, fields):
    """Return an ILVIS2 file DataFrame, performing all necessary
    conversions / augmentation on the data.
    """
    field_names = [name for name, _, _ in fields]
    df = pd.read_csv(filename, delim_whitespace=True, comment="#", names=field_names)

    for col in ILVIS2_LONGITUDE_FIELD_NAMES:
        if col in df.columns:
            df[col] = df[col].apply(_shift_lon)

    df = _add_utc_datetime(df, file_date)

    df = _scale_and_convert(df, fields)

    return df


def ilvis2_filenames(year):
    """Use the default search path to find all ILVIS2 files for the
    specified year.

    Parameters
    ----------
    year
        The year for which to find matching files.

    Returns
    -------
    filenames
        The list of absolute filenames that match the given year.
    """
    filepaths = []
    for input_dir in SEARCH_PATHS:
        filepaths.extend(glob.glob(os.path.join(input_dir, f"{year}*/*.TXT")))

    return filepaths


def df_columns(df):
    """Return a list of column names corresponding to the data encoded
    and returned by the `row_values` function. This should be the
    database column names corresponding to the values returned by that
    function.

    Parameters
    ----------
    df
        The dataframe for which to generate the column names.

    Returns
    -------
    names
        The list of column names for the data frame.

    """
    if len(df.columns) == (len(ILVIS2_V104_FIELDS) + 1):
        return [
            "utc_datetime",
            "point",
            "lfid",
            "shotnumber",
            "time",
            "clon",
            "clat",
            "zc",
            "hlon",
            "hlat",
            "zh",
        ]
    elif len(df.columns) == (len(ILVIS2_V202b_FIELDS) + 1):
        return [
            "utc_datetime",
            "point",
            "lfid",
            "shotnumber",
            "time",
            "hlon",
            "hlat",
            "zh",
            "tlon",
            "tlat",
            "zt",
            "rh10",
            "rh15",
            "rh20",
            "rh25",
            "rh30",
            "rh35",
            "rh40",
            "rh45",
            "rh50",
            "rh55",
            "rh60",
            "rh65",
            "rh70",
            "rh75",
            "rh80",
            "rh85",
            "rh90",
            "rh95",
            "rh96",
            "rh97",
            "rh98",
            "rh99",
            "rh100",
            "azimuth",
            "incident_angle",
            "range",
            "complexity",
            "channel_zt",
            "channel_zg",
            "channel_rh",
        ]
    else:
        raise ValueError("Unknown row type: cannot convert to SQL str.")


def row_values(row):
    """Return a bytestring containing comma-delimited values for a given
    row in the dataset. This string can be used in a SQL statement to
    insert the data into a matching database table.

    Parameters
    ----------
    row
        The row tuple from a pandas.DataFrame obtained by calling
        ilvis2_data and augmented with `utc_datetime`.

    Returns
    -------
    row
        The row as a comma-delimited bytestring (`bytes`).
    """
    # The row will have one more value in it than the input file
    # because we add utc_datetime.
    if len(row) == (len(ILVIS2_V104_FIELDS) + 1):
        return b"%s,SRID=4326;POINT(%f %f %f),%d,%d,%d,%d,%d,%d,%d,%d,%d\n" % (
            row.utc_datetime,
            row.GLON,
            row.GLAT,
            row.ZG,
            row.LFID,
            row.SHOTNUMBER,
            row.TIME,
            row.CLON,
            row.CLAT,
            row.ZC,
            row.HLON,
            row.HLAT,
            row.ZH,
        )
    elif len(row) == (len(ILVIS2_V202b_FIELDS) + 1):
        return (
            b"%s,SRID=4326;POINT(%f %f %f),%d,%d,%d,%d,%d,%d,%d,"
            b"%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,"
            b"%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n"
        ) % (
            row.utc_datetime,
            row.GLON,
            row.GLAT,
            row.ZG,
            row.LFID,
            row.SHOTNUMBER,
            row.TIME,
            row.HLON,
            row.HLAT,
            row.ZH,
            row.TLON,
            row.TLAT,
            row.ZT,
            row.RH10,
            row.RH15,
            row.RH20,
            row.RH25,
            row.RH30,
            row.RH35,
            row.RH40,
            row.RH45,
            row.RH50,
            row.RH55,
            row.RH60,
            row.RH65,
            row.RH70,
            row.RH75,
            row.RH80,
            row.RH85,
            row.RH90,
            row.RH95,
            row.RH96,
            row.RH97,
            row.RH98,
            row.RH99,
            row.RH100,
            row.AZIMUTH,
            row.INCIDENT_ANGLE,
            row.RANGE,
            row.COMPLEXITY,
            row.CHANNEL_ZT,
            row.CHANNEL_ZG,
            row.CHANNEL_RH,
        )
    else:
        raise ValueError("Unknown row type: cannot convert to SQL str.")


def ilvis2_data(fn):
    """Return the ilvis2 data given a filename.

    Parameters
    ----------
    fn
        The filename (str) to read. This can be a file in the LVIS2
        v1.0.4 or v2.0.2b format.
        https://lvis.gsfc.nasa.gov/Data/Data_Structure/DataStructure_LDS104.html
        https://lvis.gsfc.nasa.gov/Data/Data_Structure/DataStructure_LDS202.html

    Returns
    -------
    data
        The ilvis2 (pandas.DataFrame) data.

    """
    m = re.search(r"_\D{2}(\d{4})_", fn)
    year = int(m.group(1))

    if year < 2017:
        the_fields = ILVIS2_V104_FIELDS
    else:
        the_fields = ILVIS2_V202b_FIELDS

    return _ilvis2_data(fn, _file_date(os.path.basename(fn)), the_fields)


@pa.check_types()
def ilvis2_data(filepath: Path) -> ILVIS2DataFrame: ...
