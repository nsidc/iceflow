from __future__ import annotations

from pathlib import Path

import pandas as pd

from nsidc.iceflow.data.atm1b import atm1b_data
from nsidc.iceflow.data.glah06 import glah06_data
from nsidc.iceflow.data.ilvis2 import ilvis2_data
from nsidc.iceflow.data.models import (
    ATM1BDataFrame,
    GLAH06DataFrame,
    IceflowDataFrame,
    ILVIS2DataFrame,
)


def read_iceflow_datafile(
    filepath: Path,
) -> IceflowDataFrame | ATM1BDataFrame | ILVIS2DataFrame | GLAH06DataFrame:
    # iceflow data are expected to exist in a directory named like
    # `{short_name}_{version}`
    dataset_subdir = filepath.parent.name
    short_name, _version = dataset_subdir.split("_")

    if short_name in ["ILATM1B", "BLATM1B"]:
        return atm1b_data(filepath)
    elif short_name == "ILVIS2":
        return ilvis2_data(filepath)
    elif short_name == "GLAH06":
        return glah06_data(filepath)
    else:
        err_msg = f"Unrecognized dataset {short_name=} extracted from {filepath.parent}"
        raise RuntimeError(err_msg)


def read_iceflow_datafiles(filepaths: list[Path]) -> IceflowDataFrame:
    all_dfs = []
    for filepath in filepaths:
        df = read_iceflow_datafile(filepath)
        all_dfs.append(df)

    complete_df = IceflowDataFrame(pd.concat(all_dfs))

    return complete_df
