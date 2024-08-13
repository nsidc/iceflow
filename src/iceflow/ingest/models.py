from __future__ import annotations

import pandera as pa
from pandera.typing import Index, Series


class commonDataColumns(pa.DataFrameModel):
    utc_datetime: Index[pa.dtypes.DateTime] = pa.Field(check_name=True)
    # TODO: can/should this be typed as a Literal w/ specific ITRF strings?
    ITRF: Series[str]
    latitude: Series[pa.dtypes.Float] = pa.Field(coerce=True)
    longitude: Series[pa.dtypes.Float] = pa.Field(coerce=True)
    elevation: Series[pa.dtypes.Float] = pa.Field(coerce=True)
