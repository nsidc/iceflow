from __future__ import annotations

from typing import Literal, get_args

# ITRF strings recognized by proj, which is used in the ITRF transformation
# code.
ITRF = Literal[
    "ITRF93",
    "ITRF94",
    "ITRF96",
    "ITRF97",
    "ITRF2000",
    "ITRF2005",
    "ITRF2008",
    "ITRF2014",
    "ITRF2020",
]

SUPPORTED_ITRFS: list[ITRF] = list(get_args(ITRF))
