# Jupyter Notebooks

```{toctree}
:maxdepth: 2
:hidden:
:caption: content

./0_introduction.ipynb
./corrections.ipynb
./iceflow-example.ipynb
./iceflow-with-icepyx.ipynb
```

[Jupyter notebooks](https://docs.jupyter.org/en/latest/) provide executable
examples of how to use `iceflow`.

## Prerequisites

The `iceflow` notebooks are best approached with some familiarity with Python
and its geoscience stack. If you feel like learning more about geoscience and
Python, you can find great tutorials by CU Boulder's Earth Lab here:
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

## Iceflow notebooks

- [Altimetry Data at NSIDC](./0_introduction) has an overview about airborne
  altimetry and related data sets from NASA’s
  [IceBridge](https://www.nasa.gov/mission_pages/icebridge/index.html) mission,
  and satellite altimetry data from
  [ICESat/GLAS](https://icesat.gsfc.nasa.gov/icesat/) and
  [ICESat-2](https://icesat-2.gsfc.nasa.gov/).

- [NSIDC Iceflow example](./iceflow-example) provides an example of how to
  search for, download, and interact with `ILATM1B v1` data for a small area of
  interest. This notebook also illustrates how to perform
  [ITRF](https://itrf.ign.fr/) transformations to facilitate comparisons across
  datasets. To learn more about ITRF transformations, see the
  [Applying Coordinate Transformations to Facilitate Data Comparison](./corrections)
  notebook.

- [Using iceflow with icepyx to Generate an Elevation Timeseries](./iceflow-with-icepyx)
  shows how to search for, download, and interact with a large amount of data
  across many datasets supported by `iceflow`. It also illustrates how to
  utilize [icepyx](https://icepyx.readthedocs.io/en/latest/) to find and access
  ICESat-2 data. Finally, the notebook provides a simple time-series analysis
  for elevation change over an area of interest across `iceflow` supported
  datasets and ICESat-2.
