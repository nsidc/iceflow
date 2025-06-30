# v1.1.0

- Support selecting alternative lat/lon/elev triplet as primary lat/lon/elev
  fields for ILVIS2 data. By default, the `low_mode` coordinates are used, which
  represent the center of the lowest detected mode within the waveform. This
  replicates the behavior of the valkyrie service this code is based on. Users
  may now choose between the following coordinate sets: `low_mode` (the
  default), `high_mode`, `centroid` (ILVIS2 v1 only), and `highest_signal`
  (ILVIS2 v2 only).
- Update documentation around ILVIS2 datasets and their multiple tuplets of
  lat/lon/elev fields.
- Update data model for `IceflowDataFrame` to include `dataset`, which gives the
  dataset short name and version as a string (e.g., ILVIS v2 is "ILVISv2").
- Add `total_size_mb` property to `IceflowSearchResult` and log size when
  downloading.

# v1.0.0

- Update `transform_itrf` function to be more flexible. Both forward and reverse
  transformations between proj-supported ITRFs are now supported, which means
  that more ITRF-to-ITRF transformations are handled.
- Update `icepyx` dependency to >=2.0.0 for the "Using nsidc-iceflow with icepyx
  to Generate an Elevation Timeseries" notebook.
- Filter for cloud-hosted data, avoiding duplicate granule results from
  `fetch.find_iceflow_data`
- Pass through search kwargs to `earthaccess` without any type validation. This
  allows earthaccess to do watever validation it needs to, and then it passes
  those on to CMR. This provides much greater flexibility over data search and
  makes the interface more consistent with `icepyx` and `earthaccess`.
  https://github.com/nsidc/nsidc-iceflow/issues/51.
- Remove restrictive `fetch_iceflow_df` function from public API. Users should
  utilize the search, download, and read functions described in
  `doc/getting-started.md` instead.

# v0.3.0

- Use `pydantic` to create custom BoundingBox class for
  `DatasetSearchParameters`.
- `transform_itrf` will calculate plate for source ITRF if not given with
  `target_epoch`.
- Add support for ILATM1B v2 and BLATM1B v1.
- Add support for ILVIS2 v1 and v2.
- Improve API, providing ability to search across datasets and save to
  intermediate parquet file.
- Add jupyter notebook showing use of `nsidc-iceflow` alongside `icepyx`

# v0.2.0

- Use `pydantic` to manage and validate dataset & dataset search parameters.
- Fixup use of `pandera` to actually run validators.
- Use `np.nan` for nodata values instead of `0`.
- Update package structure to be namespaced to `nsidc` and publish to PyPi.

# v0.1.0

- Initial release
