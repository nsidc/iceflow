"""End-to-End test for the typical iceflow pipeline.

* Searches for small sample of data
* Downloads small sample of data
* Performs ITRF transformation

This serves as prototype for planned Jupyter Notebook-based tutorial featuring
this library.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import dask.dataframe as dd
import pandas as pd

from nsidc.iceflow import (
    download_iceflow_results,
    find_iceflow_data,
    make_iceflow_parquet,
)
from nsidc.iceflow.api import fetch_iceflow_df
from nsidc.iceflow.data.models import (
    BLATM1BDataset,
    BoundingBox,
    DatasetSearchParameters,
    GLAH06Dataset,
    IceflowDataFrame,
    ILATM1BDataset,
    ILVIS2Dataset,
)


def test_atm1b_ilatm1b(tmp_path):
    target_itrf = "ITRF2014"
    common_bounding_box = BoundingBox(
        lower_left_lon=-103.125559,
        lower_left_lat=-75.180563,
        upper_right_lon=-102.677327,
        upper_right_lat=-74.798063,
    )

    # Native ITRF is ITRF2005
    results_ilatm1b_v1_2009 = fetch_iceflow_df(
        dataset_search_params=DatasetSearchParameters(
            datasets=[ILATM1BDataset(version="1")],
            bounding_box=common_bounding_box,
            temporal=(dt.date(2009, 11, 1), dt.date(2009, 12, 1)),
        ),
        output_dir=tmp_path,
        output_itrf=target_itrf,
    )

    # Native ITRF is ITRF2008
    results_ilatm1b_v2_2014 = fetch_iceflow_df(
        dataset_search_params=DatasetSearchParameters(
            datasets=[ILATM1BDataset(version="2")],
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


def test_atm1b_blatm1b(tmp_path):
    common_bounding_box = BoundingBox(
        lower_left_lon=-120.0,
        lower_left_lat=-75.1,
        upper_right_lon=-92.0,
        upper_right_lat=-65.0,
    )

    results_blamt1b_v2_2014 = fetch_iceflow_df(
        dataset_search_params=DatasetSearchParameters(
            datasets=[BLATM1BDataset()],
            bounding_box=common_bounding_box,
            temporal=(dt.date(2002, 11, 27), dt.date(2002, 11, 28)),
        ),
        output_dir=tmp_path,
    )

    assert (results_blamt1b_v2_2014.ITRF == "ITRF2000").all()


def test_ivlis2(tmp_path):
    results_v1 = fetch_iceflow_df(
        dataset_search_params=DatasetSearchParameters(
            datasets=[ILVIS2Dataset(version="1")],
            bounding_box=BoundingBox(
                lower_left_lon=-120.0,
                lower_left_lat=-80.0,
                upper_right_lon=-90.0,
                upper_right_lat=-65.0,
            ),
            temporal=(dt.datetime(2009, 10, 25, 15), dt.datetime(2009, 10, 25, 17)),
        ),
        output_dir=tmp_path,
    )

    assert (results_v1.ITRF == "ITRF2000").all()

    results_v2 = fetch_iceflow_df(
        dataset_search_params=DatasetSearchParameters(
            datasets=[ILVIS2Dataset(version="2")],
            bounding_box=BoundingBox(
                lower_left_lon=-180,
                lower_left_lat=60.0,
                upper_right_lon=180,
                upper_right_lat=90,
            ),
            temporal=(dt.datetime(2017, 8, 25, 0), dt.datetime(2017, 8, 25, 14, 30)),
        ),
        output_dir=tmp_path,
    )

    assert (results_v2.ITRF == "ITRF2008").all()

    # test that v1 and 2 can be concatenated
    complete_df = IceflowDataFrame(pd.concat([results_v1, results_v2]))

    assert complete_df is not None


def test_glah06(tmp_path):
    common_bounding_box = BoundingBox(
        lower_left_lon=-180,
        lower_left_lat=-90,
        upper_right_lon=180,
        upper_right_lat=90,
    )

    results = fetch_iceflow_df(
        dataset_search_params=DatasetSearchParameters(
            datasets=[GLAH06Dataset()],
            bounding_box=common_bounding_box,
            temporal=(
                dt.datetime(2003, 2, 20, 22, 25),
                dt.datetime(2003, 2, 20, 22, 25, 38),
            ),
        ),
        output_dir=tmp_path,
    )

    assert (results.ITRF == "ITRF2008").all()


def _create_iceflow_parquet(
    *,
    dataset_search_params: DatasetSearchParameters,
    output_dir: Path,
    target_itrf: str,
    overwrite: bool = False,
    target_epoch: str | None = None,
) -> Path:
    """Create a parquet dataset containing the lat/lon/elev data matching the dataset search params.

    This function creates a parquet dataset that can be easily used alongside dask,
    containing lat/lon/elev data.

    Note: this function writes a single `iceflow.parquet` to the output
    dir. This code does not currently support updates to the parquet after being
    written. This is intended to help facilitate analysis of a specific area
    over time. If an existing `iceflow.parquet` exists and the user wants to
    create a new `iceflow.parquet` for a different area or timespan, they will
    need to move/remove the existing `iceflow.parquet` first (e.g., with the
    `overwrite=True` kwarg).
    """
    iceflow_search_results = find_iceflow_data(
        dataset_search_params=dataset_search_params,
    )

    download_iceflow_results(
        iceflow_search_results=iceflow_search_results,
        output_dir=output_dir,
    )

    parquet_path = make_iceflow_parquet(
        data_dir=output_dir,
        target_itrf=target_itrf,
        overwrite=overwrite,
        target_epoch=target_epoch,
    )

    return parquet_path


def test_create_iceflow_parquet(tmp_path):
    target_itrf = "ITRF2014"
    common_bounding_box = BoundingBox(
        lower_left_lon=-49.149,
        lower_left_lat=69.186,
        upper_right_lon=-48.949,
        upper_right_lat=69.238,
    )

    # This should finds 4 results for ILATM1B v1 and 3 results for v2.
    parquet_path = _create_iceflow_parquet(
        dataset_search_params=DatasetSearchParameters(
            datasets=[ILATM1BDataset(version="1"), ILATM1BDataset(version="2")],
            bounding_box=common_bounding_box,
            temporal=((dt.date(2007, 1, 1), dt.date(2014, 10, 28))),
        ),
        output_dir=tmp_path,
        target_itrf=target_itrf,
    )

    df = dd.read_parquet(parquet_path)  # type: ignore[attr-defined]

    # Assert that the parquet data has the expected columns
    expected_columns = sorted(["latitude", "longitude", "elevation", "dataset"])
    assert expected_columns == sorted(df.columns)

    # Assert that the two datasets we expect are present.
    assert sorted(["ILATM1Bv1", "ILATM1Bv2"]) == sorted(
        df.dataset.unique().compute().values
    )
