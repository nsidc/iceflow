from __future__ import annotations

import pandera as pa
from pandera.typing import Index, Series

# ITRF strings recognized by proj, which is used in the ITRF transformation
# code.
# TODO: make this a constant in a different module?
ITRF_LIST = [
    "ITRF93",
    "ITRF94",
    "ITRF96",
    "ITRF97",
    "ITRF2000",
    "ITRF2005",
    "ITRF2008",
]


class commonDataColumns(pa.DataFrameModel):
    utc_datetime: Index[pa.dtypes.DateTime] = pa.Field(check_name=True)
    ITRF: Series[str] = pa.Field(isin=ITRF_LIST)
    latitude: Series[pa.dtypes.Float] = pa.Field(coerce=True)
    longitude: Series[pa.dtypes.Float] = pa.Field(coerce=True)
    elevation: Series[pa.dtypes.Float] = pa.Field(coerce=True)
