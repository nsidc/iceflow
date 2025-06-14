# Getting started with iceflow

## Altimetry Overview

Before working with `iceflow` directly, it may be helpful to understand the
basics about pre-IceBridge, IceBridge, ICESat/GLAS and ICESat-2 datasets. Learn
about these `iceflow` supported datasets in
[Altimetry Data at the NSIDC DAAC: Point Cloud Data Overview](./altimetry-data-overview)

## Jupyter Notebooks

Executable Jupyter Notebooks provide a great starting point for using `iceflow`.
See [Jupyter Notebooks](./notebooks/index.md) for more information.

## API overview

`iceflow` provides a simple API for finding, downloading, and accessing
iceflow-supported datasets.

### Finding data

To find `iceflow`-supported data for an area of interest and timeframe, use
[`find_iceflow_data`](nsidc.iceflow.find_iceflow_data):

```
import datetime as dt

from nsidc.iceflow import (
    find_iceflow_data,
    DatasetSearchParameters,
    BoundingBox,
)


search_results = find_iceflow_data(
    dataset_search_params=DatasetSearchParameters(
        bounding_box=BoundingBox(lower_left_lon=-103.125559, lower_left_lat=-75.180563, upper_right_lon=-102.677327, upper_right_lat=-74.798063),
        temporal=(dt.date(2009, 11, 1), dt.date(2009, 12, 31)),
    ),
)
```

### Downloading data

Once search results have been found, download data with
[`download_iceflow_results`](nsidc.iceflow.download_iceflow_results):

```
from pathlib import Path
from nsidc.iceflow import download_iceflow_results

downloaded_filepaths = download_iceflow_results(
    iceflow_search_result=iceflow_search_result,
    output_dir=Path("/path/to/data/dir/"),
)
```

### Accessing data

Iceflow data can be very large, and fitting it into memory can be a challenge!
To facilitate analysis of iceflow data,
[`make_iceflow_parquet`](nsidc.iceflow.make_iceflow_parquet) provides a
mechanism to create a [parquet](https://parquet.apache.org/docs/overview/)
datastore that can be used alongside [dask](https://www.dask.org/):

```
import dask.dataframe as dd
from nsidc.iceflow import make_iceflow_parquet

parquet_path = make_iceflow_parquet(
    data_dir=Path("/path/to/data/dir/"),
    target_itrf="ITRF2014",
)
df = dd.read_parquet(parquet_path)
```

Note that `make_iceflow_parquet` creates a parquet datastore for the data in the
provided `data_dir` with the data transformed into a common
[ITRF](https://itrf.ign.fr/) to facilitate analysis. Only datetime, lat, lon,
and elevation fields are preserved in the parquet datastore.

To access and analyze the full data record in the source files, use
[`read_iceflow_datafiles`](nsidc.iceflow.read_iceflow_datafiles):

```
from nsidc.iceflow import read_iceflow_datafiles

# Read all of the data in the source files - not just lat/lon/elev.
df = read_iceflow_datafiles(downloaded_files)

# Optional: transform lat/lon/elev to common ITRF:
from nsidc.iceflow import transform_itrf
df = transform_itrf(
    data=df,
    target_itrf="ITRF2014",
)
```

Note that `read_iceflow_datafiles` reads all of the data from the given
filepaths. This could be a large amount of data, and could cause your program to
crash if physical memory limits are exceeded.
