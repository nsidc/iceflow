from __future__ import annotations

from pathlib import Path

import earthaccess
import pydantic
from loguru import logger

from nsidc.iceflow.data.models import (
    Dataset,
    IceflowSearchResult,
    IceflowSearchResults,
)
from nsidc.iceflow.data.supported_datasets import ALL_SUPPORTED_DATASETS


def _find_iceflow_data_for_dataset(
    *,
    dataset: Dataset,
    **search_kwargs,
) -> IceflowSearchResult:
    earthaccess.login()

    ctx_string = f"{dataset.short_name=} {dataset.version=} with {search_kwargs=}"

    try:
        granules_list = earthaccess.search_data(
            short_name=dataset.short_name,
            version=dataset.version,
            # Select only cloud-hosted granules. Without specifying cloud vs
            # non-cloud, we may get duplicate granules as long as the ECS copy
            # remains.
            cloud_hosted=True,
            **search_kwargs,
        )
    except IndexError:
        # There's no data matching the given parameters.
        granules_list = []

    num_results = len(granules_list)

    if not num_results:
        logger.warning(f"Found no results for {ctx_string}")
        granules_list = []

    iceflow_search_result = IceflowSearchResult(dataset=dataset, granules=granules_list)
    return iceflow_search_result


def _download_iceflow_search_result(
    *,
    iceflow_search_result: IceflowSearchResult,
    output_dir: Path,
) -> list[Path]:
    # No granules found for this search result object.
    if not iceflow_search_result.granules:
        return []
    # short_name and version-based subdir for data.
    subdir_name = f"{iceflow_search_result.dataset.short_name}_{iceflow_search_result.dataset.version}"
    output_subdir = output_dir / subdir_name

    logger.info(
        f"Downloading {len(iceflow_search_result.granules)} granules"
        f" (approx. {iceflow_search_result.total_size_mb} MB)"
        f" to {output_subdir}."
    )

    output_subdir.mkdir(exist_ok=True)
    downloaded_files = earthaccess.download(
        iceflow_search_result.granules, str(output_subdir)
    )
    downloaded_filepaths = [Path(filepath_str) for filepath_str in downloaded_files]
    # There may be duplicate filepaths returned by earthaccess because of data
    # existing both in the cloud and on ECS.
    downloaded_filepaths = list(set(downloaded_filepaths))

    return downloaded_filepaths


@pydantic.validate_call()
def find_iceflow_data(
    *,
    datasets: list[Dataset] = ALL_SUPPORTED_DATASETS,
    **search_kwargs,
) -> IceflowSearchResults:
    """Find iceflow-compatible data using search kwargs.

    `search_kwargs` are passed to `earthaccess.search_data`, allowing for
    CMR-supported filters (see
    https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html)
    """
    iceflow_search_results = []
    for dataset in datasets:
        iceflow_search_result = _find_iceflow_data_for_dataset(
            dataset=dataset,
            **search_kwargs,
        )
        iceflow_search_results.append(iceflow_search_result)

    return iceflow_search_results


def download_iceflow_results(
    iceflow_search_results: IceflowSearchResults,
    output_dir: Path,
) -> list[Path]:
    all_downloaded_files = []
    for iceflow_search_result in iceflow_search_results:
        downloaded_filepaths = _download_iceflow_search_result(
            iceflow_search_result=iceflow_search_result,
            output_dir=output_dir,
        )
        all_downloaded_files.extend(downloaded_filepaths)

    return all_downloaded_files
