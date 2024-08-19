from __future__ import annotations

import datetime as dt
from collections.abc import Sequence
from typing import Literal

import pandera as pa
import pydantic
from pandera.typing import DataFrame, Index, Series

from iceflow.itrf import ITRF_REGEX


class CommonDataColumnsSchema(pa.DataFrameModel):
    utc_datetime: Index[pa.dtypes.DateTime] = pa.Field(check_name=True)
    ITRF: Series[str] = pa.Field(str_matches=ITRF_REGEX.pattern)
    latitude: Series[pa.dtypes.Float] = pa.Field(coerce=True)
    longitude: Series[pa.dtypes.Float] = pa.Field(coerce=True)
    elevation: Series[pa.dtypes.Float] = pa.Field(coerce=True)


class ATM1BSchema(CommonDataColumnsSchema):
    # Data fields unique to ATM1B data.
    rel_time: Series[pa.dtypes.Int32]
    xmt_sigstr: Series[pa.dtypes.Int32]
    rcv_sigstr: Series[pa.dtypes.Int32]
    azimuth: Series[pa.dtypes.Int32]
    pitch: Series[pa.dtypes.Int32]
    roll: Series[pa.dtypes.Int32]
    gps_pdop: Series[pa.dtypes.Int32]
    gps_time: Series[pa.dtypes.Int32]
    passive_signal: Series[pa.dtypes.Int32]
    passive_footprint_latitude: Series[pa.dtypes.Int32]
    passive_footprint_longitude: Series[pa.dtypes.Int32]
    passive_footprint_synthesized_elevation: Series[pa.dtypes.Int32]


IceflowDataFrame = DataFrame[CommonDataColumnsSchema]
ATM1BDataFrame = DataFrame[ATM1BSchema]

DatasetShortName = Literal["ILATM1B"]


class Dataset(pydantic.BaseModel):
    short_name: DatasetShortName
    version: str


class ATM1BDataset(Dataset):
    short_name: DatasetShortName = "ILATM1B"


class DatasetSearchParameters(pydantic.BaseModel):
    dataset: Dataset
    bounding_box: Sequence[float]
    temporal: tuple[dt.datetime | dt.date, dt.datetime | dt.date]
