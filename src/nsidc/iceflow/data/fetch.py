from __future__ import annotations

import datetime as dt
from pathlib import Path

import earthaccess
from loguru import logger

from nsidc.iceflow.data.models import BoundingBox, Dataset, IceflowSearchResult


def _find_iceflow_data(
    *,
    dataset: Dataset,
    bounding_box: BoundingBox,
    temporal: tuple[dt.datetime | dt.date, dt.datetime | dt.date],
) -> IceflowSearchResult:
    earthaccess.login()

    ctx_string = (
        f"{dataset.short_name=} {dataset.version=} with {bounding_box=} {temporal=}"
    )

    try:
        granules_list = earthaccess.search_data(
            short_name=dataset.short_name,
            version=dataset.version,
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
        granules_list = []

    num_results = len(granules_list)

    if not num_results:
        logger.error(f"Found no results for {ctx_string}")
        granules_list = []

    iceflow_search_result = IceflowSearchResult(dataset=dataset, granules=granules_list)
    return iceflow_search_result


def _download_iceflow_results(
    *, iceflow_results: IceflowSearchResult, output_dir: Path
) -> list[Path]:
    # short_name based subdir for data.
    output_subdir = output_dir / iceflow_results.dataset.short_name
    logger.info(
        f"Downloading {len(iceflow_results.granules)} granules" f" to {output_subdir}."
    )

    output_subdir.mkdir(exist_ok=True)
    downloaded_files = earthaccess.download(
        iceflow_results.granules, str(output_subdir)
    )
    downloaded_filepaths = [Path(filepath_str) for filepath_str in downloaded_files]
    # There may be duplicate filepaths returned by earthaccess because of data
    # existing both in the cloud and on ECS.
    downloaded_filepaths = list(set(downloaded_filepaths))

    return downloaded_filepaths


def search_and_download(
    *,
    dataset: Dataset,
    bounding_box: BoundingBox,
    temporal: tuple[dt.datetime | dt.date, dt.datetime | dt.date],
    output_dir: Path,
) -> list[Path]:
    """Search and download data.

    Wraps EDL auth and CMR search using `earthaccess`.

    Data matching the given parameters are downloaded to a subfolder of the
    given `output_dir` named after the `short_name`.
    """
    iceflow_results = _find_iceflow_data(
        dataset=dataset,
        bounding_box=bounding_box,
        temporal=temporal,
    )

    downloaded_filepaths = _download_iceflow_results(
        iceflow_results=iceflow_results, output_dir=output_dir
    )

    return downloaded_filepaths
