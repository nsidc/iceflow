from __future__ import annotations

from typing import Generic, TypeVar

import pandera as pa
from pandera.typing import DataFrame, Index, Series

from iceflow.itrf import SUPPORTED_ITRFS

TDataFrame_co = TypeVar("TDataFrame_co", covariant=True)


# Workaround for inheritance issue. See:
# https://github.com/unionai-oss/pandera/issues/1170
class IceFlowDataFrame(DataFrame, Generic[TDataFrame_co]):  # type: ignore[type-arg]
    pass


class commonDataColumns(pa.DataFrameModel):
    utc_datetime: Index[pa.dtypes.DateTime] = pa.Field(check_name=True)
    ITRF: Series[str] = pa.Field(isin=SUPPORTED_ITRFS)
    latitude: Series[pa.dtypes.Float] = pa.Field(coerce=True)
    longitude: Series[pa.dtypes.Float] = pa.Field(coerce=True)
    elevation: Series[pa.dtypes.Float] = pa.Field(coerce=True)
