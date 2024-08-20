from __future__ import annotations

import gps_timemachine


def test_gps_timemachine_import():
    assert gps_timemachine is not None


def test_import_package():
    from nsidc import iceflow

    assert iceflow is not None
