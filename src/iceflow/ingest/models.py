from __future__ import annotations

import pandera as pa
from pandera.typing import Index, Series

from iceflow.itrf import SUPPORTED_ITRFS


class commonDataColumns(pa.DataFrameModel):
    utc_datetime: Index[pa.dtypes.DateTime] = pa.Field(check_name=True)
    ITRF: Series[str] = pa.Field(isin=SUPPORTED_ITRFS)
    latitude: Series[pa.dtypes.Float] = pa.Field(coerce=True)
    longitude: Series[pa.dtypes.Float] = pa.Field(coerce=True)
    elevation: Series[pa.dtypes.Float] = pa.Field(coerce=True)
