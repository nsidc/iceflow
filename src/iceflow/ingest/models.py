from __future__ import annotations

from typing import Generic, TypeVar

import pandera as pa
from pandera.typing import DataFrame, Index, Series

from iceflow.itrf import SUPPORTED_ITRFS

TDataFrame_co = TypeVar("TDataFrame_co", covariant=True)


# Workaround for inheritance issue. See:
# https://github.com/unionai-oss/pandera/issues/1170
class DataFrame_co(DataFrame, Generic[TDataFrame_co]):  # type: ignore[type-arg]
    pass


class CommonDataColumnsSchema(pa.DataFrameModel):
    utc_datetime: Index[pa.dtypes.DateTime] = pa.Field(check_name=True)
    ITRF: Series[str] = pa.Field(isin=SUPPORTED_ITRFS)
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


IceflowDataFrame = DataFrame_co[CommonDataColumnsSchema]
ATM1BDataFrame = DataFrame_co[ATM1BSchema]
