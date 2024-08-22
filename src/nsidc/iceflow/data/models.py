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


IceflowDataFrame = DataFrame[CommonDataColumnsSchema]
ATM1BDataFrame = DataFrame[ATM1BSchema]

DatasetShortName = Literal["ILATM1B"]


class Dataset(pydantic.BaseModel):
    short_name: DatasetShortName
    version: str


class ATM1BDataset(Dataset):
    short_name: DatasetShortName = "ILATM1B"


class BoundingBox(pydantic.BaseModel):
    lower_left_lon: float
    lower_left_lat: float
    upper_right_lon: float
    upper_right_lat: float


class DatasetSearchParameters(pydantic.BaseModel):
    dataset: Dataset
    bounding_box: BoundingBox
    temporal: tuple[dt.datetime | dt.date, dt.datetime | dt.date]
