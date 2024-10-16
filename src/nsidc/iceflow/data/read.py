from __future__ import annotations

import functools
from pathlib import Path

from nsidc.iceflow.data.atm1b import atm1b_data
from nsidc.iceflow.data.glah06 import glah06_data
from nsidc.iceflow.data.ilvis2 import ilvis2_data
from nsidc.iceflow.data.models import (
    ATM1BDataFrame,
    ATM1BDataset,
    Dataset,
    GLAH06DataFrame,
    GLAH06Dataset,
    IceflowDataFrame,
    ILVIS2DataFrame,
    ILVIS2Dataset,
)


@functools.singledispatch
def read_data(
    dataset: Dataset, _filepath: Path
) -> IceflowDataFrame | ATM1BDataFrame | ILVIS2DataFrame | GLAH06DataFrame:
    msg = f"{dataset=} not recognized."
    raise RuntimeError(msg)


@read_data.register
def _(_dataset: ATM1BDataset, filepath: Path) -> ATM1BDataFrame:
    return atm1b_data(filepath)


@read_data.register
def _(_dataset: ILVIS2Dataset, filepath: Path) -> ILVIS2DataFrame:
    return ilvis2_data(filepath)


@read_data.register
def _(_dataset: GLAH06Dataset, filepath: Path) -> GLAH06DataFrame:
    return glah06_data(filepath)
