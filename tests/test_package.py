from __future__ import annotations

import importlib.metadata

import iceflow as m


def test_version():
    assert importlib.metadata.version("iceflow") == m.__version__
