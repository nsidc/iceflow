from __future__ import annotations

import datetime as dt
import shutil
from pathlib import Path

import dask.dataframe as dd
import pandas as pd
from loguru import logger

from nsidc.iceflow.data.fetch import search_and_download
from nsidc.iceflow.data.models import (
    BoundingBox,
    Dataset,
    DatasetSearchParameters,
    IceflowDataFrame,
)
from nsidc.iceflow.data.read import read_data
from nsidc.iceflow.itrf.converter import transform_itrf


def _df_for_one_dataset(
    *,
    dataset: Dataset,
    bounding_box: BoundingBox,
    temporal: tuple[dt.datetime | dt.date, dt.datetime | dt.date],
    output_dir: Path,
    # TODO: also add option for target epoch!!
    output_itrf: str | None,
) -> IceflowDataFrame:
    results = search_and_download(
        short_name=dataset.short_name,
        version=dataset.version,
        bounding_box=bounding_box,
        temporal=temporal,
        output_dir=output_dir,
    )

    all_dfs = []
    for result in results:
        data_df = read_data(dataset, result)
        all_dfs.append(data_df)

    complete_df = IceflowDataFrame(pd.concat(all_dfs))

    if output_itrf is not None:
        complete_df = transform_itrf(
            data=complete_df,
            target_itrf=output_itrf,
        )

    return complete_df


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

    dfs = []
    for dataset in dataset_search_params.datasets:
        result = _df_for_one_dataset(
            dataset=dataset,
            temporal=dataset_search_params.temporal,
            bounding_box=dataset_search_params.bounding_box,
            output_dir=output_dir,
            output_itrf=output_itrf,
        )
        dfs.append(result)

    complete_df = IceflowDataFrame(pd.concat(dfs))

    return complete_df


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

    for dataset in dataset_search_params.datasets:
        results = search_and_download(
            short_name=dataset.short_name,
            version=dataset.version,
            temporal=dataset_search_params.temporal,
            bounding_box=dataset_search_params.bounding_box,
            output_dir=output_dir,
        )

        for result in results:
            data_df = read_data(dataset, result)
            df = IceflowDataFrame(data_df)

            df = transform_itrf(
                data=df,
                target_itrf=target_itrf,
                target_epoch=target_epoch,
            )

            # Add a string col w/ dataset name and version.
            df["dataset"] = [f"{dataset.short_name}v{dataset.version}"] * len(
                df.latitude
            )
            common_columns = ["latitude", "longitude", "elevation", "dataset"]
            common_dask_df = dd.from_pandas(df[common_columns])  # type: ignore[attr-defined]
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
