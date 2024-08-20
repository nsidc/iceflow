from __future__ import annotations

from nsidc import iceflow


def test_version():
    assert iceflow.__version__ is not None
