"""End-to-End test for the typical iceflow pipeline.

* Searches for small sample of data
* Downloads small sample of data
* Performs ITRF transformation

This serves as prototype for planned Jupyter Notebook-based tutorial featuring
this library.
"""

from __future__ import annotations

import pandas as pd

from iceflow.data.atm1b import atm1b_data
from iceflow.data.fetch import search_and_download
from iceflow.data.models import IceflowDataFrame
from iceflow.itrf.converter import transform_itrf


def test_e2e(tmp_path):
    # TODO: handle different versions of datasets.
    # ILATM1B has two versions. v1 is in
    # qfit format and covers 2009-03-31 through 2012-11-08. v2 is in hdf5 format
    # and covers 2013-03-20 through 2019-11-20. We want to support both. Without
    # specifying the version, earthaccess returns results for both versions.
    # This might be OK, but ILVIS2 has a similar situation, but we don't
    # (currently) have code to support it.
    results2009 = search_and_download(
        short_name="ILATM1B",
        version="1",
        output_dir=tmp_path,
        bounding_box=(-103.125559, -75.180563, -102.677327, -74.798063),
        temporal=("2009-11-01", "2009-12-01"),
    )

    results2012 = search_and_download(
        short_name="ILATM1B",
        version="1",
        output_dir=tmp_path,
        bounding_box=(-103.125559, -75.180563, -102.677327, -74.798063),
        temporal=("2012-11-01", "2012-12-01"),
    )

    # 3 results total; ~62M total size
    results = [*results2009, *results2012]
    all_dfs = []
    for result in results:
        data_df = atm1b_data(result)
        all_dfs.append(data_df)

    # This df contains data w/ two ITRFs: ITRF2005 and ITRF2008.
    complete_df = pd.concat(all_dfs)
    complete_df = IceflowDataFrame(complete_df)

    transformed = transform_itrf(
        data=complete_df,
        target_itrf="ITRF2008",
    )

    assert transformed is not None
