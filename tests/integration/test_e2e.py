"""End-to-End test for the typical iceflow pipeline.

* Searches for small sample of data
* Downloads small sample of data
* Performs ITRF transformation

This serves as prototype for planned Jupyter Notebook-based tutorial featuring
this library.
"""

from __future__ import annotations

import datetime as dt

import pandas as pd

from nsidc.iceflow.api import fetch_iceflow_df
from nsidc.iceflow.data.models import (
    ATM1BDataset,
    BoundingBox,
    DatasetSearchParameters,
    IceflowDataFrame,
)


def test_e2e(tmp_path):
    target_itrf = "ITRF2014"
    common_bounding_box = BoundingBox(
        lower_left_lon=-103.125559,
        lower_left_lat=-75.180563,
        upper_right_lon=-102.677327,
        upper_right_lat=-74.798063,
    )

    results_ilatm1b_v1_2009 = fetch_iceflow_df(
        dataset_search_params=DatasetSearchParameters(
            dataset=ATM1BDataset(version="1"),
            bounding_box=common_bounding_box,
            temporal=(dt.date(2009, 11, 1), dt.date(2009, 12, 1)),
        ),
        output_dir=tmp_path,
        output_itrf=target_itrf,
    )

    results_ilatm1b_v2_2014 = fetch_iceflow_df(
        dataset_search_params=DatasetSearchParameters(
            dataset=ATM1BDataset(version="2"),
            bounding_box=common_bounding_box,
            temporal=(dt.date(2014, 11, 1), dt.date(2014, 12, 1)),
        ),
        output_dir=tmp_path,
        output_itrf=target_itrf,
    )

    complete_df = IceflowDataFrame(
        pd.concat([results_ilatm1b_v1_2009, results_ilatm1b_v2_2014])
    )

    assert (complete_df.ITRF.unique() == target_itrf).all()
