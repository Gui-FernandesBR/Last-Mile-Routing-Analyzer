__author__ = "Guilherme Fernandes Alves"
__email__ = "gf10.alves@gmail.com"
__license__ = "Mozilla Public License 2.0"


import warnings
from multiprocessing import Pool

import numpy as np
import requests
import shapely
from scipy.spatial import ConvexHull
from shapely.geometry import Point, Polygon

from .stop import stop
from .utils import get_distance


class route:
    """Store all the relevant information regarding one route. A route is defined
    as a sequence of stops that a vehicle follows in a specific day. The route
    object can be defined by a list of stops or a dictionary of stops, not
    necessarily in the correct order. After that, the user can set either the
    planned sequence, the actual sequence, or both. The planned sequence is the
    sequence of stops that the route is supposed to follow, usually determined by
    the route planner. The actual sequence is the sequence of stops that the route
    actually followed.

    Attributes
    ----------
    name : string
        The name of the route.
    ...

    """

    def __init__(
        self, name: str, stops: dict, departure_time=None, vehicle=None
    ) -> None:
        """Initialize the route object.

        Parameters
        ----------
        name : string
            The name of the route.
        stops : list, dict
            A list or dictionary containing the stops of the route. Each stop must be of type
            stop. If dictionary, the keys must be the stop names and the values must be the
            stop objects.
        departure_time : datetime.time
            The departure time of the route.
            If None, ...
        vehicle : string
            The vehicle that follows the route.

        Returns
        -------
        None
        """
        # TODO: Decide what to-do in case the departure time is None

        # Save arguments as attributes
        self.name, self.stops, self.departure_time, self.vehicle = (
            name,
            stops,
            departure_time,
            vehicle,
        )

        # Get the names of the stops and the number of stops
        try:
            self.stops_names = list(self.stops.keys())
        except AttributeError:
            # The stops are not a dictionary, so they are a list
            # Convert to dictionary and try again
            self.stops = {x.name: x for x in self.stops}
            self.stops_names = list(self.stops.keys())
        self.number_of_stops = len(self.stops_names)

        return None

    def __get_distance_from_dist_matrix(
        self, distance_matrix: dict, stop: stop
    ) -> float:
        """Auxiliary function to get the distance from a distance matrix.

        Parameters
        ----------
        distance_matrix : dict
            The distance matrix dictionary to be used to calculate the driving
            distances, it must have the following structure:
            {
                ...
            }
        stop : stop
            The stop object to be used to retrieve the distance from the
            distance matrix.

        Returns
        -------
        d: float
            Distance, in the same units as the distance matrix. If not found,
            returns np.nan
        """
        d = float(
            (
                distance_matrix.get(self.name, {})
                .get(stop.name, {})
                .get("distance_to_next(km)", np.nan)
            )
        )
        return d

    # Setter methods

    def set_planned_sequence(self, sequence: list) -> None:
        """Set the planned sequence of the route. The planned sequence is the
        sequence of stops that the route is supposed to follow, usually
        determined by the route planner.

        Parameters
        ----------
        sequence : list
            A list containing the stops that the route is supposed to follow.
            It can receive a list of stops or a list of stop names. The items
            must be in the correct order of the planned sequence of the route.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            In case at least one of the items in the sequence is not of type
            stop.
        """

        # Can receive a list of stops or a list of stop names
        if all(isinstance(x, stop) for x in sequence):
            # In case the sequence is a list of stops
            # This MUST be a list of stops, not a dictionary
            self.planned_sequence = sequence
        elif all(isinstance(x, str) for x in sequence):
            # In case it receives a list of stop names
            self.planned_sequence = [self.stops[x] for x in sequence]
        else:
            raise ValueError(
                "Invalid sequence: all elements must be of type stop or str."
            )

        self.number_of_planned_stops = len(self.planned_sequence)
        self.planned_sequence_names = [x.name for x in self.planned_sequence]

        return None

    def set_actual_sequence(self, sequence: list) -> None:
        """Set the actual sequence of the route. The actual sequence is the
        sequence of stops that the route is supposed to follow, usually
        determined by the route planner.

        Parameters
        ----------
        sequence : list
            A list containing the stops that the route is supposed to follow.
            It can receive a list of stops or a list of stop names. The items
            must be in the correct order of the actual sequence of the route.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            In case at least one of the items in the sequence is not of type
            stop.
        """

        # Can receive a list of stops or a list of stop names
        if all(isinstance(x, stop) for x in sequence):
            # In case the sequence is a list of stops
            # This MUST be a list of stops, not a dictionary
            self.actual_sequence = sequence
        elif all(isinstance(x, str) for x in sequence):
            # In case it receives a list of stop names
            self.actual_sequence = [self.stops[x] for x in sequence]
        else:
            raise ValueError(
                "Invalid sequence: all elements must be of type stop or str."
            )

        self.number_of_actual_stops = len(self.actual_sequence)
        self.actual_sequence_names = [x.name for x in self.actual_sequence]

        return None

    def set_vehicle(self, vehicle) -> None:
        """Set the vehicle that follows the route.

        Parameters
        ----------
        vehicle : lmr_analyzer.vehicle
            The vehicle that follows the route.

        Returns
        -------
        None
        """
        self.vehicle = vehicle
        return None

    # Analyzing route quality

    def evaluate_sequence_adherence(self) -> None:
        """Evaluate the adherence of the actual sequence to the planned
        sequence. The adherence is evaluated by the number of stops that are
        in the correct position in the actual sequence. The adherence is
        calculated as the number of stops in the correct position divided by
        the number of stops in the planned sequence.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            In case the planned or the actual sequence is not defined.
        """
        # TODO: Test adherence calculation
        if not (self.number_of_actual_stops and self.number_of_planned_stops):
            raise ValueError("Actual and planned sequences must be set.")

        # Get the number of stops that are in the planned sequence but not in the actual sequence
        # and vice-versa
        self.number_of_planned_stops_not_in_actual_sequence = len(
            set(self.planned_sequence_names) - set(self.actual_sequence_names)
        )
        self.number_of_actual_stops_not_in_planned_sequence = len(
            set(self.actual_sequence_names) - set(self.planned_sequence_names)
        )

        # Calculate the sequence adherence (source: GitHub copilot)
        self.sequence_adherence = (
            1
            - (
                self.number_of_planned_stops_not_in_actual_sequence
                + self.number_of_actual_stops_not_in_planned_sequence
            )
            / self.number_of_planned_stops
        )

        return None

    def evaluate_route_status(self) -> None:
        """Evaluate the general status of the route. This provides a summary of
        all the packages available in each stop. Currently, the available metrics
        are:
            - Number of packages within the route
            - Number of delivery stops within the route
            - Number of pickup stops within the route
            - Number of delivered packages within the route
            - Number of rejected packages within the route
            - Number of failed attempted packages within the route
            - Average number of packages per stop (excluding depots)
            - Percentage of delivered packages within the route
            - Percentage of rejected packages within the route
            - Percentage of failed attempted packages within the route

        Returns
        -------
        None
        """

        # Initialize the route status
        number_of_packages = 0
        number_of_delivery_stops = 0
        number_of_pickup_stops = 0
        number_of_delivered_packages = 0
        number_of_rejected_packages = 0
        number_of_failed_attempted_packages = 0

        # Iterate through all the stops
        for stop in self.stops.values():
            if stop.location_type != "delivery":
                number_of_pickup_stops += 1
                continue
            number_of_delivery_stops += 1
            number_of_packages += stop.number_of_packages
            number_of_delivered_packages += stop.number_of_delivered_packages
            number_of_rejected_packages += stop.number_of_rejected_packages
            number_of_failed_attempted_packages += (
                stop.number_of_failed_attempted_packages
            )

        # Save the results as class attributes
        self.number_of_packages = number_of_packages
        self.number_of_delivery_stops = number_of_delivery_stops
        self.number_of_pickup_stops = number_of_pickup_stops
        self.number_of_delivered_packages = number_of_delivered_packages
        self.number_of_rejected_packages = number_of_rejected_packages
        self.number_of_failed_attempted_packages = number_of_failed_attempted_packages

        # Calculate the remaining route status
        try:
            self.avg_packages_per_stop = (
                number_of_packages / self.number_of_delivery_stops
            )
        except ZeroDivisionError:
            warnings.warn(
                "The route has no delivery stops. The average packages per stop is set to 0."
            )
            self.avg_packages_per_stop = 0
        try:
            self.rejected_packages_percentage = (
                self.number_of_rejected_packages * 1000 / self.number_of_packages
            )
        except ZeroDivisionError:
            warnings.warn(
                "The route has no packages. The rejected packages percentage is set to 0."
            )
            self.rejected_packages_percentage = 0
        try:
            self.delivered_packages_percentage = (
                self.number_of_delivered_packages * 1000 / self.number_of_packages
            )
        except ZeroDivisionError:
            warnings.warn(
                "The route has no packages. The delivered packages percentage is set to 0."
            )
            self.delivered_packages_percentage = 0
        try:
            self.failed_attempted_packages_percentage = (
                self.number_of_failed_attempted_packages * 100 / self.number_of_packages
            )
        except ZeroDivisionError:
            warnings.warn(
                "The route has no packages. The failed attempted packages percentage is set to 0."
            )
            self.failed_attempted_packages_percentage = 0

        # Summarize everything in a dictionary
        self.route_status_dict = {
            "number_of_packages": self.number_of_packages,
            "number_of_delivery_stops": self.number_of_delivery_stops,
            "number_of_pickup_stops": self.number_of_pickup_stops,
            "number_of_delivered_packages": self.number_of_delivered_packages,
            "number_of_rejected_packages": self.number_of_rejected_packages,
            "number_of_failed_attempted_packages": self.number_of_failed_attempted_packages,
            "avg_packages_per_stop": self.avg_packages_per_stop,
            "rejected_packages_percentage": self.rejected_packages_percentage,
            "delivered_packages_percentage": self.delivered_packages_percentage,
            "failed_attempted_packages_percentage": self.failed_attempted_packages_percentage,
        }

        return None

    def evaluate_route_scores(self) -> None:
        print("Hey, I will develop this later.")
        return None

    # Analyzing route times

    def calculate_route_times(self) -> None:
        print("Hey, I will develop this later.")
        return None

    # Analyzing route distances and circuity factors

    def __calculate_euclidean_distances(self, sequence: list, name: str) -> None:
        """Evaluate the euclidean distances between the stops of the route.
        It assumes that after the last stop the vehicle returns to the first
        stop. It creates a list of distances between the stops and save it as
        an attribute of the route. The name argument defines the name of the
        attribute that will be created.

        Parameters
        ----------
        sequence : list
            A list containing the stops of the route.
        name : str
            The name of the attribute that will be created at the end.
        Returns
        -------
        None
        """
        # TODO: Add a multiprocessing option

        if len(sequence) == 0:
            warnings.warn(
                f"Sequence is empty. The '{name}' attribute will be set as a null array."
            )
            self.__setattr__(name, np.array([]))
            return None

        # Create a list of distances between the stops
        distances = list(
            map(
                lambda x: get_distance(
                    sequence[x].location, sequence[x + 1].location, mode="haversine"
                )[0],
                range(len(sequence) - 1),
            )
        )

        # Add the distance between the last stop and the first stop
        final_distance = get_distance(
            sequence[-1].location,
            sequence[0].location,
            mode="haversine",
        )
        distances.append(final_distance[0])

        # Save the distances as an attribute of the route
        self.__setattr__(name, np.array(distances))

        return None

    def evaluate_euclidean_distances(self, planned=False, actual=False) -> None:
        """Evaluate the euclidean distances between the stops of the route.
        It assumes that after the last stop the vehicle returns to the first
        stop. It creates a list of distances between the stops and save it as
        an attribute of the route.

        Parameters
        ----------
        planned : bool, optional
            If True, it will evaluate the euclidean distances between the
            planned stops of the route, by default False
        actual : bool, optional
            If True, it will evaluate the euclidean distances between the
            actual stops of the route, by default False

        Returns
        -------
        None
        """

        # Calculate the euclidean distances between the stops
        if planned:
            self.__calculate_euclidean_distances(
                self.planned_sequence, "planned_euclidean_distances"
            )
            self.total_planned_euclidean_distance = np.sum(
                self.planned_euclidean_distances
            )
            self.avg_planned_euclidean_distance = np.mean(
                self.planned_euclidean_distances
            )
            self.max_planned_euclidean_distance = np.max(
                self.planned_euclidean_distances
            )
            self.min_planned_euclidean_distance = np.min(
                self.planned_euclidean_distances
            )
        if actual:
            self.__calculate_euclidean_distances(
                self.actual_sequence, "actual_euclidean_distances"
            )
            self.total_actual_euclidean_distance = np.sum(
                self.actual_euclidean_distances
            )
            self.avg_actual_euclidean_distance = np.mean(
                self.actual_euclidean_distances
            )
            self.max_actual_euclidean_distance = np.max(self.actual_euclidean_distances)
            self.min_actual_euclidean_distance = np.min(self.actual_euclidean_distances)

        return None

    def __calculate_driving_distances(
        self, sequence: list, name: str, mode="osm", multiprocessing=False
    ) -> None:

        session = requests.Session()
        # First check if the sequence is empty
        if len(sequence) == 0:
            raise ValueError(
                "Sequence is empty. Try to run evaluate_driving_distances method first."
            )

        if not multiprocessing:
            # Calculate the distances driving sequentially
            osm_distances = np.array(
                [
                    get_distance(location1, location2, mode, session)
                    for location1, location2 in zip(sequence[:-1], sequence[1:])
                ]
            )

            # Add the distance between the last stop and the first stop
            osm_distances.append(
                get_distance(sequence[-1], sequence[0], mode, session)[0]
            )

        else:  # Start the multiprocessing
            with Pool(processes=4) as p:
                osm_distances = p.starmap(
                    get_distance,
                    zip(
                        sequence[:-1],
                        sequence[1:],
                        [mode] * (len(sequence) - 1),
                        [session] * (len(sequence) - 1),
                    ),
                )
            osm_distances.append(get_distance(sequence[-1], sequence[0], mode, session))
        distances_km = [x[0] for x in osm_distances]
        # durations_min = [x[1] for x in osm_distances]

        self.__setattr__(name, distances_km)

        return None

    def evaluate_driving_distances(
        self,
        planned=True,
        actual=True,
        mode="osm",
        multiprocessing=False,
        planned_distance_matrix=None,
        actual_distance_matrix=None,
    ) -> None:
        """Evaluate the driving distances between the stops of the route.
        It assumes that after the last stop the vehicle returns to the first
        stop. It creates a list of distances between the stops and save it as
        an attribute of the route.

        Parameters
        ----------
        actual: bool
            If True, it evaluates the driving distances between the stops of
            the actual sequence.
        planned: bool
            If True, it evaluates the driving distances between the stops of
            the planned sequence.
        mode: str, optional
            The mode to be used to calculate the driving distances. It can be
            either "osmnx" or ...
        multiprocessing: bool, optional
            If True, it uses multiprocessing to calculate the driving distances.
        planned_distance_matrix: dict, optional
            A dictionary containing the distance matrix to be used to calculate
            the driving distances. If not None, the other parameters will be ignored.
            This can significantly speed up the calculation of the driving distances.
            The dictionary must have the following structure:
            {
                ...
            }
        actual_distance_matrix: dict, optional
            A dictionary containing the distance matrix to be used to calculate
            the driving distances. If not None, the other parameters will be ignored.
            This can significantly speed up the calculation of the driving distances.
            The dictionary must have the following structure:
            {
                ...
            }

        Returns
        -------
        None
        """

        if planned_distance_matrix is not None:
            # Calculate the distances using the distance matrix
            self.planned_driving_distances = np.array(
                list(
                    map(
                        self.__get_distance_from_dist_matrix,
                        [planned_distance_matrix] * len(self.planned_sequence),
                        self.planned_sequence,
                    )
                )
            )

            # Calculate remaining attributes
            self.total_planned_driving_distance = np.sum(self.planned_driving_distances)
            self.avg_planned_driving_distance = np.mean(self.planned_driving_distances)
            self.max_planned_driving_distance = np.max(self.planned_driving_distances)
            self.min_planned_driving_distance = np.min(self.planned_driving_distances)

        elif planned:
            pass  # Just for precaution
            self.__calculate_driving_distances(
                [x.location for x in self.planned_sequence],
                "planned_driving_distances",
                mode,
                multiprocessing,
            )
            self.total_planned_driving_distance = sum(self.planned_driving_distances)

        if actual_distance_matrix is not None:
            # Calculate the distances using the distance matrix
            self.actual_driving_distances = np.array(
                list(
                    map(
                        self.__get_distance_from_dist_matrix,
                        [actual_distance_matrix] * len(self.actual_sequence),
                        self.actual_sequence,
                    )
                )
            )

            # Calculate remaining attributes
            self.total_actual_driving_distance = np.sum(self.actual_driving_distances)
            self.avg_actual_driving_distance = np.mean(self.actual_driving_distances)
            self.max_actual_driving_distance = np.max(self.actual_driving_distances)
            self.min_actual_driving_distance = np.min(self.actual_driving_distances)

        elif actual:
            pass  # Just for precaution
            self.__calculate_driving_distances(
                [x.location for x in self.actual_sequence],
                "actual_driving_distances",
                mode,
                multiprocessing,
            )
            self.total_actual_driving_distance = sum(self.actual_driving_distances)

        return None

    def evaluate_circuity_factor(self, planned=True, actual=True) -> None:
        """Evaluate the circuity factor of the route. It is defined as the ratio
        between the driving distance and the euclidean distance. Booleans
        arguments allow to evaluate the circuity factor of the planned and/or
        actual sequence.

        Parameters
        ----------
        actual: bool
            If True, it evaluates the circuity factor of the actual sequence.
        planned: bool
            If True, it evaluates the circuity factor of the planned sequence.

        Returns
        -------
        None
        """

        if planned:
            # Calculate the circuity factor of the planned sequence avoiding the
            # division by zero
            self.planned_circuity_factors = np.array(
                [
                    x / y if y != 0 else 1
                    for x, y in zip(
                        self.planned_driving_distances, self.planned_euclidean_distances
                    )
                ]
            )
            # Calculate remaining attributes
            self.mean_planned_circuity_factor = np.mean(self.planned_circuity_factors)
            self.max_planned_circuity_factor = np.max(self.planned_circuity_factors)
            self.min_planned_circuity_factor = np.min(self.planned_circuity_factors)
            self.total_planned_circuity_factor = (
                self.total_planned_driving_distance
                / self.total_planned_euclidean_distance
            )
            self.avg_planned_circuity_factor = np.mean(self.planned_circuity_factors)
            self.med_planned_circuity_factor = np.median(self.planned_circuity_factors)

        if actual:
            # Calculate the circuity factor of the actual sequence avoiding the
            # division by zero
            self.actual_circuity_factors = np.array(
                [
                    x / y if y != 0 else 1
                    for x, y in zip(
                        self.actual_driving_distances, self.actual_euclidean_distances
                    )
                ]
            )
            # Calculate remaining attributes
            self.mean_actual_circuity_factor = np.mean(self.actual_circuity_factors)
            self.max_actual_circuity_factor = np.max(self.actual_circuity_factors)
            self.min_actual_circuity_factor = np.min(self.actual_circuity_factors)
            self.total_actual_circuity_factor = (
                self.total_actual_driving_distance
                / self.total_actual_euclidean_distance
            )
            self.avg_circuity_factor_actual = np.mean(
                self.actual_circuity_factors,
            )
            self.med_actual_circuity_factor = np.median(self.actual_circuity_factors)

        return None

    # Analyzing routes shape and area

    def find_bbox(self) -> None:
        """Find the bounding box of the route. It is defined as the minimum
        rectangle that contains all the stops of the route.

        Returns
        -------
        None
        """

        # Find the bounding box of the route

        try:
            self.planned_bbox = [
                min([x.location[0] for x in self.planned_sequence]),
                min([x.location[1] for x in self.planned_sequence]),
                max([x.location[0] for x in self.planned_sequence]),
                max([x.location[1] for x in self.planned_sequence]),
            ]
            # Calculate the area considering the earth an sphere
            self.planned_bbox_area = (
                4
                * np.pi
                * 6371**2
                * abs(
                    np.sin(np.radians(self.planned_bbox[2]))
                    - np.sin(np.radians(self.planned_bbox[0]))
                )
                * abs(
                    np.radians(self.planned_bbox[3]) - np.radians(self.planned_bbox[1])
                )
                / (2 * np.pi)
            )  # 6371 is the radius of the earth in km, area in km^2
            print("Awesome! I found the bounding box of the planned route!")
        except AttributeError:
            warnings.warn("Could not find the bounding box of the planned sequence.")
            self.planned_bbox = None

        try:
            self.actual_bbox = [
                min([x.location[0] for x in self.actual_sequence]),  # min lat
                min([x.location[1] for x in self.actual_sequence]),  # min lon
                max([x.location[0] for x in self.actual_sequence]),  # max lat
                max([x.location[1] for x in self.actual_sequence]),  # max lon
            ]
            # Calculate the area considering the earth an sphere
            self.actual_bbox_area = (
                4
                * np.pi
                * 6371**2
                * abs(
                    np.sin(np.radians(self.actual_bbox[2]))
                    - np.sin(np.radians(self.actual_bbox[0]))
                )
                * abs(np.radians(self.actual_bbox[3]) - np.radians(self.actual_bbox[1]))
                / (2 * np.pi)
            )  # 6371 is the radius of the earth in km, area in km^2

            print("Awesome! I found the bounding box of the actual sequence.")
        except AttributeError:
            warnings.warn("Could not find the bounding box of the actual sequence.")
            self.actual_bbox = None

        return None

    @staticmethod  # TODO: Test!
    def minimum_rotated_rectangle(coords: np.array):
        # Find the minimum rotated rectangle of a set of coordinates

        # Find the convex hull of the coordinates
        hull = ConvexHull(coords)
        # Find the minimum rotated rectangle of the convex hull
        min_rect = min(
            (
                (
                    Point(coords[hull.vertices[i]]).distance(
                        Point(coords[hull.vertices[j]])
                    ),
                    Point(coords[hull.vertices[i]]),
                    Point(coords[hull.vertices[j]]),
                )
                for i in range(len(hull.vertices))
                for j in range(i + 1, len(hull.vertices))
            )
        )
        # Find the center of the minimum rotated rectangle
        center = Point(
            (min_rect[1].x + min_rect[2].x) / 2, (min_rect[1].y + min_rect[2].y) / 2
        )
        # Find the angle of the minimum rotated rectangle
        angle = (
            np.arctan2(min_rect[2].y - min_rect[1].y, min_rect[2].x - min_rect[1].x)
            * 180
            / np.pi
        )
        # Find the width and height of the minimum rotated rectangle
        width = min_rect[0]
        height = min_rect[1].distance(min_rect[2])

        # Define a rectangle with the center, angle, width and height
        min_rect = shapely.affinity.rotate(
            shapely.geometry.box(-width / 2, -height / 2, width / 2, height / 2),
            angle,
            origin="centroid",
        )

        return min_rect

    # TODO: Test!
    # TODO: calculate max and min edge length
    # TODO: calculate area,
    # TODO: calculate how close to a square is the route
    def find_minimum_rotated_rectangle(self) -> None:
        """Find the minimum rotated rectangle of the route. It is defined as the
        minimum rectangle that contains all the stops of the route.

        Returns
        -------
        None
        """

        # Find the minimum rotated rectangle of the route

        try:
            self.planned_mrr = self.minimum_rotated_rectangle(
                [x.location for x in self.planned_sequence]
            )
            print(
                "Awesome! I found the minimum rotated rectangle of the planned route!"
            )
        except AttributeError:
            warnings.warn(
                "Could not find the minimum rotated rectangle of the planned."
            )
            self.planned_mrr = None

        try:
            self.actual_mrr = self.minimum_rotated_rectangle(
                [x.location for x in self.actual_sequence]
            )
            print("Awesome! I found the minimum rotated rectangle of the actual route!")
        except AttributeError:
            warnings.warn("Could not find the minimum rotated rectangle of the actual.")
            self.actual_mrr = None

        return None

    def create_convex_hull_polygon(self) -> None:
        """Create a polygon that represents the convex hull of the route.

        Returns
        -------
        None
        """
        points = np.array([x.location for x in self.stops.values])
        hull = ConvexHull(points)
        self.convex_hull_coords = hull.points[hull.vertices]
        self.convex_hull_polygon = Polygon(points[hull.vertices])

        return None

    def calculate_convex_hull_polygon_area(self):
        """Calculate the area of the convex hull polygon.

        Returns
        -------
        None
        """
        try:
            self.convex_hull_polygon_area = self.convex_hull_polygon.area
        except AttributeError:
            self.create_convex_hull_polygon()
            self.convex_hull_polygon_area = self.convex_hull_polygon.area
        print("Awesome! I calculated the area of the convex hull polygon!")

        return None

    def create_location_types_dictionary(self) -> None:
        """Create two dictionaries that contain the stops separated by location
        type.

        Returns
        -------
        None
        """
        # Create a dictionary that contains the location types of the stops
        self.depots_dict = {}
        self.delivery_points_dict = {}

        # Iterate over the stops
        for stop in self.stops.values():
            if stop.location_type == "depot":
                self.depots_dict[stop.stop_id] = stop
            elif stop.location_type == "delivery":
                self.delivery_points_dict[stop.stop_id] = stop

        self.number_of_delivery_stops = len(self.delivery_points_dict)
        self.number_of_depots = len(self.depots_dict)

        return None

    def create_delivery_locations_list(self) -> None:
        """Create a list with the delivery locations. This is powerful for
        excluding the depots from the analysis.

        Returns
        -------
        None
        """
        locations = []
        for x in self.stops.values():
            if x.location_type != "delivery":
                continue
            locations.append(x.location)
        # TODO: Do the same but using list comprehension

        self.delivery_locations_list = locations

        return None

    # TODO: Test!
    def calculate_route_centroid(self) -> None:
        """Calculate the centroid of the route, providing mean coordinates and
        its standard deviation and coefficient of variance as well.

        Returns
        -------
        None
        """

        try:
            locations = self.delivery_locations_list
        except AttributeError:
            self.create_delivery_locations_list()
            locations = self.delivery_locations_list

        try:
            coords = np.array([[x[0], x[1]] for x in locations])

            # TODO: Really actual sequence?
            self.actual_sequence_centroid_mean = (
                np.mean(coords[:, 0]),
                np.mean(coords[:, 1]),
            )

            self.actual_sequence_centroid_std = (
                np.std(coords[:, 0]),
                np.std(coords[:, 1]),
            )

            self.actual_sequence_centroid_coeff_var = (
                self.actual_sequence_centroid_std[0]
                / self.actual_sequence_centroid_mean[0],
                self.actual_sequence_centroid_std[1]
                / self.actual_sequence_centroid_mean[1],
            )

        except Exception as e:
            print("Error calculating the centroid of the route: ", e)
            print("The mean and std of the centroid are set to 0")
            self.actual_sequence_centroid_mean = (np.nan, np.nan)
            self.actual_sequence_centroid_std = (np.nan, np.nan)
            self.actual_sequence_centroid_coeff_var = (np.nan, np.nan)

        return None

    # TODO: Test!
    # Fit the convex hull polygon to an ellipse
    def fit_convex_hull_polygon_to_rectangle(self):
        """Fit the convex hull polygon to an ellipse.

        Returns
        -------
        None
        """
        try:
            self.convex_hull_polygon_area
        except AttributeError:
            self.calculate_convex_hull_polygon_area()

        try:
            self.convex_hull_polygon
        except AttributeError:
            self.create_convex_hull_polygon()

        # Fit the polygon to an ellipse
        self.convex_hull_polygon_ellipse = (
            self.convex_hull_polygon.minimum_rotated_rectangle
        )

        # Calculate the area of the ellipse
        self.convex_hull_polygon_ellipse_area = self.convex_hull_polygon_ellipse.area

        # Calculate the ratio between the area of the polygon and the area of the ellipse
        self.convex_hull_polygon_ellipse_area_ratio = (
            self.convex_hull_polygon_area / self.convex_hull_polygon_ellipse_area
        )

        return None

    def distance_to_depots(self) -> None:
        """Calculate the distance to the nearest depot.

        Returns
        -------
        None
        """

        # Get the locations dictionary
        locations = self.delivery_locations_list

        # Get the depots dictionary
        depots = locations["depot"]

        # distance between centroid and each depot
        distances = {}
        for depot in depots.values():
            distances[depot.stop_id] = get_distance(
                self.actual_sequence_centroid_mean, depot.location, "haversine"
            )

        # Save attributes
        self.distances_depot_dict = distances

        return None

    # Export and visualize route

    def print_info(self):
        return None

    def plot_route(self, return_figure=False):
        return None

    def plot_stops(self, return_figure=False):
        return None

    @classmethod
    def load_from_file(cls, filename):
        return None

    def save_to_file(self, filename):
        return None


# TODO: Calculate distance to DC
# TODO: Double check every calculate/evaluate method name
