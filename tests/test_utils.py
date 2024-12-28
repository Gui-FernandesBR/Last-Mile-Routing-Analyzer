from unittest.mock import Mock, patch

import pytest
import requests

from lmr_analyzer.utils import drive_distance_osm, get_distance, haversine


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


class TestDriveDistanceOSM:
    @patch("requests.Session.get")
    def test_drive_distance_osm_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": "Ok",
            "routes": [
                {
                    "duration": 3600,  # 1 hour in seconds
                    "distance": 100000,  # 100 km in meters
                }
            ],
        }
        mock_get.return_value = mock_response

        origin = (40.7128, -74.0060)  # New York City
        destination = (34.0522, -118.2437)  # Los Angeles
        distance, duration = drive_distance_osm(origin, destination)

        assert distance == 100  # 100 km
        assert duration == 60  # 60 minutes

    @patch("requests.Session.get")
    def test_drive_distance_osm_http_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "code": "NoRoute",
            "routes": [],
        }
        mock_get.return_value = mock_response

        origin = (40.7128, -74.0060)  # New York City
        destination = (34.0522, -118.2437)  # Los Angeles

        with pytest.raises(RuntimeError):
            drive_distance_osm(origin, destination)


class TestGetDistance:
    def test_get_distance_haversine(self):
        location1 = (0, 0)
        location2 = (0, 1)
        distance, duration = get_distance(location1, location2, mode="haversine")
        assert pytest.approx(distance, 0.1) == 111.32
        assert duration == 0

    @patch("lmr_analyzer.utils.drive_distance_osm")
    def test_get_distance_osm(self, mock_drive_distance_osm):
        mock_drive_distance_osm.return_value = (100, 60)
        location1 = (40.7128, -74.0060)  # New York City
        location2 = (34.0522, -118.2437)  # Los Angeles
        distance, duration = get_distance(location1, location2, mode="osm")
        assert distance == 100
        assert duration == 60

    @patch("lmr_analyzer.utils.drive_distance_osmnx")
    def test_get_distance_osmnx(self, mock_drive_distance_osmnx):
        mock_drive_distance_osmnx.return_value = 100
        location1 = (40.7128, -74.0060)  # New York City
        location2 = (34.0522, -118.2437)  # Los Angeles
        distance, duration = get_distance(location1, location2, mode="osmnx")
        assert distance == 100
        assert duration == 0

    @patch("lmr_analyzer.utils.drive_distance_gmaps")
    def test_get_distance_gmaps(self, mock_drive_distance_gmaps):
        mock_drive_distance_gmaps.return_value = (100, 60)
        location1 = (40.7128, -74.0060)  # New York City
        location2 = (34.0522, -118.2437)  # Los Angeles
        distance, duration = get_distance(location1, location2, mode="gmaps")
        assert distance == 100
        assert duration == 60

    def test_get_distance_invalid_mode(self):
        location1 = (0, 0)
        location2 = (0, 1)
        with pytest.raises(ValueError):
            get_distance(location1, location2, mode="invalid_mode")
