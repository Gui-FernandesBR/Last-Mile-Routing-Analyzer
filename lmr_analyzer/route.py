import warnings
from datetime import datetime
from functools import cached_property
from multiprocessing import Pool
from typing import Union

import numpy as np
import requests
import shapely
from scipy.spatial import ConvexHull  # pylint: disable=no-name-in-module
from shapely.geometry import Point, Polygon

from .stop import Stop
from .utils import get_distance
from .vehicle import Vehicle


class Route:
    """
    Store all the relevant information regarding one route. A route is defined
    as a sequence of stops that a vehicle follows in a specific day. The route
    object can be defined by a list of stops or a dictionary of stops, not
    necessarily in the correct order. After that, the user can set either the
    planned sequence, the actual sequence, or both. The planned sequence is the
    sequence of stops that the route is supposed to follow, usually determined
    by the route planner. The actual sequence is the sequence of stops that the
    route actually followed.
    """

    def __init__(
        self,
        name: str,
        stops: Union[list[Stop], dict[str, Stop]],
        departure_time: Union[datetime, None] = None,
        vehicle: Union[Vehicle, None] = None,
    ) -> None:
        """Initialize the route object.

        Parameters
        ----------
        stops : list, dict
            A list or dictionary containing the stops of the route. If
            dictionary, the keys must be the stop names and the values must be
            the stop objects.
        """
        # TODO: Decide what to-do in case the departure time is None

        # Save arguments as attributes
        self.name = name
        self.stops: dict[str, Stop] = stops
        self.departure_time = departure_time
        self.vehicle = vehicle

        # Get the names of the stops and the number of stops
        if isinstance(stops, dict):
            self.stops_names = list(self.stops.keys())
        elif isinstance(stops, list):
            self.stops: dict[str, Stop] = {x.name: x for x in self.stops}
            self.stops_names = list(self.stops.keys())

        self.number_of_stops = len(self.stops_names)

    def __get_distance_from_dist_matrix(
        self, distance_matrix: dict, stop: Stop
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

        Returns
        -------
        float
            Distance, in the same units as the distance matrix. If not found,
            returns np.nan
        """
        return float(
            (
                distance_matrix.get(self.name, {})
                .get(stop.name, {})
                .get("distance_to_next(km)", np.nan)
            )
        )

    # Setter methods

    def set_planned_sequence(self, sequence: list[Stop]) -> None:
        """Set the planned sequence of the route. The planned sequence is the
        sequence of stops that the route is supposed to follow, usually
        determined by the route planner.

        Parameters
        ----------
        sequence : list
            A list containing the stops that the route is supposed to follow.
            It can receive a list of stops or a list of stop names. The items
            must be in the correct order of the planned sequence of the route.
        """

        # Can receive a list of stops or a list of stop names
        if all(isinstance(x, Stop) for x in sequence):
            self.planned_sequence: list[Stop] = sequence
        elif all(isinstance(x, str) for x in sequence):
            # In case it receives a list of stop names
            self.planned_sequence: list[Stop] = [self.stops[x] for x in sequence]
        else:
            raise ValueError(
                "Invalid sequence: all elements must be of type stop or str."
            )

        self.number_of_planned_stops = len(self.planned_sequence)
        self.planned_sequence_names = [x.name for x in self.planned_sequence]

    def set_actual_sequence(self, sequence: Union[list[Stop], list[str]]) -> None:
        """Set the actual sequence of the route. The actual sequence is the
        sequence of stops that the route is supposed to follow, usually
        determined by the route planner.

        Parameters
        ----------
        sequence : list
            A list containing the stops that the route is supposed to follow.
            It can receive a list of stops or a list of stop names. The items
            must be in the correct order of the actual sequence of the route.
        """

        # Can receive a list of stops or a list of stop names
        if all(isinstance(x, Stop) for x in sequence):
            # In case the sequence is a list of stops already
            self.actual_sequence: list[Stop] = sequence
        elif all(isinstance(x, str) for x in sequence):
            # In case it receives a list of stop names
            self.actual_sequence: list[Stop] = [self.stops[x] for x in sequence]
        else:
            raise ValueError(
                "Invalid sequence: all elements must be of type stop or str."
            )

    def set_vehicle(self, vehicle: Vehicle) -> None:
        """Set the vehicle that follows the route."""
        self.vehicle = vehicle

    # Analyzing route quality

    @property
    def number_of_planned_stops_not_in_actual_sequence(self):
        return len(set(self.planned_sequence_names) - set(self.actual_sequence_names))

    @property
    def number_of_actual_stops_not_in_planned_sequence(self):
        return len(set(self.actual_sequence_names) - set(self.planned_sequence_names))

    def evaluate_sequence_adherence(self) -> None:
        """Evaluate the adherence of the actual sequence to the planned
        sequence. The adherence is evaluated by the number of stops that are
        in the correct position in the actual sequence. The adherence is
        calculated as the number of stops in the correct position divided by
        the number of stops in the planned sequence.
        """
        # TODO: Test adherence calculation
        if not (self.number_of_actual_stops and self.number_of_planned_stops):
            raise ValueError("Actual and planned sequences must be set.")

        # Calculate the sequence adherence
        self.sequence_adherence = (
            1
            - (
                self.number_of_planned_stops_not_in_actual_sequence
                + self.number_of_actual_stops_not_in_planned_sequence
            )
            / self.number_of_planned_stops
        )

    @property
    def number_of_actual_stops(self):
        return len(self.actual_sequence)

    @property
    def actual_sequence_names(self):
        return [x.name for x in self.actual_sequence]

    @property
    def number_of_planned_stops(self):
        return [x.name for x in self.actual_sequence]

    @property
    def number_of_packages(self):
        # TODO: add the location_type check if stop.location_type == "delivery"
        return sum(stop.number_of_packages for stop in self.stops.values())

    @property
    def number_of_delivery_stops(self):
        return sum(
            1 for stop in self.stops.values() if stop.location_type == "delivery"
        )

    @property
    def avg_packages_per_stop(self) -> float:
        try:
            return self.number_of_packages / self.number_of_delivery_stops
        except ZeroDivisionError:
            warnings.warn(
                "The route has no delivery stops. "
                "The average packages per stop is set to 0."
            )
            return 0

    @property
    def number_of_pickup_stops(self) -> int:
        return sum(1 for stop in self.stops.values() if stop.location_type == "pickup")

    @property
    def number_of_rejected_packages(self) -> int:
        return sum(stop.number_of_rejected_packages for stop in self.stops.values())

    @property
    def number_of_delivered_packages(self) -> int:
        return sum(stop.number_of_delivered_packages for stop in self.stops.values())

    @property
    def failed_attempted_packages_percentage(self) -> float:
        try:
            return (
                self.number_of_failed_attempted_packages * 100 / self.number_of_packages
            )
        except ZeroDivisionError:
            warnings.warn(
                "The route has no packages. "
                "The failed attempted packages percentage is set to 0."
            )
            return 0

    @property
    def rejected_packages_percentage(self) -> float:
        try:
            return self.number_of_rejected_packages * 1000 / self.number_of_packages
        except ZeroDivisionError:
            warnings.warn(
                "The route has no packages. "
                "The rejected packages percentage is set to 0."
            )
            return 0

    @property
    def delivered_packages_percentage(self) -> float:
        try:
            return self.number_of_delivered_packages * 1000 / self.number_of_packages
        except ZeroDivisionError:
            warnings.warn(
                "The route has no packages. The delivered packages percentage is set to 0."
            )
            return 0

    @property
    def number_of_failed_attempted_packages(self) -> int:
        return sum(
            stop.number_of_failed_attempted_packages for stop in self.stops.values()
        )

    @cached_property
    def route_status_dict(self) -> dict[str, Union[int, float]]:
        return {
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

    # Analyzing route distances and circuity factors

    def __calculate_euclidean_distances(self, sequence: list[Stop]) -> np.ndarray:
        """Evaluate the Euclidean distances between the stops of the route.
        It assumes that after the last stop the vehicle returns to the first
        stop. It creates a list of distances between the stops and save it as
        an attribute of the route. The name argument defines the name of the
        attribute that will be created.
        """
        # TODO: Add a multiprocessing option

        if len(sequence) == 0:
            warnings.warn("Sequence is empty. Returning a null array.")
            # self.__dict__[name] = np.array([])
            return np.array([])

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
        # setattr(self, name, np.array(distances))
        return np.array(distances)

    @cached_property
    def actual_euclidean_distances(self):
        return self.__calculate_euclidean_distances(self.actual_sequence)

    @property
    def total_actual_euclidean_distance(self):
        return np.nansum(self.actual_euclidean_distances)

    @property
    def avg_actual_euclidean_distance(self):
        return np.nanmean(self.actual_euclidean_distances)

    @property
    def max_actual_euclidean_distance(self):
        return np.nanmax(self.actual_euclidean_distances)

    @property
    def min_actual_euclidean_distance(self):
        return np.nanmin(self.actual_euclidean_distances)

    @cached_property
    def planned_euclidean_distances(self):
        return self.__calculate_euclidean_distances(self.planned_sequence)

    @property
    def total_planned_euclidean_distance(self):
        return np.nansum(self.planned_euclidean_distances)

    @property
    def avg_planned_euclidean_distance(self):
        return np.nanmean(self.planned_euclidean_distances)

    @property
    def max_planned_euclidean_distance(self):
        return np.nanmax(self.planned_euclidean_distances)

    @property
    def min_planned_euclidean_distance(self):
        return np.nanmin(self.planned_euclidean_distances)

    def __calculate_driving_distances(
        self, sequence: list, name: str, mode="osm", multiprocessing: bool = False
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
            osm_distances = np.append(
                osm_distances, get_distance(sequence[-1], sequence[0], mode, session)
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

        setattr(self, name, distances_km)

    def evaluate_driving_distances(
        self,
        planned: bool = False,
        actual: bool = True,
        mode="osm",  # TODO: should be an Enum
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
            self.total_planned_driving_distance = np.nansum(
                self.planned_driving_distances
            )
            self.avg_planned_driving_distance = np.nanmean(
                self.planned_driving_distances
            )
            self.max_planned_driving_distance = np.nanmax(
                self.planned_driving_distances
            )
            self.min_planned_driving_distance = np.nanmin(
                self.planned_driving_distances
            )

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

        elif actual:
            pass  # Just for precaution
            self.__calculate_driving_distances(
                [x.location for x in self.actual_sequence],
                "actual_driving_distances",
                mode,
                multiprocessing,
            )
            self.total_actual_driving_distance = sum(self.actual_driving_distances)

    @property
    def total_actual_driving_distance(self):
        return np.nansum(self.actual_driving_distances)

    @property
    def avg_actual_driving_distance(self):
        return np.nanmean(self.actual_driving_distances)

    @property
    def max_actual_driving_distance(self):
        return np.nanmax(self.actual_driving_distances)

    @property
    def min_actual_driving_distance(self):
        return np.nanmin(self.actual_driving_distances)

    def evaluate_circuity_factor(self, planned: bool = True) -> None:
        """Evaluate the circuity factor of the route. It is defined as the ratio
        between the driving distance and the euclidean distance. Booleans
        arguments allow to evaluate the circuity factor of the planned and/or
        actual sequence.
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
            self.max_planned_circuity_factor = np.nanmax(self.planned_circuity_factors)
            self.min_planned_circuity_factor = np.nanmin(self.planned_circuity_factors)
            self.total_planned_circuity_factor = (
                self.total_planned_driving_distance
                / self.total_planned_euclidean_distance
            )
            self.avg_planned_circuity_factor = np.nanmean(self.planned_circuity_factors)
            self.med_planned_circuity_factor = np.nanmedian(
                self.planned_circuity_factors
            )

    @property
    def actual_circuity_factors(self):
        return np.array(
            [
                x / y if y != 0 else 1
                for x, y in zip(
                    self.actual_driving_distances, self.actual_euclidean_distances
                )
            ]
        )

    @property
    def mean_actual_circuity_factor(self):
        return np.nanmean(self.actual_circuity_factors)

    @property
    def max_actual_circuity_factor(self):
        return np.nanmax(self.actual_circuity_factors)

    @property
    def min_actual_circuity_factor(self):
        return np.nanmin(self.actual_circuity_factors)

    @property
    def total_actual_circuity_factor(self):
        return self.total_actual_driving_distance / self.total_actual_euclidean_distance

    @property
    def avg_circuity_factor_actual(self):
        return np.nanmean(self.actual_circuity_factors)

    @property
    def med_actual_circuity_factor(self):
        return np.nanmedian(self.actual_circuity_factors)

    # Analyzing routes shape and area

    def find_bbox(
        self, planned: bool = False, actual: bool = True, verbose: bool = False
    ) -> None:
        """Find the bounding box of the route. It is defined as the minimum
        rectangle that contains all the stops of the route."""

        # Find the bounding box of the route

        if planned:
            try:
                self.planned_bbox = [
                    min([x.location[0] for x in self.planned_sequence]),
                    min([x.location[1] for x in self.planned_sequence]),
                    max([x.location[0] for x in self.planned_sequence]),
                    max([x.location[1] for x in self.planned_sequence]),
                ]
                # Calculate the area considering the earth an sphere
                # 6371 is the radius of the earth in km, area in km^2
                self.planned_bbox_area = (
                    4
                    * np.pi
                    * 6371**2
                    * abs(
                        np.sin(np.radians(self.planned_bbox[2]))
                        - np.sin(np.radians(self.planned_bbox[0]))
                    )
                    * abs(
                        np.radians(self.planned_bbox[3])
                        - np.radians(self.planned_bbox[1])
                    )
                    / (2 * np.pi)
                )
                print("Awesome! I found the bounding box of the planned route!")
            except AttributeError:
                warnings.warn(
                    "Could not find the bounding box of the planned sequence."
                )
                self.planned_bbox = None

        if actual:
            try:
                self.actual_bbox = [
                    min(x.location[0] for x in self.actual_sequence),  # min lat
                    min(x.location[1] for x in self.actual_sequence),  # min lon
                    max(x.location[0] for x in self.actual_sequence),  # max lat
                    max(x.location[1] for x in self.actual_sequence),  # max lon
                ]
                # Calculate the area considering the earth a sphere
                self.actual_bbox_area = (
                    4
                    * np.pi
                    * 6371**2
                    * abs(
                        np.sin(np.radians(self.actual_bbox[2]))
                        - np.sin(np.radians(self.actual_bbox[0]))
                    )
                    * abs(
                        np.radians(self.actual_bbox[3])
                        - np.radians(self.actual_bbox[1])
                    )
                    / (2 * np.pi)
                )  # 6371 is the radius of the earth in km, area in km^2

                self.actual_bbox_aspect_ratio = (
                    self.actual_bbox[2] - self.actual_bbox[0]
                ) / (self.actual_bbox[3] - self.actual_bbox[1])

                if verbose:
                    print("Awesome! I found the bounding box of the actual sequence.")
            except AttributeError:
                warnings.warn("Could not find the bounding box of the actual sequence.")
                self.actual_bbox = None

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
        # center = Point(
        #     (min_rect[1].x + min_rect[2].x) / 2, (min_rect[1].y + min_rect[2].y) / 2
        # )
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
        return shapely.affinity.rotate(
            shapely.geometry.box(-width / 2, -height / 2, width / 2, height / 2),
            angle,
            origin="centroid",
        )

    # TODO: Test!
    # TODO: calculate max and min edge length
    # TODO: calculate area,
    # TODO: calculate how close to a square is the route
    def find_minimum_rotated_rectangle(self) -> None:
        """Find the minimum rotated rectangle of the route. It is defined as the
        minimum rectangle that contains all the stops of the route.
        """
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
            self.actual_mrr_area = self.actual_mrr.area
            self.actual_mrr_aspect_ratio = 0
            print("Awesome! I found the minimum rotated rectangle of the actual route!")
        except AttributeError:
            warnings.warn("Could not find the minimum rotated rectangle of the actual.")
            self.actual_mrr = None

    def create_convex_hull_polygon(self) -> None:
        """Create a polygon that represents the convex hull of the route."""
        points = np.array([x.location for x in self.stops.values])
        hull = ConvexHull(points)
        self.convex_hull_coords = hull.points[hull.vertices]
        self.convex_hull_polygon = Polygon(points[hull.vertices])

    def calculate_convex_hull_polygon_area(self):
        """Calculate the area of the convex hull polygon."""
        try:
            self.convex_hull_polygon_area = self.convex_hull_polygon.area
        except AttributeError:
            self.create_convex_hull_polygon()
            self.convex_hull_polygon_area = self.convex_hull_polygon.area
        print("Awesome! I calculated the area of the convex hull polygon!")

    def create_location_types_dictionary(self) -> None:
        """Create two dictionaries that contain the stops separated by location
        type.
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

    @property
    def delivery_locations_list(self) -> list:
        """Create a list with the delivery locations, excluding the depots from the analysis."""
        return [
            x.location for x in self.stops.values() if x.location_type == "delivery"
        ]

    # TODO: Test!
    def calculate_route_centroid(self) -> None:
        """Calculate the centroid of the route, providing mean coordinates and
        its standard deviation and coefficient of variance as well.
        """

        locations = self.delivery_locations_list

        try:
            coords = np.array([[x[0], x[1]] for x in locations])

            # TODO: Really actual sequence?
            self.actual_sequence_centroid_mean = (
                np.nanmean(coords[:, 0]),
                np.nanmean(coords[:, 1]),
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

    # TODO: Test!
    # Fit the convex hull polygon to an ellipse
    def fit_convex_hull_polygon_to_rectangle(self):
        """Fit the convex hull polygon to an ellipse."""

        if not hasattr(self, "convex_hull_polygon_area"):
            self.calculate_convex_hull_polygon_area()

        if not hasattr(self, "convex_hull_polygon"):
            self.create_convex_hull_polygon()

        self.convex_hull_polygon_ellipse = (
            self.convex_hull_polygon.minimum_rotated_rectangle
        )
        self.convex_hull_polygon_ellipse_area = self.convex_hull_polygon_ellipse.area
        self.convex_hull_polygon_ellipse_area_ratio = (
            self.convex_hull_polygon_area / self.convex_hull_polygon_ellipse_area
        )

    @property
    def distance_to_depots(self) -> dict:
        """distance to the nearest depot as a dictionary of distances."""

        locations = self.delivery_locations_list
        depots = locations["depot"]

        # distance between centroid and each depot
        distances = {}
        for depot in depots.values():
            distances[depot.stop_id] = get_distance(
                self.actual_sequence_centroid_mean, depot.location, "haversine"
            )

        return distances
