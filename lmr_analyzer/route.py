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
