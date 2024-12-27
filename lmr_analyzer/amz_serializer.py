import csv
import json
import time
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pytz

from lmr_analyzer.bbox import BoundingBox
from lmr_analyzer.package import Package
from lmr_analyzer.route import Route
from lmr_analyzer.stop import Stop
from lmr_analyzer.vehicle import Vehicle


class AmazonSerializer:
    """A serializer for the Amazon data. The serializer is used to convert the
    Amazon data into a format that can be used by the LMR algorithm.
    """

    def __init__(self, root_directory: str = None):
        """Initializes the serializer"""
        # TODO: Special case for missing files
        # TODO: Check contents on the directory before loading the data

        self.serialize_all(root_directory)

    def serialize_routes(
        self, routes_dict: dict, packages_dict: dict, bbox_list: list = None
    ):
        """Serializes a route object into a dictionary. The dictionary can be
        used to create a new route object for each route present in the
        routes_dict.

        Parameters
        ----------
        routes_dict : dict
            A dictionary containing the routes to be serialized. The dictionary
            must be in the form ...
        packages_dict : dict
            A dictionary containing the packages to be serialized. The dictionary
            must be in the form ...
        bbox_list : list
            A list containing the bounding boxes to be used in the routes. It
            must be a list of bbox objects.

        Returns
        -------
        routes_dict: dict
            A dictionary containing the serialized routes. The dictionary is
            in the form ...
        """

        self.__initialize_bbox_list(bbox_list)

        for route_id, route in routes_dict.items():
            if isinstance(routes_dict[route_id], Route):
                continue

            for stop_id in routes_dict[route_id]["stops"]:
                if isinstance(routes_dict[route_id]["stops"][stop_id], Stop):
                    continue

                lc_type = routes_dict[route_id]["stops"][stop_id]["type"]
                match lc_type:
                    case "Dropoff":
                        lc_type = "delivery"
                    case "Station":
                        lc_type = "depot"
                    case _:
                        raise ValueError(
                            f"Invalid location type, please check {lc_type}"
                        )

                stop = Stop(
                    name=stop_id,
                    location=(
                        routes_dict[route_id]["stops"][stop_id]["lat"],
                        routes_dict[route_id]["stops"][stop_id]["lng"],
                    ),
                    location_type=lc_type,
                    time_window=(0, 0),
                    packages=packages_dict[route_id][stop_id],
                )

                routes_dict[route_id]["stops"][stop_id] = stop

            vehicle = Vehicle(
                name="vehicle" + str(route_id),
                capacity=routes_dict[route_id]["executor_capacity_cm3"],
            )

            date = [int(x) for x in routes_dict[route_id]["date_YYYY_MM_DD"].split("-")]
            hour = [
                int(x) for x in routes_dict[route_id]["departure_time_utc"].split(":")
            ]
            route = Route(
                name=route_id,
                stops=routes_dict[route_id]["stops"],
                departure_time=datetime(
                    date[0], date[1], date[2], hour[0], hour[1], hour[2], 0, pytz.UTC
                ),
                vehicle=vehicle,
            )

            routes_dict[route_id] = route

        return self.__separate_routes_by_bbox(routes_dict, self.bbox_list)

    def __initialize_bbox_list(self, bbox_list):
        if not bbox_list:
            los_angeles = BoundingBox(
                name="Los Angeles",
                lat1=36,
                lat2=30,
                lon1=-117,
                lon2=-120,
            )

            seattle = BoundingBox(
                name="Seattle",
                lat1=50,
                lat2=46,
                lon1=-124,
                lon2=-120,
            )

            chicago = BoundingBox(
                name="Chicago",
                lat1=41,
                lat2=43,
                lon1=-90,
                lon2=-86,
            )

            boston = BoundingBox(
                name="Boston",
                lat1=41,
                lat2=44,
                lon1=-73,
                lon2=-70,
            )

            austin = BoundingBox(
                name="Austin",
                lat1=31,
                lat2=29,
                lon1=-99,
                lon2=-97,
            )

            # Save the bounding boxes in a list
            self.bbox_list = [los_angeles, seattle, chicago, boston, austin]
        else:
            self.bbox_list = bbox_list

    def __separate_routes_by_bbox(
        self, routes_dict, bbox_list
    ) -> dict[str, dict[str, Route]]:
        """Separates the routes by bounding box. The routes are separated by
        bounding box to reduce the computational cost of the LMR algorithm.

        Warning: Please take care when selecting the bounding boxes. The code
        will not work properly if a route is present in more than one bounding
        box.

        Parameters
        ----------
        bbox_list : list
            A list of bbox objects.

        Returns
        -------
        dict:
            A dictionary containing the routes separated by bounding box. Example:
            new_routes_dict = {
                bbox1: {route1, route2, ...},
                bbox2: {route3, route4, ...},
                ...
            }
        """

        # Create a new dictionary to store the routes separated by bounding box
        new_routes_dict = {i.name: {} for i in bbox_list}

        # Iterate through the routes
        for route_id, route in routes_dict.items():
            # Get the first stop of the route
            stop = route.stops[list(route.stops.keys())[0]]

            # Get the coordinates of the current stop
            lat, lng = stop.location

            # Iterate through the bounding boxes
            for bbox in bbox_list:
                # Check if the current stop is inside the current bounding box
                if (
                    bbox.lat_min <= lat <= bbox.lat_max
                    and bbox.lon_min <= lng <= bbox.lon_max
                ):
                    # Add the route to the new dictionary
                    new_routes_dict[bbox.name][route_id] = route
                    break

        # Return the new dictionary
        # TODO: Understand why I am loosing 12 routes after this step
        return new_routes_dict

    def serialize_actual_sequences(self, actual_sequences) -> dict:
        """Serializes the actual sequences into a dictionary. The dictionary
        can be used to create a new route object for each route present in the
        actual_sequences.

        Parameters
        ----------
        actual_sequences : dict
            A dictionary containing the actual sequences to be serialized. The
            dictionary must be in the form ...

        Returns
        -------
        dict
            A dictionary containing the serialized actual sequences. The
            dictionary is in the form ...
        """
        for route_id, route_dict in actual_sequences.items():
            if isinstance(route_dict, list):
                continue
            for _, ac_dict in route_dict.items():
                sorted_ac_dict = dict(sorted(ac_dict.items(), key=lambda item: item[1]))
                sequence_names = list(sorted_ac_dict.keys())
                actual_sequences[route_id] = sequence_names

        return actual_sequences

    def serialize_all(self, root_directory: str):
        """Serializes all the files in the root directory."""
        start = time.time()

        # Read the package data
        with open(f"{root_directory}/package_data.json", "r") as outfile:
            db_package = json.load(outfile)

        ## Serialize the package data
        self.packages_dict = serialize_packages(packages_dict=db_package.copy())

        ## Calculate the total number of packages
        self.total_packages = 0
        for x in self.packages_dict.keys():
            for y in self.packages_dict[x].keys():
                self.total_packages += len(self.packages_dict[x][y])

        ## Store variables as attributes
        pck_time = time.time()
        print(f"package_data.json has been loaded in {pck_time - start:.2f} seconds.")

        # Read the route data
        with open(f"{root_directory}/route_data.json", "r") as outfile:
            db_route = json.load(outfile)

        ## Serialize the route data
        self.routes_dict = self.serialize_routes(
            routes_dict=db_route.copy(), packages_dict=self.packages_dict
        )

        ## Store variables as attributes
        self.total_routes = len(self.routes_dict)
        route_time = time.time()
        print(
            f"route_data.json has been loaded in {route_time - pck_time:.2f} seconds."
        )

        # Read the actual sequences
        with open(f"{root_directory}/actual_sequences.json", "r") as outfile:
            db_ac_sequences = json.load(outfile)
        ac_sequences_dict = db_ac_sequences.copy()

        ## Serialize the actual sequences
        ac_sequences_dict = self.serialize_actual_sequences(
            actual_sequences=ac_sequences_dict
        )
        ## Modify each route in the routes_dict to include the actual sequence
        for route in self.routes_dict.values():
            route.set_actual_sequence(ac_sequences_dict[route.name])
        ac_sequence_time = time.time()

        print(
            "actual_sequences.json has been loaded in "
            f"{ac_sequence_time - route_time:.2f} seconds."
        )
        print(
            "We are ready to proceed. All files have been loaded in "
            f"{time.time() - start:.2f} seconds."
        )

    def time_history_analysis(self, routes_dict) -> tuple:
        # Hey, I will document this later
        la_times = [
            [r.departure_time, len(r.stops)]
            for r in routes_dict["Los Angeles"].values()
        ]

        boston_times = [
            [r.departure_time, len(r.stops)] for r in routes_dict["Boston"].values()
        ]

        austin_times = [
            [r.departure_time, len(r.stops)] for r in routes_dict["Austin"].values()
        ]

        chicago_times = [
            [r.departure_time, len(r.stops)] for r in routes_dict["Chicago"].values()
        ]

        seattle_times = [
            [r.departure_time, len(r.stops)] for r in routes_dict["Seattle"].values()
        ]

        la_times_by_day = self.__create_times_dict(la_times)
        boston_times_by_day = self.__create_times_dict(boston_times)
        austin_times_by_day = self.__create_times_dict(austin_times)
        chicago_times_by_day = self.__create_times_dict(chicago_times)
        seattle_times_by_day = self.__create_times_dict(seattle_times)

        # Store the time range
        self.time_range: tuple = min(chicago_times_by_day.keys()), max(
            chicago_times_by_day.keys()
        )

        return (
            la_times_by_day,
            boston_times_by_day,
            austin_times_by_day,
            chicago_times_by_day,
            seattle_times_by_day,
        )

    def __create_times_dict(self, times):
        times_by_day = {}
        for t, stops in times:
            day = t.date()
            if day not in times_by_day:
                times_by_day[day] = 0
            times_by_day[day] += stops
        return times_by_day

    def plot_time_analysis(self, routes_dict):
        # Plot the number of stops by day

        plt.figure(figsize=(8, 4))
        plt.bar(routes_dict.keys(), routes_dict.values())
        plt.xticks(rotation=45)
        # plt.xlabel("Day")
        plt.ylabel("Number of deliveries")
        plt.title("Number of deliveries per day in Los Angeles")
        # plt.xlim(min(routes_dict.keys()), max(routes_dict.keys()))
        plt.xlim(datetime(2018, 7, 14), datetime(2018, 9, 1))
        plt.ylim(0, 25000)
        plt.show()
        # plt.savefig(filename, dpi=300)

    def print_info_by_city(self):
        """Prints the number of routes by city."""
        s = 0
        for city, dictionary in self.routes_dict.items():
            print(f"Number of routes in {city:12}: {len(dictionary)}")
            s += len(dictionary)
        print(f"Total number of routes: {s:13}\n")

        # Print the percentage of each city
        for city, dictionary in self.routes_dict.items():
            print(
                f"Percentage of routes in {city:12}: {len(dictionary) / s * 100:.2f}%"
            )

    def print_info(self):
        """Prints the information about the loaded database."""

        # Package Data
        print(
            f"A total of {self.total_packages} packages were loaded from: package_data.json"
        )
        print(f"  (...it considers total of {self.number_of_deliveries} deliveries)")
        print(f"    (...which represents a total of {self.number_of_routes} routes")

        # Route Data
        print(
            f"A total of {len(self.routes_dict)} routes were loaded from route_data.json"
        )

        print("Routes by city:")
        self.print_info_by_city()

    def export_routes_to_csv(
        self, city: str = "Los Angeles", filename="routes.csv"
    ) -> None:

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(
                [
                    "route",
                    "stop",
                    "lat",
                    "lon",
                    "distance_to_next_stop(km)",
                    "duration(min)",
                ]
            )
            # Iterate over routes
            for route in self.routes_dict[city].values():
                for stop in route.actual_sequence:
                    writer.writerow(
                        [
                            route.name,
                            stop.name,
                            stop.location[0],
                            stop.location[1],
                            "-",
                            "-",
                        ]
                    )

    @property
    def number_of_deliveries(self):
        try:
            return np.sum(
                [len(self.packages_dict[x]) for x in self.packages_dict.keys()]
            )
        except AttributeError:
            return None

    @property
    def number_of_routes(self):
        try:
            return len(self.packages_dict.keys())
        except AttributeError:
            return None


