from __future__ import annotations

from pathlib import Path

import pandas as pd

from iceflow.data.fetch import search_and_download
from iceflow.data.models import (
    DatasetSearchParameters,
    IceflowDataFrame,
)
from iceflow.data.read import read_data
from iceflow.itrf.converter import transform_itrf


def fetch_iceflow_df(
    *,
    dataset_search_params: DatasetSearchParameters,
    output_dir: Path,
    output_itrf: str | None,
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
        data_df = read_data(dataset_search_params.dataset, result)
        all_dfs.append(data_df)

    complete_df = IceflowDataFrame(pd.concat(all_dfs))

    if output_itrf is not None:
        complete_df = transform_itrf(
            data=complete_df,
            target_itrf=output_itrf,
        )

    return complete_df
