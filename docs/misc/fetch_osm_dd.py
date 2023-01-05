import csv
import time

import requests

# This file is used to fetch the distance between the points using the OSM API
# It was used to create the drive distances that are available in the
# data/driving_distances folder of the LMR repository


# Initialize a new session
session = requests.Session()

# Get the data from the API
def drive_distance_osm(origin, destination, i, n):
    """Calculate the driving distance between two points using OSM API.
    Internet connection is required.

    Parameters
    ----------
    origin : tuple
        The origin point coordinates. The coordinates must be in the form (lat, lon).
    destination : tuple
        The destination point coordinates. The coordinates must be in the form (lat, lon).
    session : requests.Session
        The session to be used to make the request. If None, a new session will be created. This can be used to reuse the same session for multiple requests, which can impact performance.

    Returns
    -------
    (distance, duration) : tuple
        The distance and duration of the shortest path between the origin and destination points.
        The distance is in meters and the duration is in minutes.
    """

    start = time.time()

    # Create the coordinates string
    coordinates = "{},{};{},{}".format(
        origin[1], origin[0], destination[1], destination[0]
    )  # lon1, lat1, lon2, lat2

    # Get the driving distance from the OpenStreetMaps API
    url = "http://router.project-osrm.org/route/v1/driving/{}".format(coordinates)
    res = session.get(url).json()

    # Check if the route was properly found, raise an error if not
    if res["code"] != "Ok":
        save_results(data, main_file)
        raise ValueError(
            f"Route not found. OSM API returned an error when calculating the following distance: from {origin} to {destination}"
        )
    # Get the route length and duration and convert to km and minutes, respectively
    duration = res["routes"][0]["duration"] / 60  # in minutes
    distance = res["routes"][0]["distance"] / 1000  # in km
    # geometry = polyline.decode(res["routes"][0]["geometry"])

    # Return a tuple with the route length and duration
    end = time.time()
    print(
        "{} of {} ({:.2f}%) completed. OSM API request took {:.2f} s to catch driving distance from ({:.6f}, {:.6f}) to ({:.6f}, {:.6f}) ".format(
            i,
            n,
            100 * i / n,
            end - start,
            float(origin[0]),
            float(origin[1]),
            float(destination[0]),
            float(destination[1]),
        )
    )
    return (distance, duration)


# Open the file with the coordinates
def read_coord_file(filename):
    with open(filename, "r") as f:
        data = list(csv.reader(f))
    f.close()
    return data


# Calculate the distance and duration between the points
def calculate_distance_duration(data, n):
    """_summary_

    Parameters
    ----------
    data : _type_
        _description_
    n : int
        Number of lines to be processed

    Returns
    -------
    _type_
        _description_
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


# Save the results to a file
def save_results(data, filename):
    with open(filename, "w") as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerows(data)
    f.close()
    return None


if __name__ == "__main__":
    main_start = time.time()
    main_file = "Austin.csv"
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
