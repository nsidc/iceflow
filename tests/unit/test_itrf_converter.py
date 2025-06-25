from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from pyproj import Transformer

from nsidc.iceflow.data.models import IceflowDataFrame
from nsidc.iceflow.itrf.converter import (
    _datetime_to_decimal_year,
    _itrf_transformation_step,
    transform_itrf,
)


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
            "dataset": ["foov1", "foov2"],
        },
    )

    constant_datetime = pd.to_datetime("1993-07-02 12:00:00")
    synth_df.index = pd.Index([constant_datetime] * 2, name="utc_datetime")
    synth_iceflow_df = IceflowDataFrame(synth_df)

    result = transform_itrf(
        data=synth_iceflow_df,
        target_itrf="ITRF2014",
    )

    # Before and after values were extracted from the synthetic dataset in the
    # ITRF corrections notebook put together by Kevin. See:
    # ./docs/notebooks/corrections.ipynb
    assert result.latitude.to_numpy()[0] == 69.99999974953995
    assert result.longitude.to_numpy()[0] == -50.0000001319163
    # Rounding to 8 decimals in a field assumed to be measured in meters is 10nm accuracy!
    # This rounding became necessary when pyproj updated to a newer than 3.6.1
    # version, leading to a difference of ~1nm in the resulting calculation.
    assert np.round(result.elevation.to_numpy()[0], 8) == np.round(
        1.0052761882543564, 8
    )


def _itrf_cart_coords_to_wgs84(x, y, z):
    transformer = Transformer.from_pipeline("+proj=cart +inv +ellps=WGS84")

    lon, lat, elev = transformer.transform(x, y, z)

    return lon, lat, elev


def test_transform_itrf_ectt():
    """Verifies that our transformation code matches the example transformation given by the ECTT.

    The ETRF/ITRF Coordinate Transformation Tool (ECTT)
    (https://doi.org/10.24414/ROB-EUREF-ECTT) provides a web-based interface for
    converting between various ITRF realizations at different epochs.

    See the ECTT here: https://epncb.oma.be/_productsservices/coord_trans/index.php#results

    For this test, use the existing "station_1" example given in the ECTT. Set
    input frame to ITRF93 and Epoch to 1993.0 and set "Transform to" to ITRF2014
    with an Epoch of 1993.0.

    Input:
    # Lines starting by # are treated as comments
    # Fields (in decimal format) should be separated by at least one space
    #
    # --> Example without velocity <--
    # Stationname (no space character) X[m] Y[m] Z[m] :
    Station_1 4027894.006 307045.600 4919474.910

    Results:
    #_Station Frame  Epoch        X[m]          Y[m]          Z[m]    VX[m/yr] VY[m/yr] VZ[m/yr]
    Station_1 ITRF2014 1993.00  4027894.0021   307045.5873  4919474.9151
    """
    # Convert Station 1 initial coordinates, given in ITRF 1993 meters, to
    # WGS84 lat/lon/elev for input into the iceflow conversion function.
    lon, lat, elev = _itrf_cart_coords_to_wgs84(4027894.006, 307045.600, 4919474.910)

    synth_df = pd.DataFrame(
        {
            # Note: duplicate data here because otherwise a deprecation warning
            # error about single-value series is raised from pandas' internals,
            # and pytest complains.
            "longitude": [lon, lon],
            "latitude": [lat, lat],
            "elevation": [elev, elev],
            "ITRF": ["ITRF93", "ITRF93"],
            "dataset": ["foov1", "foov2"],
        },
    )

    constant_datetime = pd.to_datetime("1993-01-01 00:00:00")
    synth_df.index = pd.Index([constant_datetime] * 2, name="utc_datetime")
    synth_iceflow_df = IceflowDataFrame(synth_df)

    result = transform_itrf(
        data=synth_iceflow_df,
        target_itrf="ITRF2014",
    )

    # convert station 1 results in ITRF 2014 meters to WGS84 lat/lon/elev
    expected_lon, expected_lat, expected_elev = _itrf_cart_coords_to_wgs84(
        4027894.0021, 307045.5873, 4919474.9151
    )

    # The results are very close to what we expect with the full pipeline
    assert np.round(result.longitude.to_numpy()[0], 9) == np.round(expected_lon, 9)
    assert np.round(result.latitude.to_numpy()[0], 8) == np.round(expected_lat, 8)
    assert np.round(result.elevation.to_numpy()[0], 4) == np.round(expected_elev, 4)


def test__itrf_transformation_step():
    """Tests that we have the ITRF transformation correct.


    The ETRF/ITRF Coordinate Transformation Tool (ECTT)
    (https://doi.org/10.24414/ROB-EUREF-ECTT) provides a web-based interface for
    converting between various ITRF realizations at different epochs.

    See the ECTT here: https://epncb.oma.be/_productsservices/coord_trans/index.php#results

    For this test, use the existing "station_1" example given in the ECTT. Set
    input frame to ITRF93 and Epoch to 1993.0 and set "Transform to" to ITRF2014
    with an Epoch of 1993.0.

    Input:
    # Lines starting by # are treated as comments
    # Fields (in decimal format) should be separated by at least one space
    #
    # --> Example without velocity <--
    # Stationname (no space character) X[m] Y[m] Z[m] :
    Station_1 4027894.006 307045.600 4919474.910

    Results:
    #_Station Frame  Epoch        X[m]          Y[m]          Z[m]    VX[m/yr] VY[m/yr] VZ[m/yr]
    Station_1 ITRF2014 1993.00  4027894.0021   307045.5873  4919474.9151
    """
    # Input values given to ECTT
    station_1_x = 4027894.006
    station_1_y = 307045.600
    station_1_z = 4919474.910
    station_1_epoch = 1993.0

    transformation_step = _itrf_transformation_step("ITRF93", "ITRF2014")
    transformer = Transformer.from_pipeline("+proj=pipeline " + transformation_step)

    actual_x, actual_y, actual_z, _ = transformer.transform(
        station_1_x, station_1_y, station_1_z, station_1_epoch
    )

    # Exact output values reported by ECTT
    expected_x = 4027894.0021
    expected_y = 307045.5873
    expected_z = 4919474.9151

    assert np.round(actual_x, 4) == expected_x
    assert np.round(actual_y, 4) == expected_y
    assert np.round(actual_z, 4) == expected_z


def test__itrf_transformation_step_failure():
    """Test that the _itrf_transformation_step raises an error if there is no
    pre-defined transform."""

    with pytest.raises(
        RuntimeError, match="Failed to find a pre-defined ITRF transformation"
    ):
        _itrf_transformation_step("ITRF2022", "ITRF93")


def test__itrf_transformation_step_fwd():
    """Test that the forward transform is returned."""
    expected = "+step +init=ITRF2014:ITRF2008"
    actual_step = _itrf_transformation_step("ITRF2014", "ITRF2008")

    assert expected == actual_step


def test__itrf_transformation_step_inv():
    """Test that the forward transform is returned."""
    expected = "+step +inv +init=ITRF2014:ITRF2008"
    actual_step = _itrf_transformation_step("ITRF2008", "ITRF2014")

    assert expected == actual_step


@pytest.mark.parametrize("timezone", ["America/Denver", "UTC"])
def test__datetime_to_decimal_year(timezone, monkeypatch):
    monkeypatch.setenv("TZ", timezone)
    result = _datetime_to_decimal_year(pd.to_datetime("1993-07-02 12:00:00"))
    assert result == 1993.5
