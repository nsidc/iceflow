from __future__ import annotations

import re

ITRF_REGEX = re.compile(r"^ITRF\d{2}(\d{2})?$")


def check_itrf(itrf_str: str) -> bool:
    """Check if the given string is  a valid ITRF.

    Based on a regex match. ITRF strings are conventionally "ITRF" followed by
    the 2-digit or 4-digit year (e.g., "ITRF93" or "ITRF2008").

    ITRFs prior to the 2000s conventionally used a 2-digit year (e.g.,
    "ITRF88").

    ITRF2020 is recognized as "ITRF20".
    """

    match = ITRF_REGEX.match(itrf_str)

    return match is not None
