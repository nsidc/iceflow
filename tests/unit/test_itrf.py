from __future__ import annotations

from nsidc.iceflow.itrf import check_itrf


def test_check_itrf():
    # These should return False
    assert not check_itrf("Not an ITRF string")
    assert not check_itrf("ITRF")

    # These should return True
    assert check_itrf("ITRF2008")
    assert check_itrf("ITRF88")
