import warnings
from math import asin, cos, radians, sin, sqrt
from typing import Tuple

import networkx as nx
import osmnx as ox
import requests

# Distances calculations


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates the great circle distance between two points on Earth (specified
    in decimal degrees). Returns the distance between the two points in km.
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    d_lon = lon2 - lon1
    d_lat = lat2 - lat1
    a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371 km
    return 6371 * c


def drive_distance_gmaps(
    origin: Tuple[float, float],  # lat, lon
    destination: Tuple[float, float],  # lat, lon
    gmaps_api_key: str,  # Google Maps API key
) -> Tuple[float, float]:
    """Calculate the driving distance between two points using Google Maps API.
    Internet connection is required. The Google Maps API key must be passed.
    """
    # TODO: Test gmaps API!

    # Create the coordinates string
    origin_coordinates = f"{origin[0]},{origin[1]}"
    destination_coordinates = f"{destination[0]},{destination[1]}"

    # Create the request URL
    url = (
        "https://maps.googleapis.com/maps/api/directions/json?origin="
        f"{origin_coordinates}&destination={destination_coordinates}&key={gmaps_api_key}"
    )

    # Make the request
    response = requests.get(url)

    if response.status_code != 200:
        raise RuntimeError("Request failed")

    # Get the response
    data = response.json()

    if data["status"] != "OK":
        raise RuntimeError("Request failed")

    # Get the distance and duration
    distance_km = data["routes"][0]["legs"][0]["distance"]["value"] / 1000
    duration_min = data["routes"][0]["legs"][0]["duration"]["value"] / 60
    # TODO: check if this is really in minutes

    return (distance_km, duration_min)


def drive_distance_osm(
    origin: Tuple[float, float],
    destination: Tuple[float, float],
    session: requests.Session = None,
) -> Tuple[float, float]:
    """Calculate the driving distance between two points using OSM API.
    Internet connection is required.

    session : requests.Session
        The session to be used to make the request. If None, a new session will
        be created. This can be used to reuse the same session for multiple
        requests, which can impact performance.
    """

    lon1, lat1 = origin
    lon2, lat2 = destination
    coordinates = f"{lon1},{lat1};{lon2},{lat2}"

    # Get the driving distance from the OpenStreetMaps API
    url = f"http://router.project-osrm.org/route/v1/driving/{coordinates}"
    if session is None:
        session = requests.Session()
    r = session.get(url)
    res = r.json()

    # Check if the route was properly found, raise a warning otherwise
    if res["code"] != "Ok":
        warnings.warn(
            f"OSM API returned an {res['code']} error when calculating the "
            f"following distance: from {origin} to {destination}"
        )

    duration_min = res["routes"][0]["duration"] / 60  # in minutes
    distance_km = res["routes"][0]["distance"] / 1000  # in km

    return (distance_km, duration_min)


def drive_distance_osmnx(
    origin: tuple[float, float],  # lat, lon
    destination: tuple[float, float],  # lat, lon
) -> float:
    """Calculate the driving distance between two points using OSMnx."""
    # TODO: allow receiving stop objects

    if not isinstance(origin, tuple) or not isinstance(destination, tuple):
        raise TypeError("The origin and destination must be tuple types.")

    # Define the bounding box of the area of interest
    north = max(origin[0], destination[0])
    south = min(origin[0], destination[0])
    east = max(origin[1], destination[1])
    west = min(origin[1], destination[1])

    # Modify the bounding box if the distance between the points is too small
    if abs(north - south) < 0.01:
        north += 0.005
        south -= 0.005
    if abs(east - west) < 0.01:
        east += 0.005
        west -= 0.005

    # Get the graph for the area of interest
    graph = ox.graph_from_bbox(
        north=north, south=south, east=east, west=west, network_type="drive"
    )

    # Get the nearest nodes to the origin and destination points
    origin_node = ox.distance.nearest_nodes(graph, origin[1], origin[0])
    destination_node = ox.distance.nearest_nodes(graph, destination[1], destination[0])

    # Get the shortest path between the origin and destination nodes
    route_length = nx.shortest_path_length(
        graph,
        source=origin_node,
        target=destination_node,
        weight="length",
        method="dijkstra",
    )

    # Return the length of the shortest path, in km
    return route_length / 1000  # km


# TODO: Support for Bing API


def get_distance(
    location1: Tuple[float, float],
    location2: Tuple[float, float],
    mode="haversine",
    session: requests.Session = None,
):
    """Calculate the distance between two points. It supports five different
    distance calculation methods: "haversine", "gmaps", "osm" or "osmnx".
    Some of these methods were not extensively tested, so use them with caution.

    Parameters
    ----------
    location1 : tuple
        The coordinates of the first location. The coordinates must be in the form (lat, lon).
    location2 : tuple
        The coordinates of the second location. The coordinates must be in the form (lat, lon).
    mode : string
        Distance calculation mode. The mode must be one of the following:
        'haversine', 'gmaps', 'osmnx'.

    Returns
    -------
    (distance, duration): tuple
        The distance and duration of the path between the origin and destination
        points. The distance is in kilometers and the duration is in minutes.
        The duration is only available for the 'gmaps', or 'osm' modes.
        Otherwise, the duration is set to None.
    """
    match mode:
        case "haversine":
            return (
                haversine(location1[0], location1[1], location2[0], location2[1]),
                0,
            )
        case "osm":
            return drive_distance_osm(location1, location2, session)
        case "osmnx":
            return (drive_distance_osmnx(location1, location2), 0)
        case "gmaps":
            return drive_distance_gmaps(location1, location2, gmaps_api_key="")
        case _:
            raise ValueError(
                "Invalid mode, please choose one of the following: "
                "haversine, gmaps, osm or osmnx"
            )


# Auxiliary functions


def get_city_state_names(
    location: Tuple[float, float], session=None
) -> Tuple[str, str]:
    """Get the city and state names from a location. The location must be a
    tuple with the coordinates (lat, lon). The method uses the nominatim API
    from OpenStreetMaps.
    """
    lat, lon = location
    url = (
        f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}"
    )
    if session is None:
        session = requests.Session()
    r = session.get(url)
    res = r.json()

    try:
        city = res["address"]["city"]
    except KeyError:
        city = res["address"]["county"]
    state = res["address"]["state"]

    return (city, state)
