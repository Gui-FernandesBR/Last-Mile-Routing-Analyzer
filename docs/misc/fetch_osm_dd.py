"""
This file is used to fetch the distance between the points using the OSM API.
It was used to create the drive distances that are available in the
data/driving_distances folder of the LMR repository
"""

import csv
import time
from typing import Tuple

import requests

SESSION = requests.Session()


def drive_distance_osm(
    origin: Tuple[float, float],  # lat, lon
    destination: Tuple[float, float],  # lat, lon
    i: int,
    n: int,
) -> Tuple[float, float]:  # distance, duration
    """Calculate the driving distance between two points using OSM API.
    Internet connection is required.

    Parameters
    ----------
    origin : The coordinates must be as (lat, lon).
    destination : The coordinates must be as (lat, lon).
    session : The session to be used to make the request. If None, a new session
        will be created. This can be used to reuse the same session for multiple
        requests, which can impact performance.
    i : The index of the current line being processed.
    n : The total number of lines to be processed.

    Returns
    -------
    (distance, duration) : Tuple[float, float]
        The distance and duration of the shortest path between the origin and
        destination points. The distance is in meters and the duration is in
        minutes.
    """

    start = time.time()

    # Create the coordinates string
    coordinates = "{},{};{},{}".format(
        origin[1], origin[0], destination[1], destination[0]
    )  # lon1, lat1, lon2, lat2

    # Get the driving distance from the OpenStreetMaps API
    url = f"http://router.project-osrm.org/route/v1/driving/{coordinates}"
    res = SESSION.get(url).json()

    # Check if the route was properly found, raise an error if not
    if res["code"] != "Ok":
        save_results(data, main_file)
        raise ValueError(
            "Route not found. OSM API returned an error when calculating the "
            f"following distance: from {origin} to {destination}"
        )
    # Get the route length and duration and convert to km and minutes, respectively
    duration = res["routes"][0]["duration"] / 60  # in minutes
    distance = res["routes"][0]["distance"] / 1000  # in km
    # geometry = polyline.decode(res["routes"][0]["geometry"])

    end = time.time()
    print(
        f"{i} of {n} ({100 * i / n:.2f}%) completed. "
        f"OSM API request took {end - start:.2f} s to catch driving distance from "
        f"({origin[0]:.6f}, {origin[1]:.6f}) to ({destination[0]:.6f}, {destination[1]:.6f})"
    )
    # Return a tuple with the route length and duration
    return (distance, duration)


def read_coord_file(filename):
    """Open the file with the coordinates"""
    with open(filename, "r") as f:
        data = list(csv.reader(f))
    f.close()
    return data


def calculate_distance_duration(
    data: dict,
    n: int,
) -> dict:
    """Calculate the distance and duration between the points

    Parameters
    ----------
    data : __description__
    n : Number of lines to be processed
    """
    route = data[1][0]
    route_begin_index = 1
    for i in range(1, n, 1):
        # Skip to those that already were calculated
        if data[i][4] != "-":
            print(
                "{:.1f}% completed. The current line was already evaluated".format(
                    i / n * 100
                )
            )
            route_begin_index = i
            continue

        if data[i + 1][0] == route:
            origin = (float(data[i][2]), float(data[i][3]))
            destination = (float(data[i + 1][2]), float(data[i + 1][3]))
            distance, duration = drive_distance_osm(origin, destination, i, n)
            data[i][4] = round(distance, 3)
            data[i][5] = round(duration, 0)
        else:
            route = data[i + 1][0]
            origin = (data[i][2], data[i][3])
            destination = (data[route_begin_index][2], data[route_begin_index][3])
            distance, duration = drive_distance_osm(origin, destination, i, n)
            data[i][4] = round(distance, 3)
            data[i][5] = round(duration, 0)
            route_begin_index = i + 1
        # print("Progress: {:.1f}%".format((i / n) * 100))

    return data


def save_results(data, filename):
    """Save the results to a file"""
    with open(filename, "w") as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerows(data)
    f.close()
    return None


if __name__ == "__main__":
    main_start = time.time()
    main_file = "./data/driving_distances/austin.csv"
    number_of_lines = 31273  # The number of lines to be processed
    data = read_coord_file(filename=main_file)

    try:
        data = calculate_distance_duration(data, number_of_lines)
        save_results(data, filename=main_file)
        main_end = time.time()
        print(
            "You're awesome, all the {} lines were filled in a total time of: {:.3f} s or {:.3f} min or {:.3f}".format(
                number_of_lines,
                main_end - main_start,
                (main_end - main_start) / 60,
                (main_end - main_start) / 3600,
            )
        )
    except KeyboardInterrupt:
        print("Something happened :( , please check: ")
        save_results(data, filename=main_file)
        main_end = time.time()
        print(
            "All the {} lines were filled in a total time of: {:.3f} s or {:.3f} min or {:.3f} hrs".format(
                number_of_lines,
                main_end - main_start,
                (main_end - main_start) / 60,
                (main_end - main_start) / 3600,
            )
        )
