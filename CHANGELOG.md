# v1.0.0

- Update `transform_itrf` function to be more flexible. Both forward and reverse
  transformations between proj-supported ITRFs are now supported, which means
  that more ITRF-to-ITRF transformations are handled.
- Update `icepyx` dependency to >=2.0.0 for the "Using iceflow with icepyx to
  Generate an Elevation Timeseries" notebook.
- Filter for cloud-hosted data, avoiding duplicate granule results from
  `fetch.find_iceflow_data`

# v0.3.0

- Use `pydantic` to create custom BoundingBox class for
  `DatasetSearchParameters`.
- `transform_itrf` will calculate plate for source ITRF if not given with
  `target_epoch`.
- Add support for ILATM1B v2 and BLATM1B v1.
- Add support for ILVIS2 v1 and v2.
- Improve API, providing ability to search across datasets and save to
  intermediate parquet file.
- Add jupyter notebook showing use of `iceflow` alongside `icepyx`

# v0.2.0

- Use `pydantic` to manage and validate dataset & dataset search parameters.
- Fixup use of `pandera` to actually run validators.
- Use `np.nan` for nodata values instead of `0`.
- Update package structure to be namespaced to `nsidc` and publish to PyPi.

# v0.1.0

- Initial release
