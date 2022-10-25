__author__ = "Guilherme Fernandes Alves"

from .stop import stop

# from .vehicle import vehicle


class route:
    def __init__(self, name):

        # Save arguments as attributes
        self.name = name

        # Initialize other attributes
        self.actual_sequence = []
        self.actual_sequence_names = []
        self.planned_sequence = []
        self.planned_sequence_names = []
        self.vehicle = None
        self.number_of_planned_stops = 0
        self.number_of_actual_stops = 0

        return None

    def set_planned_sequence(self, sequence, mode="fast"):
        """Set the planned sequence of the route. The planned sequence is the
        sequence of stops that the route is supposed to follow, usually
        determined by the route planner.

        Parameters
        ----------
        sequence : list
            A list containing the stops that the route is supposed to follow.
        mode : str, optional
            Define wether to check for types of sequence items or not, by default
            "fast". The other option is "safe", which will check for types over
            the entire sequence.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            In case at least one of the items in the sequence is not of type
            stop.
        """
        # TODO: Document here later
        if mode == "safe":  # Other option if 'fast'
            if all(isinstance(x, stop) for x in sequence):
                self.sequence = sequence
            else:
                raise ValueError(
                    "Invalid sequence: all elements must be of type vehicle."
                )
        else:
            self.planned_sequence = sequence

        self.planned_sequence_names = [x.name for x in self.planned_sequence]
        self.number_of_planned_stops = len(self.planned_sequence)

        return None

    def set_actual_sequence(self, sequence, mode="fast"):

        if mode == "safe":  # Other option if "fast"
            if all(isinstance(x, stop) for x in sequence):
                self.sequence = sequence
            else:
                raise ValueError(
                    "Invalid sequence: all elements must be of type vehicle."
                )
        else:
            self.actual_sequence = sequence

        self.actual_sequence_names = [x.name for x in self.actual_sequence]
        self.number_of_actual_stops = len(self.actual_sequence)
        self.actual_sequence_compactness = self.evaluate_route_compactness(
            self.actual_sequence
        )

        return None
