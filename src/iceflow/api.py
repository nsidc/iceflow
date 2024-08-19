from __future__ import annotations

import functools
from pathlib import Path
from typing import Literal

import pandas as pd

from iceflow.data.atm1b import atm1b_data
from iceflow.data.fetch import search_and_download
from iceflow.data.models import (
    ATM1BDataFrame,
    ATM1BDataset,
    Dataset,
    DatasetSearchParameters,
    IceflowDataFrame,
)
from iceflow.itrf import ITRF
from iceflow.itrf.converter import transform_itrf

DatasetShortName = Literal["ILATM1B"]


@functools.singledispatch
def read_data(dataset: Dataset, _filepath: Path) -> IceflowDataFrame:
    msg = f"{dataset=} not recognized."
    raise RuntimeError(msg)


@read_data.register
def _(_dataset: ATM1BDataset, filepath: Path) -> ATM1BDataFrame:
    return atm1b_data(filepath)


def fetch_iceflow_df(
    *,
    dataset_search_params: DatasetSearchParameters,
    output_dir: Path,
    output_itrf: ITRF | None,
) -> IceflowDataFrame:
    """Search for data matching parameters and return an IceflowDataframe.

    Optionally transform data to the given ITRF for consistency.
    """

    results = search_and_download(
        short_name=dataset_search_params.dataset.short_name,
        version=dataset_search_params.dataset.version,
        bounding_box=dataset_search_params.bounding_box,
        temporal=dataset_search_params.temporal,
        output_dir=output_dir,
    )

    all_dfs = []
    for result in results:
        # TODO: how parameterize on short_name? Perhaps with e.g.,
        # https://docs.python.org/3.11/library/functools.html#functools.singledispatch
        data_df = read_data(dataset_search_params.dataset, result)
        all_dfs.append(data_df)

    complete_df = IceflowDataFrame(pd.concat(all_dfs))

    if output_itrf is not None:
        complete_df = transform_itrf(
            data=complete_df,
            target_itrf=output_itrf,
        )

    return complete_df
