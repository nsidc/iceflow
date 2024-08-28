from __future__ import annotations

import datetime as dt

import pytest

from nsidc.iceflow.data.atm1b import _qfit_itrf_from_date


@pytest.mark.parametrize(
    ("granule_datetime", "expected_itrf"),
    [
        (dt.date(1994, 7, 1), "ITRF93"),
        (dt.date(1997, 5, 1), "ITRF94"),
        (dt.date(1998, 9, 1), "ITRF96"),
        (dt.date(2000, 12, 1), "ITRF97"),
        (dt.date(2002, 1, 1), "ITRF2000"),
        (dt.date(2002, 11, 22), "ITRF97"),
        (dt.date(2002, 12, 14), "ITRF97"),
        (dt.date(2007, 5, 11), "ITRF2000"),
        (dt.date(2010, 1, 1), "ITRF2005"),
        (dt.date(2015, 1, 1), "ITRF2008"),
    ],
)
def test_valid_dates(granule_datetime, expected_itrf):
    assert _qfit_itrf_from_date(granule_datetime) == expected_itrf


@pytest.mark.parametrize(
    "granule_datetime",
    [
        dt.date(1990, 1, 1),
        dt.date(2020, 1, 1),
    ],
)
def test_invalid_dates(granule_datetime):
    with pytest.raises(RuntimeError):
        _qfit_itrf_from_date(granule_datetime)
