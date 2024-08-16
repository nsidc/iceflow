from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Literal

import pandas as pd

from iceflow.data.atm1b import atm1b_data
from iceflow.data.fetch import search_and_download
from iceflow.data.models import IceflowDataFrame
from iceflow.itrf import ITRF
from iceflow.itrf.converter import transform_itrf

DatasetShortName = Literal["ILATM1B"]


def fetch_iceflow_df(
    *,
    # TODO: consider some container (typeddict/dataclass/pydantic) to contain &
    # validate dataset search params
    dataset_version: str,
    dataset_short_name: DatasetShortName,
    bounding_box: Sequence[float],
    temporal: tuple[str, str],
    output_dir: Path,
    output_itrf: ITRF | None,
) -> IceflowDataFrame:
    """Search for data matching parameters and return an IceflowDataframe.

    Optionally transform data to the given ITRF for consistency.
    """

    results = search_and_download(
        short_name=dataset_short_name,
        version=dataset_version,
        output_dir=output_dir,
        bounding_box=bounding_box,
        temporal=temporal,
    )

    all_dfs = []
    for result in results:
        # TODO: how parameterize on short_name?
        data_df = atm1b_data(result)
        all_dfs.append(data_df)

    complete_df = pd.concat(all_dfs)
    complete_df = IceflowDataFrame(complete_df)

    if output_itrf is not None:
        complete_df = transform_itrf(
            data=complete_df,
            target_itrf=output_itrf,
        )

    return complete_df
