__author__ = "Guilherme Fernandes Alves"

from multiprocessing import Pool

import numpy as np

from .stop import stop
from .utilities import get_distance
import requests

session = requests.Session()

# TODO: Need to test the FC evaluation function
class route:
    def __init__(self, name, stops, departure_time=None, vehicle=None):
        """_summary_

        Parameters
        ----------
        name : string
            The name of the route.
        stops : list, dict
            A list or dictionary containing the stops of the route. Each stop must be of type
            stop. If dictionary, the keys must be the stop names and the values must be the
            stop objects.

        Returns
        -------
        None
        """
        # Save arguments as attributes
        self.name, self.stops, self.departure_time, self.vehicle = (
            name,
            stops,
            departure_time,
            vehicle,
        )

        # Calculate other attributes
        if isinstance(stops, list):
            self.stops_names = [x.name for x in self.stops]
            self.number_of_stops = len(self.stops)
            self.stops = {x.name: x for x in self.stops}
        elif isinstance(stops, dict):
            self.stops_names = list(self.stops.keys())
            self.number_of_stops = len(self.stops_names)
        else:
            raise ValueError("Invalid stops: must be a list or dictionary of stops.")

        # Calculate the number of unique stops, i.e., the number of stops that
        # are not repeated in the route
        self.unique_stops = list(set(self.stops_names))
        self.number_of_unique_stops = len(self.unique_stops)

        return None

    def set_planned_sequence(self, sequence):
        """Set the planned sequence of the route. The planned sequence is the
        sequence of stops that the route is supposed to follow, usually
        determined by the route planner.

        Parameters
        ----------
        sequence : list
            A list containing the stops that the route is supposed to follow.

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

    def set_actual_sequence(self, sequence):
        """Set the actual sequence of the route. The actual sequence is the
        sequence of stops that the route actually followed. It can receive a
        list of stops or a list of stop names.

        Parameters
        ----------
        sequence : list
            A list containing the stops that the route actually followed. It can
            receive a list of stops or a list of stop names.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            In case at least one of the items in the sequence is not of type
            stop or str.
        """
        # Can receive a list of stops or a list of stop names
        if all(isinstance(x, stop) for x in sequence):
            # In case the sequence is a list of stops
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

    def set_vehicle(self, vehicle):
        self.vehicle = vehicle
        return None

    # Analyzing route quality

    def evaluate_sequence_adherence(self):
        if not (self.number_of_actual_stops and self.number_of_planned_stops):
            raise ValueError("Actual and planned sequences must be set.")

        return None

    def evaluate_route_status(self):

        route_status = {
            "avg_packages_per_stop": 0,
            "number_of_packages": 0,
            "number_of_delivery_stops": 0,
            "number_of_delivered_packages": 0,
            "number_of_rejected_packages": 0,
            "number_of_attempted_packages": 0,
        }

        # Fill the route status dictionary
        route_status["number_of_delivery_stops"] = self.number_of_stops
        for stop in self.stops.values():
            route_status["number_of_packages"] += stop.number_of_packages
            route_status[
                "number_of_delivered_packages"
            ] += stop.number_of_delivered_packages
            route_status[
                "number_of_rejected_packages"
            ] += stop.number_of_rejected_packages
            route_status[
                "number_of_attempted_packages"
            ] += stop.number_of_attempted_packages
        route_status["avg_packages_per_stop"] = (
            route_status["number_of_packages"] / self.number_of_stops
        )

        self.route_status = route_status
        return None

    def evaluate_route_scores(self):
        return None

    # Analyzing route stops

    def count_stops_types(self):
        return None

    def evaluate_distance_to_stop_types(self):
        return None

    # Analyzing route times

    def __calculate_route_times(self):
        return None

    # Analyzing route distances

    def __calculate_euclidean_distances(self, sequence, name):
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
            raise ValueError(
                "Sequence is empty. Try to run evaluate_euclidean_distances method first."
            )

        # Create a list of distances between the stops
        distances = []
        for i in range(len(sequence) - 1):
            location1 = sequence[i].location
            location2 = sequence[i + 1].location
            haversine = get_distance(location1, location2, mode="haversine")
            distances.append(haversine[0])
        # Add the distance between the last stop and the first stop
        final_distance = get_distance(
            sequence[-1].location,
            sequence[0].location,
            mode="haversine",
        )
        distances.append(final_distance[0])

        # Save the distances as an attribute of the route
        self.__setattr__(name, distances)

        return None

    def evaluate_euclidean_distances(self, planned=True, actual=True):
        """Evaluate the euclidean distances between the stops of the route.
        It assumes that after the last stop the vehicle returns to the first
        stop. It creates a list of distances between the stops and save it as
        an attribute of the route.

        Parameters
        ----------
        actual: bool
            If True, it evaluates the euclidean distances between the stops of
            the actual sequence.
        planned: bool
            If True, it evaluates the euclidean distances between the stops of
            the planned sequence.

        Returns
        -------
        None
        """
        if planned:
            self.__calculate_euclidean_distances(
                self.planned_sequence, "planned_euclidean_distances"
            )
            self.total_planned_euclidean_distance = sum(
                self.planned_euclidean_distances
            )
        if actual:
            self.__calculate_euclidean_distances(
                self.actual_sequence, "actual_euclidean_distances"
            )
            self.total_actual_euclidean_distance = sum(self.actual_euclidean_distances)

        return None

    def __calculate_driving_distances(
        self, sequence, name, mode="osm", multiprocessing=False
    ):

        session = requests.Session()
        # First check if the sequence is empty
        if len(sequence) == 0:
            raise ValueError(
                "Sequence is empty. Try to run evaluate_driving_distances method first."
            )

        # Create a list of distances between the stops
        if not multiprocessing:
            osm_distances = []
            for i in range(len(sequence) - 1):
                location1 = sequence[i]
                location2 = sequence[i + 1]
                driving_distance = get_distance(
                    location1, location2, mode="osm", session=session
                )
                osm_distances.append(driving_distance)
            # Add the distance between the last stop and the first stop
            final_distance = get_distance(
                sequence[-1],
                sequence[0],
                mode="osm",
            )
            osm_distances.append(final_distance)

        else:
            p = Pool(processes=4)
            p.starmap(
                get_distance,
                zip(
                    sequence[:-1],
                    sequence[1:],
                    [mode] * (len(sequence) - 1),
                    [session] * (len(sequence) - 1),
                ),
            )
            p.close()
            osm_distances = p.join()
            final_distance = get_distance(
                sequence[-1],
                sequence[0],
                mode="osm",
                session=session,
            )
            osm_distances.append(final_distance)

            # with Pool(processes=4) as p:
            #     osm_distances = p.starmap(
            #         get_distance,
            #         zip(
            #             sequence[:-1],
            #             sequence[1:],
            #             [mode] * (len(sequence) - 1),
            #         ),
            #         # chunksize=10,
            #     )
            osm_distances.append(get_distance(sequence[-1], sequence[0], mode=mode))
        distances_km = [x[0] for x in osm_distances]
        durations_min = [x[1] for x in osm_distances]

        self.__setattr__(name, distances_km)
        return None

    def evaluate_driving_distances(
        self, planned=True, actual=True, mode="osm", multiprocessing=False
    ):
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

        Returns
        -------
        None
        """
        if planned:
            self.__calculate_driving_distances(
                [x.location for x in self.planned_sequence],
                "planned_driving_distances",
                mode,
                multiprocessing,
            )
            self.total_planned_driving_distance = sum(self.planned_driving_distances)
        if actual:
            self.__calculate_driving_distances(
                [x.location for x in self.actual_sequence],
                "actual_driving_distances",
                mode,
                multiprocessing,
            )
            self.total_actual_driving_distance = sum(self.actual_driving_distances)

        return None

    def evaluate_circuity_factor(self, planned=True, actual=True):
        """Evaluate the circuity factor of the route.

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
            self.planned_circuity_factors = [
                x / y if y != 0 else 0
                for x, y in zip(
                    self.planned_driving_distances, self.planned_euclidean_distances
                )
            ]
            self.mean_planned_circuity_factor = np.mean(self.planned_circuity_factors)
            self.total_planned_circuity_factor = (
                self.total_planned_driving_distance
                / self.total_planned_euclidean_distance
            )
        if actual:
            # Calculate the circuity factor of the actual sequence avoiding the
            # division by zero
            self.actual_circuity_factors = [
                x / y if y != 0 else 0
                for x, y in zip(
                    self.actual_driving_distances, self.actual_euclidean_distances
                )
            ]
            self.mean_actual_circuity_factor = np.mean(self.actual_circuity_factors)
            self.total_actual_circuity_factor = (
                self.total_actual_driving_distance
                / self.total_actual_euclidean_distance
            )

        return None

    # Analyzing routes orientation

    def evaluate_street_orientation(self, sequence):
        return None

    # Analyzing routes shape and area

    def evaluate_route_compactness(self, sequence):
        return None

    def evaluate_route_area(self):
        return None

    def evaluate_route_centroid(self, sequence):
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

    @classmethod
    def save_to_file(self, filename):
        return None
