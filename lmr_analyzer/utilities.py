__author__ = "Guilherme Fernandes Alves"

from math import radians, cos, sin, asin, sqrt
import osmnx as ox
import networkx as nx
import googlemaps

# Distances calculations


def Haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
        Calculate the great circle distance between two points 
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
        # convert decimal degrees to radians 
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
        # haversine formula 
    # haversine formula
    dlon = lon2 - lon1
        dlon = lon2 - lon1 
    dlon = lon2 - lon1
    dlat = lat2 - lat1
        dlat = lat2 - lat1 
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
        c = 2 * asin(sqrt(a)) 
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km


def drive_distance_gmaps(origin, destination):

    # TODO: parametrize key
    gmaps = googlemaps.Client(key="AIzaSyC9B4JfZMhjWd4v4q4kz1G6eY0l0j8KfYU")
    directions_result = gmaps.directions(origin, destination, mode="driving")
    return directions_result[0]["legs"][0]["distance"]["value"]



    # def drive_distance_osrm(origin, destination):
    #     import requests
    #     import json

    #     url = 'http://router.project-osrm.org/route/v1/driving/'
    #     url += str(origin[1]) + ',' + str(origin[0]) + ';' + str(destination[1]) + ',' + str(destination[0])
    #     url += '?overview=false&steps=true&geometries=geojson'
    #     response = requests.get(url)
    #     data = json.loads(response.text)
    #     return data['routes'][0]['legs'][0]['distance']


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
        """    
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
