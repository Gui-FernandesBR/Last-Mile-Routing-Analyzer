import pytest

from lmr_analyzer.utils import haversine


class TestHaversine:
    def test_haversine_same_point(self):
        assert haversine(0, 0, 0, 0) == 0

    def test_haversine_known_distance(self):
        # Distance between New York City (40.7128° N, 74.0060° W) and Los Angeles (34.0522° N, 118.2437° W)
        nyc_lat, nyc_lon = 40.7128, -74.0060
        la_lat, la_lon = 34.0522, -118.2437
        expected_distance = 3940  # Approximate distance in km
        assert (
            pytest.approx(haversine(nyc_lat, nyc_lon, la_lat, la_lon), 0.1)
            == expected_distance
        )

    def test_haversine_equator(self):
        # Distance between two points on the equator
        assert pytest.approx(haversine(0, 0, 0, 1), 0.1) == 111.32

    def test_haversine_poles(self):
        # Distance between the North Pole and the South Pole
        assert pytest.approx(haversine(90, 0, -90, 0), 0.1) == 20015
