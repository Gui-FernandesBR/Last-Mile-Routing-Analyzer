from functools import cached_property

import matplotlib.pyplot as plt
import pandas as pd

from .route import Route


class Analysis:
    """A class to analyze a set of routes."""

    def __init__(self, name: str, routes: list[Route]):
        """Initialize the analysis object."""
        self.name, self.routes = (name, routes)
        self.routes = list(self.routes)
        self.routes_dict = {x.name: x for x in self.routes}

    # Time analysis

    def calculate_time_period(self) -> None:
        """Calculate the time period of the analysis. This is calculated by
        finding the minimum and maximum time of all routes.
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

    @property
    def calendar_dict(self):
        """Create and return a dictionary as a calendar considering the time of each stop."""

        calendar_dict = {}
        for route in self.routes:
            year, month, day = route.departure_time.strftime("%Y-%m-%d").split("-")
            if year not in calendar_dict:
                calendar_dict[year] = {}
            if month not in calendar_dict[year]:
                calendar_dict[year][month] = {}
            if day not in calendar_dict[year][month]:
                calendar_dict[year][month][day] = {}
            calendar_dict[year][month][day][route.name] = route.stops

        return calendar_dict

    # Circuity Factor analysis

    def calculate_driving_distances(
        self,
        planned: bool = False,
        actual: bool = True,
        mode="osm",
        multiprocessing: bool = False,
        planned_distance_matrix=None,
        actual_distance_matrix=None,
    ):
        """Calculate the driving distances between all stops for all routes, in
        case they were not calculated before."""

        for route in self.routes_dict.values():
            route.evaluate_driving_distances(
                planned=planned,
                actual=actual,
                mode=mode,
                multiprocessing=multiprocessing,
                planned_distance_matrix=planned_distance_matrix,
                actual_distance_matrix=actual_distance_matrix,
            )

    def calculate_circuity_factor(self, planned: bool = True):
        """Calculate the circuity factor of all routes."""
        for route in self.routes_dict.values():
            route.evaluate_circuity_factor(planned)

    # Package analysis

    @property
    def routes_status_dict(self) -> None:
        """Calculate the status of the routes in the analysis."""
        routes_status_dict = {}
        for route in self.routes_dict.values():
            routes_status_dict[route.name] = route.route_status_dict

        return routes_status_dict

    @property
    def total_number_of_packages(self):
        return sum(route.number_of_packages for route in self.routes)

    @property
    def number_of_delivered_packages(self):
        return sum(
            x.route_status_dict["number_of_delivered_packages"]
            for x in self.routes_dict.values()
        )

    @property
    def delivered_packages_percentage(self):
        return self.number_of_delivered_packages / self.total_number_of_packages

    @property
    def number_of_failed_attempted_packages(self):
        return sum(
            x.route_status_dict["number_of_failed_attempted_packages"]
            for x in self.routes_dict.values()
        )

    @property
    def failed_attempted_packages_percentage(self):
        return self.number_of_failed_attempted_packages / self.total_number_of_packages

    @property
    def number_of_rejected_packages(self):
        return sum(
            x.route_status_dict["number_of_rejected_packages"]
            for x in self.routes_dict.values()
        )

    @property
    def rejected_packages_percentage(self):
        return self.number_of_rejected_packages / len(self.routes_dict.values())

    @property
    def max_number_of_delivery_stops(self):
        return max(
            x.route_status_dict["number_of_delivery_stops"]
            for x in self.routes_dict.values()
        )

    @property
    def max_number_of_pickup_stops(self):
        return max(
            x.route_status_dict["number_of_pickup_stops"]
            for x in self.routes_dict.values()
        )

    @property
    def average_packages_per_stop(self):
        return self.total_number_of_packages / (self.max_number_of_delivery_stops)

    @cached_property
    def routes_status_metrics(self) -> dict[str, float]:
        return {
            "total_number_of_packages": self.total_number_of_packages,
            "number_of_delivered_packages": self.number_of_delivered_packages,
            "delivered_packages_percentage": self.delivered_packages_percentage,
            "number_of_failed_attempted_packages": self.number_of_failed_attempted_packages,
            "failed_attempted_packages_percentage": self.failed_attempted_packages_percentage,
            "number_of_rejected_packages": self.number_of_rejected_packages,
            "rejected_packages_percentage": self.rejected_packages_percentage,
            "max_number_of_delivery_stops": self.max_number_of_delivery_stops,
            "max_number_of_pickup_stops": self.max_number_of_pickup_stops,
            "average_packages_per_stop": self.average_packages_per_stop,
        }

    # Unique stops analysis (left apart from the analysis.py, because it was consuming too much time)

    # Centroid analysis

    def calculate_centroids(self) -> None:
        """Calculate the centroid of all routes."""
        for route in self.routes_dict.values():
            route.calculate_route_centroid()

    # Geometric analysis

    def calculate_each_route_bbox(self) -> None:
        """Calculate the bounding box of all routes."""

        for route in self.routes_dict.values():
            route.find_bbox()

    def find_overall_bbox(self) -> None:
        """Find and select the bbox that encloses all of the routes. It kind
        requires that the bbox had been previously calculated for each route.
        """

        # Find the bbox that encloses all of the routes
        bbox = ["init", "init", "init", "init"]
        for route in self.routes_dict.values():
            if bbox == ["init", "init", "init", "init"]:
                bbox = route.actual_bbox
            else:
                bbox = [
                    min(bbox[0], route.actual_bbox[0]),
                    min(bbox[1], route.actual_bbox[1]),
                    max(bbox[2], route.actual_bbox[2]),
                    max(bbox[3], route.actual_bbox[3]),
                ]  # TODO: Use planned/actual bbox instead of only the actual

        self.overall_bbox = bbox

        # Calculate the area of the bbox
        # TODO: This is multiplying two angles, so it is not correct
        self.overall_bbox_area = (self.overall_bbox[2] - self.overall_bbox[0]) * (
            self.overall_bbox[3] - self.overall_bbox[1]
        )

    def plot_circuity_factor(self, planned: bool = False, actual=True) -> None:
        """Plot the circuity factor of the routes."""

        if actual:
            # # Plot the circuity factor of the actual routes
            # plt.figure()
            # plt.title("Circuity factor of the actual routes")
            # plt.xlabel("Route ID")
            # plt.ylabel("Circuity factor")
            # plt.scatter(
            #     self.routes_dict.keys(),
            #     [x.total_actual_circuity_factor for x in self.routes_dict.values()],
            # )
            # plt.show()

            plt.figure()
            plt.title("Circuity factor of the actual routes")
            plt.xlabel("Total Euclidean distance (km)")
            plt.ylabel("Circuity factor")
            plt.scatter(
                [x.total_actual_euclidean_distance for x in self.routes_dict.values()],
                [x.total_actual_circuity_factor for x in self.routes_dict.values()],
            )
            plt.show()

            # TODO: Improve C.F. plots

        if planned:
            pass

    # Print and report methods

    def print_all_info(self):
        print(
            "The time period of the analysis group is: from "
            f"{self.time_period[0].strftime('%Y-%m-%d')} to "
            f"{self.time_period[1].strftime('%Y-%m-%d')}"
        )
        print(f"The time period length is: {self.time_period_length.days} days")
        print(f"The number of routes is: {len(self.routes)}")
        print(f"The number of stops is: {len(self.unique_stops_dict)}")
        print(f"The number of deliveries is: {self.number_of_deliveries}")

    # Export methods

    @cached_property
    def summarize_by_routes(self) -> dict:
        """Summarize the information by routes. This is useful for exporting
        purposes.
        """

        df = {}  # Initialize the dictionary

        # Iterate over the routes and summarize the information
        for route in self.routes:
            df[route.name] = {
                "Name": route.name,
                "Centroid Lat - mean - (deg)": route.actual_sequence_centroid_mean[0],
                "Centroid Lon - mean - (deg)": route.actual_sequence_centroid_mean[1],
                "Centroid Lat - stdev - (deg)": route.actual_sequence_centroid_std[0],
                "Centroid Lon - stdev - (deg)": route.actual_sequence_centroid_std[1],
                "Number of delivery stops": route.number_of_delivery_stops,
                "Number of depot stops": route.number_of_pickup_stops,
                # "Number of stops": route.number_of_delivery_stops + route.number_of_pickup_stops,
                "Number of packages": route.number_of_packages,
                "Number of delivered packages": route.number_of_delivered_packages,
                "Number of rejected packages": route.number_of_rejected_packages,
                "Number of failed attempted packages": route.number_of_failed_attempted_packages,
                "Avg packages per stop": route.avg_packages_per_stop,
                "Rejected packages (%)": self.rejected_packages_percentage,
                "Delivered packages (%)": self.delivered_packages_percentage,
                "Failed attempted packages (%)": self.failed_attempted_packages_percentage,
                "Bbox area - (km^2)": route.actual_bbox_area,
                "Bbox north - (deg)": route.actual_bbox[2],
                "Bbox south - (deg)": route.actual_bbox[0],
                "Bbox east - (deg)": route.actual_bbox[3],
                "Bbox west - (deg)": route.actual_bbox[1],
                # "Distance to depots (km)": route.distances_depot_dict,
                # Start storing the circuity factor details
                "Total Euclidean distance (km)": route.total_actual_euclidean_distance,
                "Total Driving distance (km)": route.total_actual_driving_distance,
                "Total Circuity factor": route.total_actual_circuity_factor,
                "Avg Euclidean distance per stop (km)": route.avg_actual_euclidean_distance,
                "Avg Driving distance per stop (km)": route.avg_actual_driving_distance,
                "Avg Circuity factor per stop": route.mean_actual_circuity_factor,
                # "Stdev Circuity factor per stop": route.std_actual_circuity_factor,
                "Min Circuity factor per stop": route.min_actual_circuity_factor,
                "Max Circuity factor per stop": route.max_actual_circuity_factor,
                "Median Circuity factor per stop": route.med_actual_circuity_factor,
            }  # TODO: Fix total packages %
        return df

    def export_summary_by_routes(
        self, filename: str = "summary_by_routes.csv"
    ) -> pd.DataFrame:
        """Summarize the status of the routes in the analysis. Each route will be
        represented by its centroid.
        """

        df = self.summarize_by_routes
        df = pd.DataFrame.from_dict(df, orient="index")
        df.to_csv(filename)
        return df


# TODO: Plot the % rejection vs Circuity factor per route/neighborhood
