"""
Copyright (c) 2024 NSIDC. All rights reserved.

iceflow: Harmonized access to (pre)OIB/IceSAT/IceSAT2 data

Users interact with `iceflow` by:

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
    ALL_DATASETS,
    BLATM1BDataset,
    BoundingBox,
    DatasetSearchParameters,
    GLAH06Dataset,
    IceflowDataFrame,
    ILATM1BDataset,
    ILVIS2Dataset,
)
from nsidc.iceflow.data.read import read_iceflow_datafiles
from nsidc.iceflow.itrf.converter import transform_itrf

# TODO: add bumpversion config to control this version number, and the conda
# recipe/meta.yaml.
__version__ = "v0.3.0"


__all__ = [
    "ALL_DATASETS",
    "BLATM1BDataset",
    "BoundingBox",
    "DatasetSearchParameters",
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
