__author__ = "Guilherme Fernandes Alves"

from .stop import stop

# from .vehicle import vehicle


class route:
    def __init__(self, name, stops):
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
        self.name = name
        self.stops = stops

        # Initialize other attributes
        self.actual_sequence = []
        self.actual_sequence_names = []
        self.planned_sequence = []
        self.planned_sequence_names = []
        self.vehicle = None
        self.number_of_planned_stops = 0
        self.number_of_actual_stops = 0

        # Calculate other attributes
        if isinstance(stops, list):
            self.stops_names = [x.name for x in self.stops]
            self.number_of_stops = len(self.stops)
        elif isinstance(stops, dict):
            self.stops_names = list(self.stops.keys())
            self.number_of_stops = len(self.stops_names)
        else:
            raise ValueError("Invalid stops: must be a list or dictionary of stops.")

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

    def get_vehicle(self):
        return self.vehicle

    def evaluate_sequence_adherence(self):
        pass

    def evaluate_route_status(self):
        pass

    # @classmethod
    def evaluate_circuity_factor(self, sequence):
        pass

    def evaluate_street_orientation(self, sequence):
        pass

    # @classmethod
    def evaluate_route_compactness(self, sequence):
        pass
        # return compactness

    def print_info(self):
        pass

    def plot_route(self, return_figure=False):
        pass

    def plot_stops(self, return_figure=False):
        pass
