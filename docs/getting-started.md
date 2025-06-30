# Getting started with `nsidc-iceflow`

## Altimetry Overview

Before working with `nsidc-iceflow` directly, it may be helpful to understand
the basics about pre-IceBridge, IceBridge, ICESat/GLAS and ICESat-2 datasets.
Learn about these `nsidc-iceflow` supported datasets in
[Altimetry Data at the NSIDC DAAC: Point Cloud Data Overview](./altimetry-data-overview)

## Jupyter Notebooks

Executable Jupyter Notebooks provide a great starting point for using
`nsidc-iceflow`. See [Jupyter Notebooks](./notebooks/index.md) for more
information.

## API overview

`nsidc-iceflow` provides a simple API for finding, downloading, and accessing
iceflow-supported datasets.

### Finding data

To find `nsidc-iceflow`-supported data for an area of interest and timeframe,
use [`find_iceflow_data`](nsidc.iceflow.find_iceflow_data):

```
import datetime as dt

from nsidc.iceflow import find_iceflow_data


search_results = find_iceflow_data(
    # Lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat
    bounding_box=(-103.125559, -75.180563, -102.677327, -74.798063),
    temporal=(dt.date(2009, 11, 1), dt.date(2009, 12, 31)),
)
```

By default, all iceflow-supported datasets are searched. To search for a
specific subset of iceflow-supported datasets, use the `datasets` kwarg:

```
from nsidc.iceflow import Dataset


search_results = find_iceflow_data(
    datasets=[Dataset(short_name="ILATM1B", version="1")],
    # Lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat
    bounding_box=(-103.125559, -75.180563, -102.677327, -74.798063),
    temporal=(dt.date(2009, 11, 1), dt.date(2009, 12, 31)),
)
```

```{include} ../supported_datasets

```

`nsidc-iceflow` currently supports the following datasets:

| Dataset                                                  | Temporal Coverage             |
| -------------------------------------------------------- | ----------------------------- |
| [ILATM1B v1](https://nsidc.org/data/ilatm1b/versions/1)  | 2009-03-31 through 2012-11-08 |
| [ILATM1B v2](https://nsidc.org/data/ilatm1b/versions/2)  | 2013-03-20 through 2019-11-20 |
| [BLATM1B v1](https://nsidc.org/data/blatm1b/versions/1)  | 1993-06-23 through 2008-10-30 |
| [ILVIS2 v1](https://nsidc.org/data/ilvis2/versions/1)    | 2009-04-14 through 2015-10-31 |
| [ILVIS2 v2](https://nsidc.org/data/ilvis2/versions/2)    | 2017-08-25 through 2017-09-20 |
| [GLAH06 v034](https://nsidc.org/data/glah06/versions/34) | 2003-02-20 through 2009-10-11 |

All other keyword arguments to this function (e.g,. `bounding_box`, `temporal`)
map to [CMR](https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html)
search parameters, and are passed un-modified to
[earthaccess.search_data](https://earthaccess.readthedocs.io/en/latest/user-reference/api/api/#earthaccess.api.search_data)
to perform the search.

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
    ilvis2_coordinate_set="low_mode",
)
df = dd.read_parquet(parquet_path)
```

Note that `make_iceflow_parquet` creates a parquet datastore for the data in the
provided `data_dir` with the data transformed into a common
[ITRF](https://itrf.ign.fr/) to facilitate analysis. Only datetime, latitude,
longitude, elevation, and dataset fields are preserved in the parquet datastore.

To access and analyze the full data record in the source files, use
[`read_iceflow_datafiles`](nsidc.iceflow.read_iceflow_datafiles):

```
from nsidc.iceflow import read_iceflow_datafiles

# Read all of the data in the source files - not just lat/lon/elev.
df = read_iceflow_datafiles(
    downloaded_files,
    ilvis2_coordinate_set="low_mode",
)

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

#### Special considerations for ILVIS2 data

Users of ILVIS2 data should be aware that ILVIS2 data contains multiple sets of
lat/lon/elev that may be of interest. By default, the `low_mode` set is used as
the primary set of latitude/longitude/elevation used by `nsidc-iceflow`.

See [ILVIS2 data](./altimetry-data-overview.md#ilvis2-data) for more
information.
