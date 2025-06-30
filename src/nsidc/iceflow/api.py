"""Module with functions defining the user-facing API for nsidc-iceflow."""

from __future__ import annotations

import shutil
from pathlib import Path

import dask.dataframe as dd
from loguru import logger

from nsidc.iceflow.data.ilvis2 import ILVIS2_DEFAULT_COORDINATE_SET
from nsidc.iceflow.data.read import read_iceflow_datafiles
from nsidc.iceflow.data.supported_datasets import ALL_SUPPORTED_DATASETS
from nsidc.iceflow.itrf.converter import transform_itrf


def make_iceflow_parquet(
    *,
    data_dir: Path,
    target_itrf: str,
    overwrite: bool = False,
    target_epoch: str | None = None,
    ilvis2_coordinate_set=ILVIS2_DEFAULT_COORDINATE_SET,
) -> Path:
    """Create a parquet dataset containing the lat/lon/elev data in `data_dir`.

    This function creates a parquet dataset that can be easily used alongside
    dask, containing lat/lon/elev data. Users who are interested in the full
    data record with all fields provided by data in the `data_dir` should use
    `read_iceflow_datafiles`.

    Note: this function writes a single `iceflow.parquet` to the output
    dir. This code does not currently support updates to the parquet after being
    written. This is intended to help facilitate analysis of a specific area
    over time. If an existing `iceflow.parquet` exists and the user wants to
    create a new `iceflow.parquet` for a different area or timespan, they will
    need to move/remove the existing `iceflow.parquet` first (e.g., with the
    `overwrite=True` kwarg).
    """
    parquet_subdir = data_dir / "iceflow.parquet"
    if parquet_subdir.exists():
        if overwrite:
            logger.info("Removing existing iceflow.parquet")
            shutil.rmtree(parquet_subdir)
        else:
            raise RuntimeError(
                "An iceflow parquet file already exists. Use `overwrite=True` to overwrite."
            )

    all_subdirs = [
        data_dir / ds.subdir_name
        for ds in ALL_SUPPORTED_DATASETS
        if (data_dir / ds.subdir_name).is_dir()
    ]
    for subdir in all_subdirs:
        iceflow_filepaths = [path for path in subdir.iterdir() if path.is_file()]
        iceflow_df = read_iceflow_datafiles(
            iceflow_filepaths,
            ilvis2_coordinate_set=ilvis2_coordinate_set,
        )

        iceflow_df = transform_itrf(
            data=iceflow_df,
            target_itrf=target_itrf,
            target_epoch=target_epoch,
        )

        # Add a string col w/ dataset name and version.
        common_columns = ["latitude", "longitude", "elevation", "dataset"]
        common_dask_df = dd.from_pandas(iceflow_df[common_columns])
        if parquet_subdir.exists():
            dd.to_parquet(
                df=common_dask_df,
                path=parquet_subdir,
                append=True,
                ignore_divisions=True,
            )
        else:
            dd.to_parquet(
                df=common_dask_df,
                path=parquet_subdir,
            )

    return parquet_subdir
