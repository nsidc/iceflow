from __future__ import annotations

import datetime as dt
from pathlib import Path

import earthaccess
from loguru import logger

from nsidc.iceflow.data.models import BoundingBox


def search_and_download(
    *,
    version: str,
    short_name: str,
    bounding_box: BoundingBox,
    temporal: tuple[dt.datetime | dt.date, dt.datetime | dt.date],
    output_dir: Path,
) -> list[Path]:
    """Search and download data.

    Wraps EDL auth and CMR search using `earthaccess`.

    Data matching the given parameters are downloaded to a subfolder of the
    given `output_dir` named after the `short_name`.
    """
    earthaccess.login()

    ctx_string = f"{short_name=} {version=} with {bounding_box=} {temporal=}"

    try:
        results = earthaccess.search_data(
            short_name=short_name,
            version=version,
            bounding_box=(
                bounding_box.lower_left_lon,
                bounding_box.lower_left_lat,
                bounding_box.upper_right_lon,
                bounding_box.upper_right_lat,
            ),
            temporal=temporal,
        )
    except IndexError:
        # There's no data matching the given parameters.
        logger.error(f"Found no results for {ctx_string}")
        return []

    num_results = len(results)

    if not num_results:
        logger.error(f"Found no results for {ctx_string}")
        return []

    # short_name based subdir for data.
    output_subdir = output_dir / short_name
    logger.info(
        f"Found {num_results} granules for {ctx_string}."
        f" Downloading to {output_subdir}."
    )

    output_subdir.mkdir(exist_ok=True)
    downloaded_files = earthaccess.download(results, str(output_subdir))
    downloaded_filepaths = [Path(filepath_str) for filepath_str in downloaded_files]
    # There may be duplicate filepaths returned by earthaccess because of data
    # existing both in the cloud and on ECS.
    downloaded_filepaths = list(set(downloaded_filepaths))

    return downloaded_filepaths
