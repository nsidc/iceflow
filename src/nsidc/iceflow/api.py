from __future__ import annotations

import shutil
from pathlib import Path

import dask.dataframe as dd
from loguru import logger

from nsidc.iceflow.data.fetch import download_iceflow_results, find_iceflow_data
from nsidc.iceflow.data.models import (
    DatasetSearchParameters,
    IceflowDataFrame,
)
from nsidc.iceflow.data.read import read_iceflow_datafiles
from nsidc.iceflow.itrf.converter import transform_itrf


def fetch_iceflow_df(
    *,
    dataset_search_params: DatasetSearchParameters,
    output_dir: Path,
    # TODO: also add option for target epoch!!
    output_itrf: str | None = None,
) -> IceflowDataFrame:
    """Search for data matching parameters and return an IceflowDataframe.

    Optionally transform data to the given ITRF for consistency.

    Note: a potentially large amount of data may be returned, especially if the
    user requests a large spatial/temporal area across multiple datasets. The
    result may not even fit in memory!

    Consider using `create_iceflow_parquet` to fetch and store data in parquet
    format.
    """

    iceflow_search_reuslts = find_iceflow_data(
        dataset_search_params=dataset_search_params,
    )

    downloaded_files = download_iceflow_results(
        iceflow_search_results=iceflow_search_reuslts,
        output_dir=output_dir,
    )

    iceflow_df = read_iceflow_datafiles(downloaded_files)

    if output_itrf is not None:
        iceflow_df = transform_itrf(
            data=iceflow_df,
            target_itrf=output_itrf,
        )

    return iceflow_df


def create_iceflow_parquet(
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
    output_subdir = output_dir / "iceflow.parquet"
    if output_subdir.exists():
        if overwrite:
            logger.info("Removing existing iceflow.parquet")
            shutil.rmtree(output_subdir)
        else:
            raise RuntimeError(
                "An iceflow parquet file already exists. Use `overwrite=True` to overwrite."
            )

    iceflow_search_results = find_iceflow_data(
        dataset_search_params=dataset_search_params,
    )

    for iceflow_search_result in iceflow_search_results:
        downloaded_files = download_iceflow_results(
            iceflow_search_results=[iceflow_search_result],
            output_dir=output_dir,
        )

        iceflow_df = read_iceflow_datafiles(downloaded_files)

        iceflow_df = transform_itrf(
            data=iceflow_df,
            target_itrf=target_itrf,
            target_epoch=target_epoch,
        )

        # Add a string col w/ dataset name and version.
        dataset = iceflow_search_result.dataset
        iceflow_df["dataset"] = [f"{dataset.short_name}v{dataset.version}"] * len(
            iceflow_df.latitude
        )
        common_columns = ["latitude", "longitude", "elevation", "dataset"]
        common_dask_df = dd.from_pandas(iceflow_df[common_columns])  # type: ignore[attr-defined]
        if output_subdir.exists():
            dd.to_parquet(  # type: ignore[attr-defined]
                df=common_dask_df,
                path=output_subdir,
                append=True,
                ignore_divisions=True,
            )
        else:
            dd.to_parquet(  # type: ignore[attr-defined]
                df=common_dask_df,
                path=output_subdir,
            )

    return output_subdir
