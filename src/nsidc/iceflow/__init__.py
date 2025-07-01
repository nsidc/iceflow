"""
Copyright (c) 2025 NSIDC. All rights reserved.

iceflow: Harmonized access to (pre)OIB/IceSAT/IceSAT2 data

Users interact with `nsidc-iceflow` by:

* Searching for data that match an area of interest/time (`find_iceflow_data`)
* Downloading data (`download_iceflow_results`)
* (Optional) Creating a parquet datastore to facilitate reading the data (`make_iceflow_parquet`)
* Reading and doing analysis with the data (`dask.dataframe.read_parquet`,
  `read_iceflow_datafiles`)
* (Optional, if using `read_iceflow_datafiles`) Transform the lat/lon/elev data
  into a target International Terrestrial Reference Frame (ITRF) (`transform_itrf`)

"""

from __future__ import annotations

from nsidc.iceflow.api import make_iceflow_parquet
from nsidc.iceflow.data.fetch import download_iceflow_results, find_iceflow_data
from nsidc.iceflow.data.models import (
    Dataset,
    IceflowDataFrame,
)
from nsidc.iceflow.data.read import read_iceflow_datafiles
from nsidc.iceflow.data.supported_datasets import (
    ALL_SUPPORTED_DATASETS,
    BLATM1BDataset,
    GLAH06Dataset,
    ILATM1BDataset,
    ILVIS2Dataset,
)
from nsidc.iceflow.itrf.converter import transform_itrf

__version__ = "v1.1.0"


__all__ = [
    "ALL_SUPPORTED_DATASETS",
    "BLATM1BDataset",
    "Dataset",
    "GLAH06Dataset",
    "ILATM1BDataset",
    "ILVIS2Dataset",
    "IceflowDataFrame",
    "__version__",
    "download_iceflow_results",
    "find_iceflow_data",
    "make_iceflow_parquet",
    "read_iceflow_datafiles",
    "transform_itrf",
]
