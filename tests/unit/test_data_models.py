from __future__ import annotations

import pandas as pd
import pandera as pa
import pytest

from nsidc.iceflow.data.models import IceflowDataFrame

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
