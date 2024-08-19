from __future__ import annotations

import datetime as dt
from collections.abc import Sequence
from pathlib import Path

import earthaccess


def search_and_download(
    *,
    version: str,
    short_name: str,
    bounding_box: Sequence[float],
    temporal: tuple[dt.datetime | dt.date, dt.datetime | dt.date],
    output_dir: Path,
) -> list[Path]:
    """Search and download data.

    Wraps EDL auth and CMR search using `earthaccess`.

    Data matching the given parameters are downloaded to a subfolder of the
    given `output_dir` named after th e`short_name`.
    """
    earthaccess.login()

    results = earthaccess.search_data(
        short_name=short_name,
        version=version,
        bounding_box=bounding_box,
        temporal=temporal,
    )

    # short_name based subdir for data.
    output_subdir = output_dir / short_name
    output_subdir.mkdir(exist_ok=True)
    downloaded_files = earthaccess.download(results, str(output_subdir))
    downloaded_filepaths = [Path(filepath_str) for filepath_str in downloaded_files]

    return downloaded_filepaths
