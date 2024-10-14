# v0.3.0

- Use `pydantic` to create custom BoundingBox class for
  `DatasetSearchParameters`.
- `transform_itrf` will calculate plate for source ITRF if not given with
  `target_epoch`.
- If the ATM1B qfit file header does not contain any mention of the ITRF, source it from hard-coded ranges based on date.
- Add support for ILATM1B v2 and BLATM1B v1.

# v0.2.0

- Use `pydantic` to manage and validate dataset & dataset search parameters.
- Fixup use of `pandera` to actually run validators.
- Use `np.nan` for nodata values instead of `0`.
- Update package structure to be namespaced to `nsidc` and publish to PyPi.

# v0.1.0

- Initial release
