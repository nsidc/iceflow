# Jupyter Notebooks

```{toctree}
:maxdepth: 2
:hidden:
:caption: content

./corrections
./iceflow-example
./iceflow-with-icepyx
```

[Jupyter notebooks](https://docs.jupyter.org/en/latest/) provide executable
examples of how to use `nsidc-iceflow`.

## Prerequisites

The `nsidc-iceflow` notebooks are best approached with some familiarity with
Python and its geoscience stack. If you feel like learning more about geoscience
and Python, you can find great tutorials by CU Boulder's Earth Lab here:
[Data Exploration and Analysis Lessons](https://www.earthdatascience.org/tags/data-exploration-and-analysis/)
or by the Data Carpentry project:
[Introduction to Geospatial Concepts](https://datacarpentry.org/organization-geospatial/)

Some Python packages/libraries that users may consider investigating include:

- [_icepyx_](https://icepyx.readthedocs.io/en/latest/): Library for ICESat-2
  data users
- [_geopandas_](https://geopandas.org/): Library to simplify working with
  geospatial data in Python (using pandas)
- [_h5py_](https://github.com/h5py/h5py): Pythonic wrapper around the
  [\*HDF5 library](https://en.wikipedia.org/wiki/Hierarchical_Data_Format)
- [_matplotlib_](https://matplotlib.org/): Comprehensive library for creating
  static, animated, and interactive visualizations in Python
- [_vaex_](https://github.com/vaexio/vaex): High performance Python library for
  lazy Out-of-Core dataframes (similar to _pandas_), to visualize and explore
  big tabular data sets

## `nsidc-iceflow` notebooks

- [NSIDC Iceflow example](./iceflow-example) provides an example of how to
  search for, download, and interact with `ILATM1B v1` data for a small area of
  interest. This notebook also illustrates how to perform
  [ITRF](https://itrf.ign.fr/) transformations to facilitate comparisons across
  datasets. To learn more about ITRF transformations, see the
  [Applying Coordinate Transformations to Facilitate Data Comparison](./corrections)
  notebook.

- [Using nsidc-iceflow with icepyx to Generate an Elevation Timeseries](./iceflow-with-icepyx)
  shows how to search for, download, and interact with a large amount of data
  across many datasets supported by `nsidc-iceflow`. It also illustrates how to
  utilize [icepyx](https://icepyx.readthedocs.io/en/latest/) to find and access
  ICESat-2 data. Finally, the notebook provides a simple time-series analysis
  for elevation change over an area of interest across `nsidc-iceflow` supported
  datasets and ICESat-2.

### Downloading `nsidc-iceflow` notebooks

Users may wish to try executing the `nsidc-iceflow` notebooks themselves.
Iceflow notebooks can be downloaded
[from GitHub](https://github.com/nsidc/nsidc-iceflow/tree/main/docs/notebooks/).
