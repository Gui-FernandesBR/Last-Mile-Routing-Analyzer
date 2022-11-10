__author__ = "Guilherme Fernandes Alves"
__license__ = "Mozilla Public License 2.0"

from datetime import datetime
from math import sqrt

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import osmnx as ox

from .geometry import geometry
from .route import route
from .stop import stop
from .utilities import get_city_state_names, get_distance


class analysis:
    """A class to analyze a set of routes."""

    def __init__(self, name, routes):
        """Initialize the analysis object.

        Parameters
        ----------
        name : str
            The name of the analysis.
        routes : list
            A list containing the routes of the analysis.

        Returns
        -------
        None
        """
        # Save arguments
        self.name, self.routes = (name, routes)

        # Check if the routes are valid
        if not isinstance(self.routes, list):
            raise TypeError("The 'routes' argument must be a list.")

        # if not all([isinstance(x, route) for x in self.routes]):
        #     raise TypeError("The 'routes' argument must be a list of route objects.")

        # Create a dictionary with the routes, to facilitate the access
        self.routes_dict = {x.name: x for x in self.routes}

        # Calculate other attributes
        # self.calculate_time_period()
        # self.calculate_euclidean_distances()
        # self.calculate_driving_distances()
        # self.calculate_circuity_factor() # In case they were not calculated before...
        # self.calculate_routes_status()
        # self.calculate_unique_stops()
        # self.add_city_states_to_dict()

        return None

    def calculate_time_period(self):
        """Calculate the time period of the analysis. This is calculated by
        finding the minimum and maximum time of all routes.

        Returns
        -------
        None
        """

        # Initialize the time period extremes
        self.total_start_time = self.total_end_time = self.routes[0].departure_time

        # Iterate over all routes to find the correct extremes
        for route in self.routes:
            if route.departure_time < self.total_start_time:
                self.total_start_time = route.departure_time
            if route.departure_time > self.total_end_time:
                self.total_end_time = route.departure_time

        # Calculate the time period
        self.time_period = (self.total_start_time, self.total_end_time)
        self.time_period_length = self.total_end_time - self.total_start_time

        return None

    def calculate_euclidean_distances(self, planned=True, actual=True):
        """Calculate the euclidean distances between all stops for all routes, in
        case they were not calculated before.

        Parameters
        ----------
        planned : bool, optional
            Whether to calculate the euclidean distances between the planned stops.
        actual : bool, optional
            Whether to calculate the euclidean distances between the actual stops.

        Returns
        -------
        None
        """
        for route in self.routes_dict.values():
            route.evaluate_euclidean_distances(planned, actual)

        return None

    def calculate_driving_distances(self, distance_matrix=None, mode=None):
        """Calculate the driving distances between all stops for all routes, in
        case they were not calculated before.

        Parameters
        ----------
        distance_matrix : dict, optional
            A dictionary containing the distance matrix.
        mode : str, optional
            The mode of transportation to use in the distance matrix.

        Returns
        -------
        None
        """

        # for route in self.routes_dict.values():
        #     # TODO: Need to add 'distance_matrix' and 'mode' as arguments
        #     route.evaluate_driving_distances(distance_matrix, mode)

        return None

    def calculate_routes_status(self):
        """Calculate the status of the routes in the analysis.

        Returns
        -------
        None
        """
        routes_status_dict = {}
        for route in self.routes_dict.values():
            try:
                routes_status_dict[route.name] = route.route_status
            except:
                route.evaluate_route_status()
                routes_status_dict[route.name] = route.route_status

        # Calculate the number of stops and packages, as well as other metrics
        self.routes_status = routes_status_dict
        self.total_number_of_packages = sum(
            [x.route_status["number_of_packages"] for x in self.routes_dict.values()]
        )

        # Calculate the package status over the routes
        ## Calculate the percentage of packages that were delivered
        self.delivered_packages = sum(
            [
                x.route_status["number_of_delivered_packages"]
                for x in self.routes_dict.values()
            ]
        )
        self.delivered_packages_percentage = (
            self.delivered_packages / self.total_number_of_packages
        )

        ## Calculate the percentage of packages that had an delivered attempt with no success
        self.attempted_packages = sum(
            [
                x.route_status["number_of_attempted_packages"]
                for x in self.routes_dict.values()
            ]
        )
        self.attempted_packages_percentage = (
            self.attempted_packages / self.total_number_of_packages
        )

        ## Calculate the percentage of rejected routes
        self.rejected_packages = sum(
            [
                x.route_status["number_of_rejected_packages"]
                for x in self.routes_dict.values()
            ]
        )
        self.rejected_packages_percentage = self.rejected_packages / len(
            self.routes_dict.values()
        )

        return None

    def calculate_unique_stops(
        self,
    ):  # I would not recommend using this function for now
        """Calculate the unique stops lists and the number of unique stops.
        It assumes that stops that are closer than 20 meters are the same stop,
        considering the haversine distance between them.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # Create a list with the first stop
        unique_stops = {
            0: {
                "latitude": self.routes[0]
                .stops[self.routes[0].stops_names[0]]
                .location[0],
                "longitude": self.routes[0]
                .stops[self.routes[0].stops_names[0]]
                .location[1],
                "location_type": self.routes[0]
                .stops[self.routes[0].stops_names[0]]
                .location_type,
                "stops": [],
            }
        }

        # Calculate the delta limit
        delta_limit = 20 * 360 / (2 * 3.14159265359 * 6371 * 1e6)

        # Iterate through all the routes
        for route in self.routes_dict.values():
            # Iterate through the stops list
            for stop in route.stops.values():
                # Iterate through the unique stops dictionary
                # TODO: This is incredibly slow. Need to find a better way to do this.
                for unique_stop in unique_stops.values():
                    # If the distance is lower and 20m
                    delta_lat = unique_stop["latitude"] - stop.location[0]
                    delta_lon = unique_stop["longitude"] - stop.location[1]

                    if sqrt(delta_lat**2 + delta_lon**2) < delta_limit:
                        # if (
                        #     get_distance(
                        #         (unique_stop["latitude"], unique_stop["longitude"]),
                        #         (stop.location[0], stop.location[1]),
                        #     )[0]
                        #     < 0.020
                        # ):
                        # Add the stop to the list of stops of the current unique stop
                        unique_stop["stops"].append(stop)
                        # Break the loop
                        break
                else:
                    # If the loop did not break, then the stop is unique until now
                    unique_stops[len(unique_stops)] = {
                        "latitude": stop.location[0],
                        "longitude": stop.location[1],
                        "location_type": stop.location_type,
                        "stops": [stop],
                    }

        # Save attributes
        self.unique_stops = unique_stops
        self.number_of_unique_stops = len(unique_stops)

        return None

    def calculate_status_by_stops(self):
        """Calculate the status of the unique stops in the analysis.

        Returns
        -------
        None
        """

        # TODO: Can be optimized by using dictionaries
        # Iterate over the unique stops dictionary
        for stop in self.unique_stops_dict.values():

            # Initialize the status of the stop
            # stop["status"] = {
            #     "number_of_packages": 0,
            #     "number_of_delivered_packages": 0,
            #     "number_of_attempted_packages": 0,
            #     "number_of_rejected_packages": 0,
            # }
            stop["number_of_packages"] = 0
            stop["number_of_delivered_packages"] = 0
            stop["number_of_attempted_packages"] = 0
            stop["number_of_rejected_packages"] = 0

            # Iterate over all the unique routes
            for route in self.routes_dict.values():

                # Iterate over all the stops in the route
                for route_stop in route.stops.values():

                    # Check if the stop is the same as the one in the unique stops dictionary
                    if (
                        abs(stop["location"][0] - route_stop.location[0]) < 0.000001
                        and abs(stop["location"][1] - route_stop.location[1]) < 0.000001
                        and stop["location_type"] == route_stop.location_type
                    ):

                        # Update the status of the stop
                        stop["number_of_packages"] += route_stop.number_of_packages
                        stop[
                            "number_of_delivered_packages"
                        ] += route_stop.number_of_delivered_packages
                        stop[
                            "number_of_attempted_packages"
                        ] += route_stop.number_of_attempted_packages
                        stop[
                            "number_of_rejected_packages"
                        ] += route_stop.number_of_rejected_packages

        return None

    def find_common_geometry(self):
        """Find and select the common geometry of the routes.

        Returns
        -------
        None
        """

        # Define the boundaries of the map
        # stops_list = list(self.unique_stops_dict.values())
        # coord_lists = [x["location"] for x in stops_list]
        # north = np.max([x[0] for x in coord_lists])
        # south = np.min([x[0] for x in coord_lists])
        # east = np.max([x[1] for x in coord_lists])
        # west = np.min([x[1] for x in coord_lists])

        return None

    # TODO: This should actually be inside the routes class
    def add_city_states_to_dict(self):
        """Create a dictionary with the states of each stop.

        Returns
        -------
        None
        """

        for stop in self.unique_stops_dict.values():
            # Get the state of the stop
            city, state = get_city_state_names(stop["location"])

            # Add the state to the dictionary
            stop["state"] = state
            stop["city"] = city

        return None

    def create_unique_stops_gdf(self):
        """Create a GeoDataFrame with the unique stops.

        Returns
        -------
        None
        """

        # Create a GeoDataFrame with the unique stops
        self.unique_stops_gdf = gpd.GeoDataFrame(
            self.unique_stops_dict.values(),
            geometry=gpd.points_from_xy(
                [x["location"][1] for x in self.unique_stops_dict.values()],
                [x["location"][0] for x in self.unique_stops_dict.values()],
            ),
        )

        return None

    def merge_gdfs(self, geometry):

        # Take the geometry object and retrieve the spatial geodataframe
        gdf = geometry.polygons

        # Merge the two geodataframe, adding neighborhood information to the stops
        self.merged_unique_stops_gdf = gpd.sjoin(
            self.unique_stops_gdf, gdf, how="left", op="within"
        )

        # Save the merged geodataframe
        import os

        self.merged_unique_stops_gdf.to_file(
            os.path.join(self.output_folder, "merged_unique_stops_gdf.geojson"),
            driver="GeoJSON",
        )

        return None

    def create_calendar_dict(self):
        """Create a dictionary as a calendar considering the time of each stop.

        Returns
        -------
        None
        """

        # Iterate through all routes and stops to create the calendar
        calendar_dict = {}
        for route in self.routes:
            # pass  # Only for safety reasons, temporarily
            year, month, day = route.departure_time.strftime("%Y-%m-%d").split("-")
            # if year not in calendar_dict.keys():
            #     calendar_dict[year] = {}
            # if month not in calendar_dict[year].keys():
            #     calendar_dict[year][month] = {}
            # if day not in calendar_dict[year][month].keys():
            #     calendar_dict[year][month][day] = {}
            # calendar_dict[year][month][day][route.name] = route.stops
            try:
                calendar_dict[year][month][day][route.name] = route.stops
            except KeyError:
                try:
                    calendar_dict[year][month][day] = {route.name: route.stops}
                except KeyError:
                    try:
                        calendar_dict[year][month] = {day: {route.name: route.stops}}
                    except KeyError:
                        try:
                            calendar_dict[year] = {
                                month: {day: {route.name: route.stops}}
                            }
                        except KeyError:
                            calendar_dict[year] = {
                                month: {day: {route.name: route.stops}}
                            }

        self.calendar_dict = calendar_dict

        return None

    def plot_historical_routes(self, save=False, show=True):
        # TODO: Implement this
        # delivery_history = {}
        # delivered_packages = {}
        # rejected_packages = {}
        # attempted_packages = {}
        # for year in self.calendar_dict.values():
        #     pass  # Only for safety reasons, temporarily
        #     for month in year.values():
        #         for day in month.values():
        #             for route in day.values():
        #                 for stop in route.values():
        #                     if stop.location_type == "delivery":
        #                         delivery_history[f"{year}-{month}-{day}"] += (
        #                             1
        #                             if f"{year}-{month}-{day}"
        #                             in delivery_history.keys()
        #                             else 1
        #                         )

        # self.delivery_history_list = [
        #     [datetime(i.split("-")), j] for i, j in delivery_history.items()
        # ]

        # plt.plot(self.delivery_history_list)

        return None

    def print_all_info(self):
        # TODO: Need further improvements
        print(
            "The time period of the analysis group is: from {} to {}".format(
                self.time_period[0].strftime("%Y-%m-%d"),
                self.time_period[1].strftime("%Y-%m-%d"),
            )
        )
        print("The time period length is: {} days".format(self.time_period_length.days))
        print("The number of routes is: {}".format(len(self.routes)))
        print("The number of stops is: {}".format(len(self.unique_stops_dict)))
        print("The number of deliveries is: {}".format(self.number_of_deliveries))

        return None

    def plot_all_info(self):
        # TODO: Implement this
        return None

    def analyze(self):
        """Analyze the routes.

        Returns
        -------
        None
        """
        # Plot the circuity factor against number of rejected attempts
        cf_rejected, cf_delivered, cf_attempt = [], [], []
        for route in self.routes:
            route.evaluate_route_status()
            route.evaluate_circuity_factor(planned=False)
            cf_rejected.append(
                [route.avg_circuity_factor_actual, route.rejected_packages_percentage]
            )
            cf_delivered.append(
                [route.avg_circuity_factor_actual, route.delivered_packages_percentage]
            )
            cf_attempt.append(
                [route.avg_circuity_factor_actual, route.attempted_packages_percentage]
            )

        # plt.plot( cf_rejected, label="Rejected")
        plt.scatter(
            x=[x[0] for x in cf_rejected],
            y=[x[1] * 100 for x in cf_rejected],
            label="Rejected",
        )
        plt.title("Rejected % vs Circuity Factor")
        plt.xlabel("Circuity Factor")
        plt.ylabel("Rejected %")
        plt.legend()
        plt.show()
        # plt.plot(cf_delivered, label="Delivered")
        plt.scatter(
            x=[x[0] for x in cf_delivered],
            y=[x[1] * 100 for x in cf_delivered],
            label="Delivered",
        )
        plt.title("Delivered % vs Circuity Factor")
        plt.xlabel("Circuity Factor")
        plt.ylabel("Delivered %")
        plt.legend()
        plt.show()
        # plt.plot(cf_attempt, label="Attempted")
        plt.scatter(
            x=[x[0] for x in cf_attempt],
            y=[x[1] * 100 for x in cf_attempt],
            label="Attempted",
        )
        plt.title("Attempted % vs Circuity Factor")
        plt.xlabel("Circuity Factor")
        plt.ylabel("Attempted %")
        plt.legend()
        plt.show()

        return None
