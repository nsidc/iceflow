from __future__ import annotations

from nsidc.iceflow.data.models import (
    BLATM1BDataset,
    Dataset,
    GLAH06Dataset,
    ILATM1BDataset,
    ILVIS2Dataset,
)

ALL_DATASETS: list[Dataset] = [
    ILATM1BDataset(version="1"),
    ILATM1BDataset(version="2"),
    BLATM1BDataset(version="1"),
    ILVIS2Dataset(version="1"),
    ILVIS2Dataset(version="2"),
    GLAH06Dataset(),
]
