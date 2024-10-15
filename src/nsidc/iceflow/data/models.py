from __future__ import annotations

import datetime as dt
from typing import Literal

import pandera as pa
import pydantic
from pandera.typing import DataFrame, Index, Series

from nsidc.iceflow.itrf import ITRF_REGEX


class CommonDataColumnsSchema(pa.DataFrameModel):
    utc_datetime: Index[pa.dtypes.DateTime] = pa.Field(check_name=True)
    ITRF: Series[str] = pa.Field(str_matches=ITRF_REGEX.pattern)
    latitude: Series[float] = pa.Field(coerce=True)
    longitude: Series[float] = pa.Field(coerce=True)
    elevation: Series[float] = pa.Field(coerce=True)


class ATM1BSchema(CommonDataColumnsSchema):
    # Data fields unique to ATM1B data.
    rel_time: Series[float] = pa.Field(nullable=True, coerce=True)
    xmt_sigstr: Series[float] = pa.Field(nullable=True, coerce=True)
    rcv_sigstr: Series[float] = pa.Field(nullable=True, coerce=True)
    azimuth: Series[float] = pa.Field(nullable=True, coerce=True)
    pitch: Series[float] = pa.Field(nullable=True, coerce=True)
    roll: Series[float] = pa.Field(nullable=True, coerce=True)
    gps_pdop: Series[float] = pa.Field(nullable=True, coerce=True)
    gps_time: Series[float] = pa.Field(nullable=True, coerce=True)
    passive_signal: Series[float] = pa.Field(nullable=True, coerce=True)
    passive_footprint_latitude: Series[float] = pa.Field(nullable=True, coerce=True)
    passive_footprint_longitude: Series[float] = pa.Field(nullable=True, coerce=True)
    passive_footprint_synthesized_elevation: Series[float] = pa.Field(
        nullable=True, coerce=True
    )
    pulse_width: Series[float] = pa.Field(nullable=True, coerce=True)


# Note/TODO: the ILVIS2 data contain multiple sets of lat/lon/elev. The common
# schema assumes one set of lat/lon/elev which is used for the ITRF
# transformation code.
class ILVIS2Schema(CommonDataColumnsSchema):
    # Common columns
    LFID: Series[float] = pa.Field(nullable=True, coerce=True)
    SHOTNUMBER: Series[float] = pa.Field(nullable=True, coerce=True)
    TIME: Series[float] = pa.Field(nullable=True, coerce=True)
    ZG: Series[float] = pa.Field(nullable=True, coerce=True)
    GLAT: Series[float] = pa.Field(nullable=True, coerce=True)
    GLON: Series[float] = pa.Field(nullable=True, coerce=True)
    HLAT: Series[float] = pa.Field(nullable=True, coerce=True)
    HLON: Series[float] = pa.Field(nullable=True, coerce=True)
    ZH: Series[float] = pa.Field(nullable=True, coerce=True)

    # V104-specific
    CLAT: Series[float] = pa.Field(nullable=True, coerce=True)
    CLON: Series[float] = pa.Field(nullable=True, coerce=True)
    ZC: Series[float] = pa.Field(nullable=True, coerce=True)

    # V202B-specific
    AZIMUTH: Series[float] = pa.Field(nullable=True, coerce=True)
    CHANNEL_RH: Series[float] = pa.Field(nullable=True, coerce=True)
    CHANNEL_ZG: Series[float] = pa.Field(nullable=True, coerce=True)
    CHANNEL_ZT: Series[float] = pa.Field(nullable=True, coerce=True)
    COMPLEXITY: Series[float] = pa.Field(nullable=True, coerce=True)
    INCIDENT_ANGLE: Series[float] = pa.Field(nullable=True, coerce=True)
    RANGE: Series[float] = pa.Field(nullable=True, coerce=True)
    RH10: Series[float] = pa.Field(nullable=True, coerce=True)
    RH15: Series[float] = pa.Field(nullable=True, coerce=True)
    RH20: Series[float] = pa.Field(nullable=True, coerce=True)
    RH25: Series[float] = pa.Field(nullable=True, coerce=True)
    RH30: Series[float] = pa.Field(nullable=True, coerce=True)
    RH35: Series[float] = pa.Field(nullable=True, coerce=True)
    RH40: Series[float] = pa.Field(nullable=True, coerce=True)
    RH45: Series[float] = pa.Field(nullable=True, coerce=True)
    RH50: Series[float] = pa.Field(nullable=True, coerce=True)
    RH55: Series[float] = pa.Field(nullable=True, coerce=True)
    RH60: Series[float] = pa.Field(nullable=True, coerce=True)
    RH65: Series[float] = pa.Field(nullable=True, coerce=True)
    RH70: Series[float] = pa.Field(nullable=True, coerce=True)
    RH75: Series[float] = pa.Field(nullable=True, coerce=True)
    RH80: Series[float] = pa.Field(nullable=True, coerce=True)
    RH85: Series[float] = pa.Field(nullable=True, coerce=True)
    RH90: Series[float] = pa.Field(nullable=True, coerce=True)
    RH95: Series[float] = pa.Field(nullable=True, coerce=True)
    RH96: Series[float] = pa.Field(nullable=True, coerce=True)
    RH97: Series[float] = pa.Field(nullable=True, coerce=True)
    RH98: Series[float] = pa.Field(nullable=True, coerce=True)
    RH99: Series[float] = pa.Field(nullable=True, coerce=True)
    RH100: Series[float] = pa.Field(nullable=True, coerce=True)
    TLAT: Series[float] = pa.Field(nullable=True, coerce=True)
    TLON: Series[float] = pa.Field(nullable=True, coerce=True)
    ZT: Series[float] = pa.Field(nullable=True, coerce=True)

    class Config:
        # This ensures all columns are present, regardless of the date. Granules
        # before 2017 use the V104 fields and anything after uses the v202b
        # fields. The data type for all values must be `float` because the null
        # value is `np.nan` - a float.
        add_missing_columns = True


IceflowDataFrame = DataFrame[CommonDataColumnsSchema]
ATM1BDataFrame = DataFrame[ATM1BSchema]
ILVIS2DataFrame = DataFrame[ILVIS2Schema]

ATM1BShortName = Literal["ILATM1B", "BLATM1B"]
DatasetShortName = ATM1BShortName | Literal["ILVIS2"]


class Dataset(pydantic.BaseModel):
    short_name: DatasetShortName
    version: str


class ATM1BDataset(Dataset):
    short_name: ATM1BShortName


class ILATM1BDataset(ATM1BDataset):
    short_name: ATM1BShortName = "ILATM1B"
    version: Literal["1", "2"]


class BLATM1BDataset(ATM1BDataset):
    short_name: ATM1BShortName = "BLATM1B"
    # There is only 1 version of BLATM1B
    version: Literal["1"] = "1"


class ILVIS2Dataset(Dataset):
    short_name: DatasetShortName = "ILVIS2"
    version: Literal["1"] = "1"


class BoundingBox(pydantic.BaseModel):
    lower_left_lon: float
    lower_left_lat: float
    upper_right_lon: float
    upper_right_lat: float


class DatasetSearchParameters(pydantic.BaseModel):
    dataset: Dataset
    bounding_box: BoundingBox
    temporal: tuple[dt.datetime | dt.date, dt.datetime | dt.date]
