from __future__ import annotations

from iceflow.itrf import check_itrf


def test_check_itrf():
    assert check_itrf("Not an ITRF string") is False
    assert check_itrf("ITRF") is False

    # These should pass.
    assert check_itrf("ITRF2008") is True
    assert check_itrf("ITRF88") is True
