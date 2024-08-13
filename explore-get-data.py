from __future__ import annotations

from pathlib import Path
from typing import Literal

import earthaccess
import pandas as pd

from iceflow.ingest.atm1b import atm1b_data
from iceflow.itrf.converter import transform_itrf

ShortName = Literal["ILATM1B"]


def search_and_download(
    *,
    version: str,
    short_name: ShortName,
    bounding_box,
    temporal: tuple[str, str],
) -> list[Path]:
    earthaccess.login()

    results = earthaccess.search_data(
        short_name=short_name,
        version=version,
        bounding_box=bounding_box,
        temporal=temporal,
    )

    downloaded_files = earthaccess.download(results, f"./data/{short_name}")
    downloaded_filepaths = [Path(filepath_str) for filepath_str in downloaded_files]

    return downloaded_filepaths


if __name__ == "__main__":
    # TODO: handle different versions of datasets.
    # ILATM1B has two versions. v1 is in
    # qfit format and covers 2009-03-31 through 2012-11-08. v2 is in hdf5 format
    # and covers 2013-03-20 through 2019-11-20. We want to support both. Without
    # specifying the version, earthaccess returns results for both versions.
    # This might be OK, but ILVIS2 has a similar situation, but we don't
    # (currently) have code to support it.
    results = search_and_download(
        short_name="ILATM1B",
        version="1",
        bounding_box=(-103.125559, -75.180563, -102.677327, -74.798063),
        temporal=("1993-01-01", "2020-01-01"),
    )

    all_dfs = []
    for result in results:
        data_df = atm1b_data(result)
        all_dfs.append(data_df)
    # This df contains data  w/ two ITRFs
    complete_df = pd.concat(all_dfs)

    transformed = transform_itrf(
        data=complete_df,
        target_itrf="ITRF2008",
    )
