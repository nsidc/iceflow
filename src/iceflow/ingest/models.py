from __future__ import annotations

from typing import TypeVar

import pandas as pd
import pandera as pa
from pandera.typing import Index, Series

from iceflow.itrf import SUPPORTED_ITRFS

TDataFrame_co = TypeVar("TDataFrame_co", covariant=True)


class IceFlowDataSchema(pa.DataFrameModel):
    utc_datetime: Index[pa.dtypes.DateTime] = pa.Field(check_name=True)
    ITRF: Series[str] = pa.Field(isin=SUPPORTED_ITRFS)
    latitude: Series[pa.dtypes.Float] = pa.Field(coerce=True)
    longitude: Series[pa.dtypes.Float] = pa.Field(coerce=True)
    elevation: Series[pa.dtypes.Float] = pa.Field(coerce=True)


class IceFlowData(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Validate the data w/ pandera
        IceFlowDataSchema.validate(self)
