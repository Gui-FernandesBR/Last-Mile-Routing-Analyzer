__author__ = "Guilherme Fernandes Alves"
__email__ = "gf10.alves@gmail.com"
__license__ = "Mozilla Public License 2.0"


import matplotlib.pyplot as plt
import pandas as pd


class analysis:
    """A class to analyze a set of routes."""

    def __init__(self, name: str, routes: list):
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

        # Create a dictionary with the routes, to facilitate the access
        self.routes_dict = {x.name: x for x in self.routes}

        return None

    # Time analysis

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

    # Circuity Factor analysis

    def calculate_euclidean_distances(self, planned=True, actual=True) -> None:
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
            route.evaluate_euclidean_distances(planned=planned, actual=actual)

        return None

    def calculate_driving_distances(
        self,
        planned=True,
        actual=True,
        mode="osm",
        multiprocessing=False,
        planned_distance_matrix=None,
        actual_distance_matrix=None,
    ):
        """Calculate the driving distances between all stops for all routes, in
        case they were not calculated before.

        Parameters
        ----------
        ...

        Returns
        -------
        None
        """

        for route in self.routes_dict.values():
            route.evaluate_driving_distances(
                planned=planned,
                actual=actual,
                mode=mode,
                multiprocessing=multiprocessing,
                planned_distance_matrix=planned_distance_matrix,
                actual_distance_matrix=actual_distance_matrix,
            )

        return None

    def calculate_circuity_factor(self, planned=True, actual=True):
        """Calculate the circuity factor of all routes.

        Parameters
        ----------
        planned : bool, optional
            Whether to calculate the circuity factor of the planned routes.
        actual : bool, optional
            Whether to calculate the circuity factor of the actual routes.

        Returns
        -------
        None
        """

        for route in self.routes_dict.values():
            route.evaluate_circuity_factor(planned=False, actual=True)

        return None

    # Package analysis

    def calculate_packages_status(self) -> None:
        """Calculate the status of the routes in the analysis.

        Returns
        -------
        None
        """
        routes_status_dict = {}
        for route in self.routes_dict.values():
            try:
                routes_status_dict[route.name] = route.route_status_dict
            except:
                route.evaluate_route_status()
                routes_status_dict[route.name] = route.route_status_dict
        # Save the dictionary
        self.routes_status_dict = routes_status_dict

        # Calculate the number of stops and packages, as well as other metrics
        self.__calculate_route_status_metrics()

        return None

    def __calculate_route_status_metrics(self) -> None:
        """Calculate the metrics of the routes status. This is an internal method,
        and should not be called directly. It will be called by the method
        'calculate_packages_status'.

        Returns
        -------
        None
        """
        self.total_number_of_packages = sum(
            [
                x.route_status_dict["number_of_packages"]
                for x in self.routes_dict.values()
            ]
        )

        # Calculate the package status over the routes
        ## Calculate the percentage of packages that were delivered
        self.number_of_delivered_packages = sum(
            [
                x.route_status_dict["number_of_delivered_packages"]
                for x in self.routes_dict.values()
            ]
        )
        self.delivered_packages_percentage = (
            self.number_of_delivered_packages / self.total_number_of_packages
        )

        ## Calculate the percentage of packages that had an delivered attempt with no success
        self.number_of_failed_attempted_packages = sum(
            [
                x.route_status_dict["number_of_failed_attempted_packages"]
                for x in self.routes_dict.values()
            ]
        )
        self.failed_attempted_packages_percentage = (
            self.number_of_failed_attempted_packages / self.total_number_of_packages
        )

        ## Calculate the percentage of rejected routes
        self.number_of_rejected_packages = sum(
            [
                x.route_status_dict["number_of_rejected_packages"]
                for x in self.routes_dict.values()
            ]
        )
        self.rejected_packages_percentage = self.number_of_rejected_packages / len(
            self.routes_dict.values()
        )

        # Calculate the max number of delivery stops
        self.max_number_of_delivery_stops = max(
            [
                x.route_status_dict["number_of_delivery_stops"]
                for x in self.routes_dict.values()
            ]
        )

        # Calculate the max number of depot stops
        self.max_number_of_pickup_stops = max(
            [
                x.route_status_dict["number_of_pickup_stops"]
                for x in self.routes_dict.values()
            ]
        )

        # Calculate the total average package per stop
        self.average_packages_per_stop = self.total_number_of_packages / (
            self.max_number_of_delivery_stops
        )

        # Summarize the results by a dictionary
        self.routes_status_metrics = {
            "total_number_of_packages": self.total_number_of_packages,
            "number_of_delivered_packages": self.number_of_delivered_packages,
            "delivered_packages_percentage": self.delivered_packages_percentage,
            "number_of_failed_attempted_packages": self.number_of_failed_attempted_packages,
            "attempted_packages_percentage": self.attempted_packages_percentage,
            "number_of_rejected_packages": self.number_of_rejected_packages,
            "rejected_packages_percentage": self.rejected_packages_percentage,
            "max_number_of_delivery_stops": self.max_number_of_delivery_stops,
            "max_number_of_pickup_stops": self.max_number_of_pickup_stops,
            "average_packages_per_stop": self.average_packages_per_stop,
        }

        return None

    # Unique stops analysis (left apart from the analysis.py, because it was consuming too much time)

    # Centroid analysis

    def calculate_centroids(self, planned=True, actual=True) -> None:
        """Calculate the centroid of all routes.

        Parameters
        ----------
        planned : bool, optional
            Whether to calculate the centroid of the planned routes.
        actual : bool, optional
            Whether to calculate the centroid of the actual routes.

        Returns
        -------
        None
        """

        for route in self.routes_dict.values():
            route.calculate_route_centroid()

        return None

    # Geometric analysis

    def calculate_each_route_bbox(self) -> None:
        """Calculate the bounding box of all routes.

        Returns
        -------
        None
        """

        for route in self.routes_dict.values():
            route.find_bbox()

        return None

    def find_overall_bbox(self) -> None:
        """Find and select the bbox that encloses all of the routes. It kind
        requires that the bbox had been previously calculated for each route.

        Returns
        -------
        None
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

        # Save the bbox
        self.overall_bbox = bbox

        # Calculate the area of the bbox
        self.overall_bbox_area = (self.overall_bbox[2] - self.overall_bbox[0]) * (
            self.overall_bbox[3] - self.overall_bbox[1]
        )  # TODO: This are is multiplying two angles, so it is not correct

        return None

    # GeoSpatial operations (in the future!)

    # Combined analysis methods

    def __calculate_all(self, planned=False, actual=False) -> None:
        """This is currently private for documentation purposes. It will be
        public in the future when it is ready."""

        return None

    # Plot methods (in the future!)

    def plot_circuity_factor(self, planned=False, actual=True) -> None:
        """Plot the circuity factor of the routes.

        Parameters
        ----------
        planned : bool, optional
            Whether to plot the planned routes.
        actual : bool, optional
            Whether to plot the actual routes.

        Returns
        -------
        None
        """

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

        return None

    # Print and report methods

    def print_all_info(self):
        # TODO: Improve print_all_info
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
        # TODO: Implement plot_all_info
        return None

    # Export methods

    def summarize_by_routes(self) -> dict:
        """Summarize the information by routes. This is useful for exporting
        purposes.

        Returns
        -------
        None
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

        # Return the dictionary
        return df

    def export_summary_by_routes(self, filename: str = "summary_by_routes.csv") -> None:
        """Summarize the status of the routes in the analysis. Each route will be
        represented by its centroid.

        Parameters
        ----------
        filename: str
            The name of the .csv file to be exported. The default is
            "summary_by_routes.csv".
        """

        df = self.summarize_by_routes()
        df = pd.DataFrame.from_dict(df, orient="index")
        df.to_csv(filename)

        return None
