from __future__ import annotations

from typing import Literal, get_args

# ITRF strings recognized by proj, which is used in the ITRF transformation
# code.
# TODO: pyproj does recognize e.g., `ITRF1993` to be an alias of
# `ITRF93`. Instead of being a hard-coded list, we could create a custom
# validator for pandera that ensures the value is e.g., `ITRF\d{4}`, and then
# the itrf transformation code could handle unrecognized ITRFs.
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