def serialize_packages(packages_dict):
    """Serializes a package object into a dictionary. The dictionary can be
    used to create a new package object for each package present in the
    packages_dict.

    Parameters
    ----------
    packages_dict : dict
        A dictionary containing the packages to be serialized. The dictionary
        must be in the form ...

    Returns
    -------
    dict
        A dictionary containing the serialized packages. The dictionary is
        in the form ...
    """

    for route_id in packages_dict:
        for stop_id in packages_dict[route_id]:
            # Iterate through the packages in the current stop
            for package_id, values in packages_dict[route_id][stop_id].items():
                if isinstance(values, Package):
                    continue

                match values["scan_status"]:
                    case "DELIVERED":
                        status = "delivered"
                    case "REJECTED":
                        status = "rejected"
                    case "DELIVERY_ATTEMPTED":
                        status = "attempted"
                    case _:
                        raise ValueError(
                            "Invalid package status. "
                            f"Please check {values['scan_status']}"
                        )

                pck = Package(
                    name=package_id,
                    dimensions=(
                        values["dimensions"]["depth_cm"],
                        values["dimensions"]["height_cm"],
                        values["dimensions"]["width_cm"],
                    ),
                    status=status,
                    weight=0,
                    price=0,
                )

                # Add the package to the package dictionary
                packages_dict[route_id][stop_id][package_id] = pck

    # TODO: Add remaining attributes object:
    # - PackageID_
    # - planned_service_time_seconds
    # - time_window[start_time_utc, end_time_utc]

    return packages_dict
