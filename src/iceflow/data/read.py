from __future__ import annotations

import functools
from pathlib import Path

from iceflow.data.atm1b import atm1b_data
from iceflow.data.models import (
    ATM1BDataFrame,
    ATM1BDataset,
    Dataset,
    IceflowDataFrame,
)


@functools.singledispatch
def read_data(dataset: Dataset, _filepath: Path) -> IceflowDataFrame | ATM1BDataFrame:
    msg = f"{dataset=} not recognized."
    raise RuntimeError(msg)


@read_data.register
def _(_dataset: ATM1BDataset, filepath: Path) -> ATM1BDataFrame:
    return atm1b_data(filepath)
