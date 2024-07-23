import json
import time
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pytz

from .package import Package
from .route import Route
from .stop import Stop
from .vehicle import Vehicle


class BoundingBox:
    """Auxiliary class to store bounding box information."""

    def __init__(self, name: str, lat1: float, lat2: float, lon1: float, lon2: float):
        """Constructor for the bbox class

        Parameters
        ----------
        name : str
            The name of the bounding box
        lat1 : float
            The minimum latitude of the bounding box
        lon1 : float
            The minimum longitude of the bounding box
        lat2 : float
            The maximum latitude of the bounding box
        lon2 : float
            The maximum longitude of the bounding box
        """
        self.name = name
        self.lat_min = min(lat1, lat2)
        self.lon_min = min(lon1, lon2)
        self.lat_max = max(lat1, lat2)
        self.lon_max = max(lon1, lon2)


class AmazonSerializer:
    """A serializer for the Amazon data. The serializer is used to convert the
    Amazon data into a format that can be used by the LMR algorithm.
    """

    def __init__(self, root_directory: str = None):
        """Initializes the serializer"""
        # TODO: Special case for missing files
        # TODO: Check contents on the directory before loading the data

        self.serialize_all(root_directory)

    @staticmethod
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

                    else:
                        if values["scan_status"] == "DELIVERED":
                            status = "delivered"
                        elif values["scan_status"] == "REJECTED":
                            status = "rejected"
                        elif values["scan_status"] == "DELIVERY_ATTEMPTED":
                            status = "attempted"
                        else:
                            raise ValueError(
                                f"Invalid package status. Please check {values['scan_status']}"
                            )

                        # Create one package object
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

        # 'PackageID_'
        # scan_status
        # time_window[start_time_utc, end_time_utc]
        # planned_service_time_seconds
        # dimensions[depth_cm, height_cm, width_cm]

        # TODO: Add remaining attributes to the package object

        return packages_dict

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

        # Initialize the bounding box list
        if bbox_list is None:
            # Define all the five standard bounding box
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

            chicago = BoundingBox(name="Chicago", lat1=41, lat2=43, lon1=-90, lon2=-86)

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

        for route_id, route in routes_dict.items():
            if isinstance(routes_dict[route_id], Route):
                continue

            for stop_id in routes_dict[route_id]["stops"]:
                if isinstance(routes_dict[route_id]["stops"][stop_id], Stop):
                    continue

                lc_type = routes_dict[route_id]["stops"][stop_id]["type"]
                if lc_type == "Dropoff":
                    lc_type = "delivery"
                elif lc_type == "Station":
                    lc_type = "depot"
                else:
                    raise ValueError(f"Invalid location type, please check {lc_type}")

                stop = Stop(
                    name=stop_id,
                    location=(
                        routes_dict[route_id]["stops"][stop_id]["lat"],
                        routes_dict[route_id]["stops"][stop_id]["lng"],
                    ),
                    location_type=lc_type,
                    time_window=(0, 0),
                    planned_service_time=0,
                    packages=packages_dict[route_id][stop_id],
                )

                routes_dict[route_id]["stops"][stop_id] = stop

            vehicle = Vehicle(
                name="random_vehicle",
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

        # Separate the routes in different bounding boxes
        routes_dict = self.__separate_routes_by_bbox(routes_dict, self.bbox_list)

        return routes_dict

    def __separate_routes_by_bbox(self, routes_dict, bbox_list):
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
                    # Break the loop
                    break

        # Return the new dictionary
        # TODO: Understand why I am loosing 12 routes after this step
        return new_routes_dict

    def serialize_actual_sequences(self, actual_sequences):
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
                sorted_ac_dict = {
                    k: v for k, v in sorted(ac_dict.items(), key=lambda item: item[1])
                }
                sequence_names = list(sorted_ac_dict.keys())
                actual_sequences[route_id] = sequence_names

        return actual_sequences

    def serialize_all(self, root_directory: str):
        """Serializes all the files in the root directory."""
        start = time.time()

        # Read the package data
        with open(f"{root_directory}/package_data.json", "r") as outfile:
            db_package = json.load(outfile)
        outfile.close()
        packages_dict = db_package.copy()

        ## Serialize the package data
        packages_dict = self.serialize_packages(packages_dict=packages_dict)

        ## Calculate the total number of packages
        total_packages = 0
        for x in packages_dict.keys():
            for y in packages_dict[x].keys():
                total_packages += len(packages_dict[x][y])

        ## Store variables as attributes
        self.packages_dict = packages_dict
        self.total_packages = total_packages
        pck_time = time.time()
        print(f"package_data.json has been loaded in {pck_time - start:.2f} seconds.")

        # Read the route data
        with open(f"{root_directory}/route_data.json", "r") as outfile:
            db_route = json.load(outfile)
        outfile.close()
        routes_dict = db_route.copy()

        ## Serialize the route data
        self.routes_dict = self.serialize_routes(
            routes_dict=routes_dict, packages_dict=packages_dict
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
        for route in routes_dict.values():
            route.set_actual_sequence(ac_sequences_dict[route.name])
        ac_sequence_time = time.time()
        print(
            "actual_sequences.json has been loaded in {:.2f} seconds.".format(
                ac_sequence_time - route_time
            )
        )

        # Read the travel times data
        self.serialize_travel_times(travel_times=None)

        print(
            "We are ready to proceed. All files have been loaded in {:.2f} seconds.".format(
                time.time() - start
            )
        )

    def time_history_analysis(self, routes_dict):
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

        # Summarize la_times by day
        la_times_by_day = self.__create_times_dict(la_times)

        # Summarize boston_times by day
        boston_times_by_day = self.__create_times_dict(boston_times)

        # Summarize austin_times by day
        austin_times_by_day = self.__create_times_dict(austin_times)

        # Summarize chicago_times by day
        chicago_times_by_day = self.__create_times_dict(chicago_times)

        # Summarize seattle_times by day
        seattle_times_by_day = self.__create_times_dict(seattle_times)

        # Store the time range
        self.time_range = min(chicago_times_by_day.keys()), max(
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
        print(
            f"  (...it considers total of {np.sum([len(self.packages_dict[x]) for x in self.packages_dict.keys()])} deliveries)"
        )
        print(
            f"    (...which represents a total of {len(self.packages_dict.keys())} routes"
        )

        # Route Data
        print(
            f"A total of {len(self.routes_dict)} routes were loaded from route_data.json"
        )

        # Actual Sequences
        print(
            "The actual sequence of {} routes were loaded".format(
                len(self.ac_sequences_dict)
            )
        )

        print("Routes by city:")
        self.print_info_by_city()

    def export_routes_to_csv(
        self, city: str = "Los Angeles", filename="routes.csv"
    ) -> None:
        # Write Los Angeles coordinates to a file
        with open(filename, "w") as f:
            # Write header
            f.write("route,stop,lat,lon,distance_to_next_stop(km),duration(min)\n")
            # Iterate over routes
            for route in self.routes_dict[city].values():
                for stop in route.actual_sequence:
                    f.write(
                        "{},{},{},{},-,-\n".format(
                            route.name, stop.name, stop.location[0], stop.location[1]
                        )
                    )


# TODO: Improve print methods
# TODO: Double check code efficiency and speed up
