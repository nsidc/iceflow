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
from nsidc.iceflow.data.ilvis2 import (
    ILVIS2_COORDINATE_SETS,
    ILVIS2_DEFAULT_COORDINATE_SET,
)
from nsidc.iceflow.data.models import (
    BoundingBoxLike,
    Dataset,
    IceflowDataFrame,
    TemporalRange,
)
from nsidc.iceflow.data.read import read_iceflow_datafiles
from nsidc.iceflow.data.supported_datasets import (
    ALL_SUPPORTED_DATASETS,
    BLATM1BDataset,
    GLAH06Dataset,
    ILATM1BDataset,
    ILVIS2Dataset,
)
from nsidc.iceflow.itrf.converter import transform_itrf


def _fetch_iceflow_df(
    *,
    bounding_box: BoundingBoxLike,
    temporal: TemporalRange,
    datasets: list[Dataset] = ALL_SUPPORTED_DATASETS,
    output_dir: Path,
    output_itrf: str | None = None,
    ilvis2_coordinate_set: ILVIS2_COORDINATE_SETS = ILVIS2_DEFAULT_COORDINATE_SET,
):
    """Search for data matching parameters and return an IceflowDataframe.

    Optionally transform data to the given ITRF for consistency.

    Note: a potentially large amount of data may be returned, especially if the
    user requests a large spatial/temporal area across multiple datasets. The
    result may not even fit in memory!

    Consider using `make_iceflow_parquet` to store downloaded data in parquet
    format.
    """

    iceflow_search_reuslts = find_iceflow_data(
        bounding_box=bounding_box,
        temporal=temporal,
        datasets=datasets,
    )

    downloaded_files = download_iceflow_results(
        iceflow_search_results=iceflow_search_reuslts,
        output_dir=output_dir,
    )

    iceflow_df = read_iceflow_datafiles(
        downloaded_files, ilvis2_coordinate_set=ilvis2_coordinate_set
    )

    if output_itrf is not None:
        iceflow_df = transform_itrf(
            data=iceflow_df,
            target_itrf=output_itrf,
        )

    return iceflow_df


def test_atm1b_ilatm1b(tmp_path):
    target_itrf = "ITRF2014"
    common_bounding_box = (
        -103.125559,
        -75.180563,
        -102.677327,
        -74.798063,
    )

    # Native ITRF is ITRF2005
    results_ilatm1b_v1_2009 = _fetch_iceflow_df(
        datasets=[ILATM1BDataset(version="1")],
        bounding_box=common_bounding_box,
        temporal=(dt.date(2009, 11, 1), dt.date(2009, 12, 1)),
        output_dir=tmp_path,
        output_itrf=target_itrf,
    )

    assert (results_ilatm1b_v1_2009.dataset == "ILATM1Bv1").all()

    # Native ITRF is ITRF2008
    results_ilatm1b_v2_2014 = _fetch_iceflow_df(
        datasets=[ILATM1BDataset(version="2")],
        bounding_box=common_bounding_box,
        temporal=(dt.date(2014, 11, 1), dt.date(2014, 12, 1)),
        output_dir=tmp_path,
        output_itrf=target_itrf,
    )

    assert (results_ilatm1b_v2_2014.dataset == "ILATM1Bv2").all()

    complete_df = IceflowDataFrame(
        pd.concat([results_ilatm1b_v1_2009, results_ilatm1b_v2_2014])
    )

    assert (complete_df.ITRF.unique() == target_itrf).all()


def test_atm1b_blatm1b(tmp_path):
    common_bounding_box = (
        -120.0,
        -75.1,
        -92.0,
        -65.0,
    )

    results_blamt1b_v1_2014 = _fetch_iceflow_df(
        datasets=[BLATM1BDataset()],
        bounding_box=common_bounding_box,
        temporal=(dt.date(2002, 11, 27), dt.date(2002, 11, 28)),
        output_dir=tmp_path,
    )

    assert (results_blamt1b_v1_2014.dataset == "BLATM1Bv1").all()

    assert (results_blamt1b_v1_2014.ITRF == "ITRF2000").all()


