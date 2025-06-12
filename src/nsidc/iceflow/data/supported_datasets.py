from __future__ import annotations

from typing import Literal

from nsidc.iceflow.data.models import (
    ATM1BDataset,
    ATM1BShortName,
    Dataset,
    DatasetShortName,
)


class ILATM1BDataset(ATM1BDataset):
    short_name: ATM1BShortName = "ILATM1B"
    version: Literal["1", "2"]


class BLATM1BDataset(ATM1BDataset):
    short_name: ATM1BShortName = "BLATM1B"
    # There is only 1 version of BLATM1B
    version: Literal["1"] = "1"


class ILVIS2Dataset(Dataset):
    short_name: DatasetShortName = "ILVIS2"
    version: Literal["1", "2"]


class GLAH06Dataset(Dataset):
    short_name: DatasetShortName = "GLAH06"
    # Note: some dataset versions are padded with zeros like GLAH06. NSIDC
    # documentation refers to "version 34", but CMR only recognizes "034".  As a
    # rule-of-thumb, ICESat-2, SMAP, and GLAH/GLA datasets have zero padding.
    version: Literal["034"] = "034"


ALL_SUPPORTED_DATASETS: list[Dataset] = [
    ILATM1BDataset(version="1"),
    ILATM1BDataset(version="2"),
    BLATM1BDataset(version="1"),
    ILVIS2Dataset(version="1"),
    ILVIS2Dataset(version="2"),
    GLAH06Dataset(),
]
