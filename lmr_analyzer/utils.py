"""The utils.py module contains auxiliary functions that are used by other
modules of the lmr_analyzer package.
"""
import warnings
from math import asin, cos, radians, sin, sqrt
from typing import Optional, Tuple

import networkx as nx
import osmnx as ox
import requests
from requests import Session

# Distances calculations


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points
    on the Earth (specified in decimal degrees)

    Parameters
    ----------
    lat1 : float
        Latitude of the first point.
    lon1 : float
        Longitude of the first point.
    lat2 : float
        Latitude of the second point.
    lon2 : float
        Longitude of the second point.

    Returns
    -------
    distance : float
        The distance between the two points in kilometers.

    Notes
    -----
    The Earth here is assumed to be perfectly spherical, with a radius of
    6371 km. This is not the most accurate model, but it is good enough for
    most applications.
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    d_lon = lon2 - lon1
    d_lat = lat2 - lat1
    a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km


def drive_distance_gmaps(origin, destination, api_key=None):
    """Calculate the driving distance between two points using Google Maps API.
    Internet connection is required. The Google Maps API key must be passed.


    Parameters
    ----------
    origin : tuple
        The origin point coordinates. The coordinates must be in the form (lat, lon).
    destination : tuple
        The destination point coordinates. The coordinates must be in the form (lat, lon).
    api_key : string
        The Google Maps API key. It can be obtained at
        https://developers.google.com/maps/documentation/directions/get-api-key
        and it is free, but it has a daily limit of 2500 requests and, of course,
        it is limited to 1 person only.

    Returns
    -------
    (distance, durante) : tuple
        The distance and duration of the shortest path between the origin and destination points.
    """
    # TODO: Test gmaps API!

    # Create the coordinates string
    origin_coordinates = f"{origin[0]},{origin[1]}"
    destination_coordinates = f"{destination[0]},{destination[1]}"

    # Create the request URL
    url = (
        "https://maps.googleapis.com/maps/api/directions/json?origin="
        + f"{origin_coordinates}&destination={destination_coordinates}&key={api_key}"
    )

    # Make the request
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception("Request failed")  # pylint: disable=broad-exception-raised

    # Get the response
    data = response.json()

    # Check if the request was successful
    if data["status"] != "OK":
        raise Exception("Request failed")  # pylint: disable=broad-exception-raised

    # Get the distance and duration
    distance = data["routes"][0]["legs"][0]["distance"]["value"] / 1000
    duration = data["routes"][0]["legs"][0]["duration"]["value"] / 60

    return (distance, duration)


def drive_distance_osm(
    origin: Tuple[float, float],
    destination: Tuple[float, float],
    session: Session = None,
) -> Tuple[float, float]:
    """Calculate the driving distance between two points using OSM API.
    Internet connection is required.

    Parameters
    ----------
    origin : tuple
        The origin point coordinates. The coordinates must be as (lat, lon).
    destination : tuple
        The destination point coordinates. The coordinates must be as (lat, lon).
    session : requests.Session
        The session to be used to make the request. If None, a new session will
        be created. This can be used to reuse the same session for multiple
        requests, which can impact performance.

    Returns
    -------
    (distance, duration) : tuple
        The distance and duration of the shortest path between the origin and
        destination points. The distance is in meters and the duration is in minutes.
    """
    # Create the coordinates string
    # coordinates: "lon1,lat1,lon2,lat2"
    coordinates = f"{origin[1]},{ origin[0]};{destination[1]},{destination[0]}"

    # Get the driving distance from the OpenStreetMaps API
    url = f"http://router.project-osrm.org/route/v1/driving/{coordinates}"
    if session is None:
        session = requests.Session()
    r = session.get(url)
    res = r.json()

    # Check if the route was properly found, raise an error if not
    if res["code"] != "Ok":
        warnings.warn(
            f"OSM API returned an {res['code']} error when calculating the "
            + f"following distance: from {origin} to {destination}"
        )

    # Get the route length and duration and convert to km and minutes
    duration = res["routes"][0]["duration"] / 60  # in minutes
    distance = res["routes"][0]["distance"] / 1000  # in km

    return (distance, duration)


def drive_distance_osmnx(
    origin: Tuple[float, float], destination: Tuple[float, float]
) -> float:
    """Calculate the driving distance between two points using OSMnx.

    Parameters
    ----------
    origin : tuple
        The origin point coordinates. The coordinates must be in the form (lat, lon).
    destination : tuple
        The destination point coordinates. The coordinates must be in the form (lat, lon).

    Returns
    -------
    route_length: float
        The length of the shortest path between the origin and destination points.
    """
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
    return route_length / 1000


def drive_distance_bing(
    origin: Tuple[float, float], destination: Tuple[float, float]
) -> Tuple[float, float]:
    """Calculate the driving distance between two points using Bing Maps API.
    Internet connection is required.
    """
    # TODO: implement Bing Maps API
    origin = origin
    destination = destination
    print("The Bing Maps support is not implemented yet.")


def get_distance(
    location1: Tuple[float, float],
    location2: Tuple[float, float],
    mode: str = "haversine",
    session: Optional[Session] = None,
) -> Tuple[float, Optional[float]]:
    """Calculate the distance between two points. It supports five different
    calculation methods: "haversine", "gmaps", "osm", "osmnx" and "bing".

    Parameters
    ----------
    location1 : tuple
        The coordinates of the first location. The coordinates must be in the
        form (lat, lon).
    location2 : tuple
        The coordinates of the second location. The coordinates must be in the
        form (lat, lon).
    mode : string
        Distance calculation mode. The mode must be one of the following:
        'haversine', 'gmaps', 'osmnx', 'bing'.
    session : requests.Session
        The session to be used to make the request. If None, a new session will
        be created. This can be used to reuse the same session for multiple
        requests, which can impact performance.

    Returns
    -------
    (distance, duration): tuple
        The distance and duration of the path between the origin and destination
        points. The distance is in kilometers and the duration is in minutes.
        The duration is only available for the 'gmaps', 'osm', and 'bing' modes.
        Otherwise, the duration is set to None.

    Notes
    -----
    Some of these methods were not extensively tested yet (Dec 2023), so use
    them with caution.
    """
    if mode.lower() == "haversine":
        return (haversine(location1[0], location1[1], location2[0], location2[1]), 0)
    elif mode.lower() == "osm":
        return drive_distance_osm(location1, location2, session)
    elif mode.lower() == "osmnx":
        return (drive_distance_osmnx(location1, location2), 0)
    elif mode.lower() == "gmaps":
        return drive_distance_gmaps(location1, location2)
    elif mode.lower() == "bing":
        return drive_distance_bing(location1, location2)
    else:
        raise ValueError(
            "Invalid mode, please choose one of the following: "
            + "haversine, gmaps, osm, osmnx, bing"
        )


# Auxiliary functions


def get_city_state_names(
    location: Tuple[float, float], session: Optional[requests.Session] = None
) -> Tuple[str, str]:
    """Get the city and state names from a location. The location must be a
    tuple with the coordinates (lat, lon). The method uses the nominatim API
    from OpenStreetMaps.

    Parameters
    ----------
    location : tuple
        The coordinates of the location. The coordinates must be in the form (lat, lon).
    session : requests.Session
        The session to be used to make the request. If None, a new session will
        be created. This can be used to reuse the same session for multiple
        requests, which can impact performance.

    Returns
    -------
    (city, state) : tuple
        The city and state names of the location. Each parameter is a string.
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