def test_ivlis2(tmp_path):
    results_v1 = _fetch_iceflow_df(
        datasets=[ILVIS2Dataset(version="1")],
        bounding_box=(
            -120.0,
            -80.0,
            -90.0,
            -65.0,
        ),
        temporal=(dt.datetime(2009, 10, 25, 15), dt.datetime(2009, 10, 25, 17)),
        output_dir=tmp_path,
    )

    assert (results_v1.dataset == "ILVIS2v1").all()

    assert (results_v1.ITRF == "ITRF2000").all()

    results_v2 = _fetch_iceflow_df(
        datasets=[ILVIS2Dataset(version="2")],
        bounding_box=(
            -180,
            60.0,
            180,
            90,
        ),
        temporal=(dt.datetime(2017, 8, 25, 0), dt.datetime(2017, 8, 25, 14, 30)),
        output_dir=tmp_path,
    )

    assert (results_v2.dataset == "ILVIS2v2").all()

    assert (results_v2.ITRF == "ITRF2008").all()

    # test that v1 and 2 can be concatenated
    complete_df = IceflowDataFrame(pd.concat([results_v1, results_v2]))

    assert complete_df is not None

    # Confirm that we get the alt. set of ilvis2 coordinates when specified.
    results_v2_alt_coords = _fetch_iceflow_df(
        datasets=[ILVIS2Dataset(version="2")],
        bounding_box=(
            -180,
            60.0,
            180,
            90,
        ),
        temporal=(dt.datetime(2017, 8, 25, 0), dt.datetime(2017, 8, 25, 14, 30)),
        output_dir=tmp_path,
        ilvis2_coordinate_set="highest_signal",
    )
    assert (results_v2_alt_coords.latitude == results_v2_alt_coords.TLAT).all()
    assert (results_v2_alt_coords.longitude == results_v2_alt_coords.TLON).all()
    assert (results_v2_alt_coords.elevation == results_v2_alt_coords.ZT).all()

    # Results v1 should use the default ("low_mode")
    assert (results_v2.latitude == results_v2.GLAT).all()
    assert (results_v2.longitude == results_v2.GLON).all()
    assert (results_v2.elevation == results_v2.ZG).all()


def test_glah06(tmp_path):
    common_bounding_box = (
        -180,
        -90,
        180,
        90,
    )

    results = _fetch_iceflow_df(
        datasets=[GLAH06Dataset()],
        bounding_box=common_bounding_box,
        temporal=(
            dt.datetime(2003, 2, 20, 22, 25),
            dt.datetime(2003, 2, 20, 22, 25, 38),
        ),
        output_dir=tmp_path,
    )

    assert (results.dataset == "GLAH06v034").all()
    assert (results.ITRF == "ITRF2008").all()


def _create_iceflow_parquet(
    *,
    bounding_box: BoundingBoxLike,
    temporal: TemporalRange,
    datasets: list[Dataset] = ALL_SUPPORTED_DATASETS,
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
        datasets=datasets,
        temporal=temporal,
        bounding_box=bounding_box,
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
    common_bounding_box = (
        -49.149,
        69.186,
        -48.949,
        69.238,
    )

    # This should finds 4 results for ILATM1B v1 and 3 results for v2.
    parquet_path = _create_iceflow_parquet(
        datasets=[ILATM1BDataset(version="1"), ILATM1BDataset(version="2")],
        bounding_box=common_bounding_box,
        temporal=((dt.date(2007, 1, 1), dt.date(2014, 10, 28))),
        output_dir=tmp_path,
        target_itrf=target_itrf,
    )

    df = dd.read_parquet(parquet_path)

    # Assert that the parquet data has the expected columns
    expected_columns = sorted(["latitude", "longitude", "elevation", "dataset"])
    assert expected_columns == sorted(df.columns)

    # Assert that the two datasets we expect are present.
    assert sorted(["ILATM1Bv1", "ILATM1Bv2"]) == sorted(
        df.dataset.unique().compute().values
    )
