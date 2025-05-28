from __future__ import annotations

import pandas as pd
import pandera as pa
import pytest

from nsidc.iceflow.data.models import BoundingBox, IceflowDataFrame

_mock_bad_df = pd.DataFrame(
    {
        "latitude": [70],
        "longitude": [-50],
        "elevation": [1],
        "ITRF": ["should fail"],
    },
)


def test_iceflowdataframe():
    with pytest.raises(pa.errors.SchemaError):
        IceflowDataFrame(_mock_bad_df)


@pa.check_types
def _pa_check_in(_df: IceflowDataFrame) -> None:
    return None


def test_pa_check_in():
    with pytest.raises(pa.errors.SchemaError):
        # The type ignore on the next line tells mypy to ignore that we're not
        # casting to the expected input type. We want to test that
        # `check_types` raises a runtime validation error
        _pa_check_in(_mock_bad_df)  # type: ignore[arg-type]


@pa.check_types
def _pa_check_out(df: pd.DataFrame) -> IceflowDataFrame:
    # The type ignore on the next line tells mypy to ignore that we're not
    # casting to the expected return type. We want to test that
    # `check_types` raises a runtime validation error
    return df  # type: ignore[return-value]


def test_pa_check_out():
    with pytest.raises(pa.errors.SchemaError):
        _pa_check_out(_mock_bad_df)


def test_bounding_box():
    bbox_with_kwargs = BoundingBox(
        lower_left_lon=-103.125559,
        lower_left_lat=-75.180563,
        upper_right_lon=-102.677327,
        upper_right_lat=-74.798063,
    )

    bbox_with_args = BoundingBox(
        -103.125559,
        -75.180563,
        -102.677327,
        -74.798063,
    )

    bbox_with_list = BoundingBox(
        [
            -103.125559,
            -75.180563,
            -102.677327,
            -74.798063,
        ]
    )

    assert bbox_with_kwargs == bbox_with_args
    assert bbox_with_kwargs == bbox_with_list

    bbox = bbox_with_kwargs

    # Access via named values
    assert bbox.lower_left_lon == -103.125559
    assert bbox.lower_left_lat == -75.180563
    assert bbox.upper_right_lon == -102.677327
    assert bbox.upper_right_lat == -74.798063

    # Access as a list/tuple
    assert list(bbox) == [-103.125559, -75.180563, -102.677327, -74.798063]
    assert tuple(bbox) == (-103.125559, -75.180563, -102.677327, -74.798063)

    # Access via index
    assert bbox[0] == -103.125559
    assert bbox[1] == -75.180563
    assert bbox[2] == -102.677327
    assert bbox[3] == -74.798063

    # Access via name
    assert bbox["lower_left_lon"] == -103.125559
    assert bbox["lower_left_lat"] == -75.180563
    assert bbox["upper_right_lon"] == -102.677327
    assert bbox["upper_right_lat"] == -74.798063
