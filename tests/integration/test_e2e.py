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
    target_itrf = "ITRF2008"
    common_bounding_box = BoundingBox(
        lower_left_lon=-103.125559,
        lower_left_lat=-75.180563,
        upper_right_lon=-102.677327,
        upper_right_lat=-74.798063,
    )
    atm1b_v1_dataset = ATM1BDataset(version="1")

    results2009 = fetch_iceflow_df(
        dataset_search_params=DatasetSearchParameters(
            dataset=atm1b_v1_dataset,
            bounding_box=common_bounding_box,
            temporal=(dt.date(2009, 11, 1), dt.date(2009, 12, 1)),
        ),
        output_dir=tmp_path,
        output_itrf=target_itrf,
    )

    results2012 = fetch_iceflow_df(
        dataset_search_params=DatasetSearchParameters(
            dataset=atm1b_v1_dataset,
            bounding_box=common_bounding_box,
            temporal=(dt.date(2012, 11, 1), dt.date(2012, 12, 1)),
        ),
        output_dir=tmp_path,
        output_itrf=target_itrf,
    )

    complete_df = IceflowDataFrame(pd.concat([results2009, results2012]))
    assert (complete_df.ITRF.unique() == target_itrf).all()
