from __future__ import annotations

import datetime as dt
import re
from collections import namedtuple
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
import pandera as pa

from nsidc.iceflow.data.models import ILVIS2DataFrame

ILVIS2_COORDINATE_SETS = Literal["low_mode", "high_mode", "centroid", "highest_signal"]
ILVIS2_COORDINATE_SET_MAPPING: dict[ILVIS2_COORDINATE_SETS, dict[str, str]] = {
    # The center of the lowest detected mode within the waveform. Available in
    # both v1 and v2.
    "low_mode": {
        "latitude": "GLAT",
        "longitude": "GLON",
        "elevation": "ZG",
    },
    # The center of the highest detected mode within the waveform. Available in
    # both v1 and v2.
    "high_mode": {
        "latitude": "HLAT",
        "longitude": "HLON",
        "elevation": "ZH",
    },
    # Centroid of the corresponding LVIS Level-1B waveform. v1 only.
    "centroid": {
        "latitude": "CLAT",
        "longitude": "CLON",
        "elevation": "ZC",
    },
    # Highest detected signal. v2 only.
    "highest_signal": {
        "latitude": "TLAT",
        "longitude": "TLON",
        "elevation": "ZT",
    },
}
# In the valkyrie service that this code is based on, only the low_mode was
# exposed to users. This default replicates that behavior.
ILVIS2_DEFAULT_COORDINATE_SET: ILVIS2_COORDINATE_SETS = "low_mode"

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


def _file_date(filename: str) -> dt.date:
    """Return the datetime from the ILVIS2 filename."""
    return dt.datetime.strptime(filename[9:18], "%Y_%m%d").date()


def _shift_lon(lon):
    """Shift longitude values from [0,360] to [-180,180]"""
    if lon >= 180.0:
        return lon - 360.0
    return lon


def _add_utc_datetime(df: pd.DataFrame, file_date) -> pd.DataFrame:
    """Add a `utc_datetime` column to the DataFrame, with values
    calculated from the given date and the `TIME` values in the
    dataset (seconds of the day).
    """
    df["utc_datetime"] = pd.to_datetime(file_date)
    df["utc_datetime"] = df["utc_datetime"] + pd.to_timedelta(df["TIME"], unit="s")

    return df


def _scale_and_convert(df: pd.DataFrame, fields) -> pd.DataFrame:
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


def _ilvis2_data(filepath: Path, file_date: dt.date, fields) -> pd.DataFrame:
    """Return an ILVIS2 file DataFrame, performing all necessary
    conversions / augmentation on the data.
    """
    field_names = [name for name, _, _ in fields]
    df = pd.read_csv(filepath, sep=r"\s+", comment="#", names=field_names)

    for col in ILVIS2_LONGITUDE_FIELD_NAMES:
        if col in df.columns:
            df[col] = df[col].apply(_shift_lon)

    df = _add_utc_datetime(df, file_date)

    df = _scale_and_convert(df, fields)

    return df


@pa.check_types()
def ilvis2_data(
    filepath: Path,
    coordinate_set: ILVIS2_COORDINATE_SETS = ILVIS2_DEFAULT_COORDINATE_SET,
) -> ILVIS2DataFrame:
    """Return the ilvis2 data given a filepath.

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
    filename = filepath.name
    match = re.search(r"_\D{2}(\d{4})_", filename)
    if not match:
        err = f"Failed to recognize {filename} as ILVIS2 data."
        raise RuntimeError(err)

    year = int(match.group(1))

    if year < 2017:
        # This corresponds to ILVIS v1
        dataset = "ILVIS2v1"
        the_fields = ILVIS2_V104_FIELDS
        # The user guide indicates ILVIS2 v1 data uses ITRF2000 as a reference frame:
        # https://nsidc.org/sites/default/files/documents/user-guide/ilvis2-v001-userguide.pdf
        itrf_str = "ITRF2000"
        # Ensure that the highest_signal coordinate set has not been selected.
        if coordinate_set == "highest_signal":
            raise ValueError(
                "ILVIS coordinate set 'highest_signal' is only available in v2 data."
            )
    else:
        # This corresponds to ILVIS v2
        dataset = "ILVIS2v2"
        the_fields = ILVIS2_V202b_FIELDS
        # The user guide indicates ILVIS2 v1 data uses ITRF2008 as a reference frame:
        # https://nsidc.org/sites/default/files/documents/user-guide/ilvis2-v002-userguide.pdf
        itrf_str = "ITRF2008"
        # Ensure that the centroid coordinate set has not been selected.
        if coordinate_set == "centroid":
            raise ValueError(
                "ILVIS coordinate set 'centroid' is only available in v1 data."
            )

    file_date = _file_date(filename)

    data = _ilvis2_data(filepath, file_date, the_fields)
    data["ITRF"] = itrf_str
    data["dataset"] = dataset

    coordinate_fields = ILVIS2_COORDINATE_SET_MAPPING[coordinate_set]
    data["latitude"] = data[coordinate_fields["latitude"]]
    data["longitude"] = data[coordinate_fields["longitude"]]
    data["elevation"] = data[coordinate_fields["elevation"]]

    data = data.set_index("utc_datetime")

    return ILVIS2DataFrame(data)
