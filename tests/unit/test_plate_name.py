from __future__ import annotations

import pytest
from shapely.geometry.point import Point

from nsidc.iceflow.itrf.plate_boundaries import plate_name


@pytest.mark.parametrize(
    ("points", "expected_plate_name"),
    [
        (
            [
                Point(-50.00, 70.00),
                Point(-105.00, 40.00),
                Point(0.00, 84.11),
                Point(0.00, 90.00),
                Point(90.00, 86.00),
                Point(180.00, 50.50),
                Point(-90.00, 16.00),
                Point(-45.00, 23.00),
                Point(-15.00, 70.55),
                Point(0.00, 72.05),
                Point(0.00, 80.13),
                Point(-3.00, 80.38),
                Point(-5.00, 83.40),
                Point(0.00, 85.00),
            ],
            "NOAM",
        ),
        (
            [
                Point(10.15, 54.30),
                Point(0.01, 84.10),
                Point(-1.00, 83.40),
                Point(9.00, 75.00),
                Point(-29.99, 51.20),
                Point(-5.00, 37.00),
                Point(37.70, 55.40),
                Point(45.00, 36.50),
                Point(60.00, 25.50),
                Point(69.00, 41.00),
                Point(75.00, 34.00),
                Point(90.00, 27.00),
                Point(100.00, -3.00),
                Point(120.00, -10.00),
                Point(120.00, 80.00),
                Point(45.00, 86.00),
            ],
            "EURA",
        ),
        (
            [
                Point(0.00, -90.00),
                Point(-178, -67),
                Point(-135, -55),
                Point(-90, -42),
                Point(-45, -61),
                Point(-1, -55),
                Point(45, -41),
                Point(90, -46),
                Point(135, -51),
                Point(175, -64),
            ],
            "ANTA",
        ),
    ],
)
def test_plate_name(points, expected_plate_name):
    for point in points:
        assert plate_name(point) == expected_plate_name
