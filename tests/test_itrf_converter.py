from __future__ import annotations

import os
import time

import pandas as pd
import pytest

from iceflow.itrf.converter import _datetime_to_decimal_year, transform_itrf


def test_transform_itrf():
    synth_df = pd.DataFrame(
        {
            # Note: duplicate data here because otherwise a deprecation warning
            # error about single-value series is raised from pandas' internals,
            # and pytest complains.
            "latitude": [70, 70],
            "longitude": [-50, -50],
            "elevation": [1, 1],
            "ITRF": ["ITRF93", "ITRF93"],
        },
    )

    constant_datetime = pd.to_datetime("1993-07-02 12:00:00")
    synth_df.index = pd.Index([constant_datetime] * 2, name="utc_datetime")

    result = transform_itrf(
        data=synth_df,
        target_itrf="ITRF2014",
    )

    # Before and after values were extracted from the synthetic dataset in the
    # ITRF corrections notebook put together by Kevin. See:
    # https://github.com/nsidc/NSIDC-Data-Tutorials/blob/a35203f18841456d258fac3a11dc04f44f839d9d/notebooks/iceflow/corrections.ipynb
    assert result.latitude.to_numpy()[0] == 69.99999974953995
    assert result.longitude.to_numpy()[0] == -50.0000001319163
    assert result.elevation.to_numpy()[0] == 1.0052761882543564


@pytest.mark.parametrize("timezone", ["America/Denver", "UTC"])
def test__datetime_to_decimal_year(timezone):
    os.environ["TZ"] = timezone
    time.tzset()
    result = _datetime_to_decimal_year(pd.to_datetime("1993-07-02 12:00:00"))
    assert result == 1993.5
