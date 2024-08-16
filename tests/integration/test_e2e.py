"""End-to-End test for the typical iceflow pipeline.

* Searches for small sample of data
* Downloads small sample of data
* Performs ITRF transformation

This serves as prototype for planned Jupyter Notebook-based tutorial featuring
this library.
"""

from __future__ import annotations

import pandas as pd

from iceflow.api import fetch_iceflow_df
from iceflow.data.models import IceflowDataFrame
from iceflow.itrf import ITRF


def test_e2e(tmp_path):
    target_itrf: ITRF = "ITRF2008"
    results2009 = fetch_iceflow_df(
        dataset_short_name="ILATM1B",
        dataset_version="1",
        output_dir=tmp_path,
        bounding_box=(-103.125559, -75.180563, -102.677327, -74.798063),
        temporal=("2009-11-01", "2009-12-01"),
        output_itrf=target_itrf,
    )

    results2012 = fetch_iceflow_df(
        dataset_short_name="ILATM1B",
        dataset_version="1",
        output_dir=tmp_path,
        bounding_box=(-103.125559, -75.180563, -102.677327, -74.798063),
        temporal=("2012-11-01", "2012-12-01"),
        output_itrf=target_itrf,
    )

    complete_df = IceflowDataFrame(pd.concat([results2009, results2012]))
    assert (complete_df.ITRF.unique() == target_itrf).all()
