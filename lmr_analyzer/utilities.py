__author__ = "Guilherme Fernandes Alves"

from math import radians, cos, sin, asin, sqrt
import osmnx as ox
import networkx as nx
import googlemaps

# Distances calculations


def Haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km


def drive_distance_gmaps(origin, destination, api_key):
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
    # TODO: Test!

    # Create the coordinates string
    origin_coordinates = "{},{}".format(origin[0], origin[1])
    destination_coordinates = "{},{}".format(destination[0], destination[1])

    # Create the request URL
    url = "https://maps.googleapis.com/maps/api/directions/json?origin={}&destination={}&key={}".format(
        origin_coordinates, destination_coordinates, api_key
    )

    # Make the request
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception("Request failed")

    # Get the response
    data = response.json()

    # Check if the request was successful
    if data["status"] != "OK":
        raise Exception("Request failed")

    # Get the distance and duration
    distance = data["routes"][0]["legs"][0]["distance"]["value"] / 1000
    duration = data["routes"][0]["legs"][0]["duration"]["value"] / 60

    return (distance, duration)


def drive_distance_osm(origin, destination):
    """Calculate the driving distance between two points using OSM API.
    Internet connection is required.

    Parameters
    ----------
    origin : tuple
        The origin point coordinates. The coordinates must be in the form (lat, lon).
    destination : tuple
        The destination point coordinates. The coordinates must be in the form (lat, lon).

    Returns
    -------
    (distance, durante) : tuple
        The distance and duration of the shortest path between the origin and destination points.
        The distance is in meters and the duration is in minutes.
    """

    # Create the coordinates string
    coordinates = "{},{};{},{}".format(
        origin[1], origin[0], destination[1], destination[0]
    )  # lon1, lat1, lon2, lat2

    # Get the driving distance from the OpenStreetMaps API
    url = "http://router.project-osrm.org/route/v1/driving/{}".format(coordinates)
    r = requests.get(url)
    res = r.json()

    # Check if the route was properly found, raise an error if not
    if res["code"] != "Ok":
        warnings.warn(
            "OSM API returned an {} error when calculating the following distance: from {} to {}".format(
                res["code"], origin, destination
            )
        )

    # Get the route length and duration and convert to km and minutes, respectively
    duration = res["routes"][0]["duration"] / 60  # in minutes
    distance = res["routes"][0]["distance"] / 1000  # in km
    # geometry = polyline.decode(res["routes"][0]["geometry"])

    # Return a tuple with the route length and duration
    print(distance)
    return (distance, duration)


def drive_distance_osmnx(origin, destination):
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
    G = ox.graph_from_bbox(
        north=north, south=south, east=east, west=west, network_type="drive"
    )

    # Get the nearest nodes to the origin and destination points
    origin_node = ox.distance.nearest_nodes(G, origin[1], origin[0])
    destination_node = ox.distance.nearest_nodes(G, destination[1], destination[0])

    # Get the shortest path between the origin and destination nodes
    route_length = nx.shortest_path_length(
        G,
        source=origin_node,
        target=destination_node,
        weight="length",
        method="dijkstra",
    )

    # Return the length of the shortest path, in km
    return route_length / 1000


def drive_distance_bing(origin, destination):
    pass


def get_distance(location1, location2, mode="haversine"):
    """_summary_

    Parameters
    ----------
    location1 : _type_
        _description_
    location2 : _type_
        _description_
    mode : string
        Distance calculation mode. The mode must be one of the following:
        'haversine', 'gmaps', 'osmnx', 'bing'.

    Returns
    -------
    _type_
        _description_
    """
    if mode == "haversine":
        return Haversine(location1[0], location1[1], location2[0], location2[1])
    elif mode == "gmaps":
        return drive_distance_gmaps(location1, location2)
    elif mode == "osmnx":
        return drive_distance_osmnx(location1, location2)
    elif mode == "bing":
        return drive_distance_bing(location1, location2)
    else:
        raise ValueError(
            "Invalid mode, please choose one of the following: haversine, gmaps, osmnx, bing"
        )
