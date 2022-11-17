__author__ = "Guilherme Fernandes Alves"
__license__ = "Mozilla Public License 2.0"

import csv
import json

import numpy as np


# TODO: Implement this fucking shit
class distance_matrix:
    """A class to either calculate or load distance matrices. A distance matrix
    is used to store the distance between each origin and destination node.
    Usually, the computation of such matrices is very expensive, so it is
    recommended to save the matrices to a file and load them when needed.
    """

    def __init__(self, matrix=None, origins=None, destinations=None, sequence=None):
        """Initializes the distance matrix class.

        Parameters
        ----------
        matrix : dict, optional
            Distance matrix as a python dictionary, by default None.
            If None, the matrix will be calculated from zero based on the
            origins and destinations points. If not None, the matrix will be
            loaded from the dictionary and the analysis will be already done.
            The dictionary must have the following structure:
            {
                "origin_1": {
                    "destination_1": distance,
                    "destination_2": distance,
                    ...
                },
        origins : dict, optional
            Dictionary containing the origins points coordinates, by default None.
            If None, the code will understand that the matrix is already
            loaded and there's no need to know the coordinates of the
            origins.
            The dictionary must have the following structure:
            {
                "origin_1": {
                    "name": "origin_1_name",
                    "latitude": latitude,
                    "longitude": longitude
                },
                "origin_2": {
                    "name": "origin_2_name",
                    "latitude": latitude,
                    "longitude": longitude
                },
                ...
            }
        destinations : dict, optional
            Dictionary containing the destination points coordinates, by default None.
            If None, the code will understand that the matrix is already
            loaded and there's no need to know the coordinates of the
            destinations.
            The dictionary must have the following structure:
            {
                "destination_1": {
                    "name": name,
                    "latitude": latitude,
                    "longitude": longitude
                },
                "destination_2": {
                    "name": name,
                    "latitude": latitude,
                    "longitude": longitude
                },
                ...
            }
        sequence : dict, optional
            Dictionary describing the sequence or sequences that will be used to
            evaluate the distances, by default None.
            If None, the full distance matrix will be performed.
            The dictionary must have the following structure:
            {
                "sequence_1": [origin_1, destination_1, destination_2, ...],
                "sequence_2": [origin_2, destination_1, destination_2, ...],
                ...
            }

        Returns
        -------
        None
        """
        # Save the parameters as attributes
        self.matrix, self.origins, self.destinations, self.sequences = (
            matrix,
            origins,
            destinations,
            sequence,
        )

        if self.matrix is not None:
            # A matrix was passed, let's evaluate and return
            self.matrix_statistics()
            self.origins_names = list(self.matrix.keys())
            self.destinations_names = list(self.matrix[self.origins_names[0]].keys())

        return None

    def load_support_matrix_file(self, filename):
        """Loads a support matrix file. A support matrix file is a file containing
        the distance matrix and the origins and destinations coordinates. This
        function will load the file and save the matrix, origins and destinations
        as attributes. This can significantly reduce the time needed to perform
        the distance matrix generation.

        Parameters
        ----------
        filename : str,
            The name of the file containing the support matrix. The file must
            be a csv file with the following structure:
            route, stop, lat, lon, distance_to_next_stop(km), duration(min)

        Returns
        -------
        None
        """

        # Open and read the csv file
        try:
            with open(filename, "r") as f:
                # Read the csv file, skipping the header and convert to a list
                reader = csv.reader(f)
                matrix = next(reader)
                matrix = list(reader)
        except FileNotFoundError:
            print("File not found!")
            return None

        n_rows = len(matrix)
        route = matrix[1][0]
        inner_dict = {}
        routes_matrix = {}

        for i in range(1, n_rows - 1):
            inner_dict[matrix[i][1]] = {
                "latitude": matrix[i][2],
                "longitude": matrix[i][3],
                "distance_to_next(km)": matrix[i][4],
                "duration_to_next(min)": matrix[i][5],
            }
            try:
                if matrix[i + 1][0] == route:  # if the next route is the same
                    pass
                else:
                    routes_matrix[route] = inner_dict
                    route = matrix[i + 1][0]
                    inner_dict = {}
            except IndexError:  # If we are at the last row
                inner_dict[matrix[i][1]] = {
                    "latitude": matrix[i][2],
                    "longitude": matrix[i][3],
                    "distance_to_next(km)": matrix[i][4],
                    "duration_to_next(min)": matrix[i][5],
                }
                routes_matrix[route] = inner_dict

        self.routes_matrix = routes_matrix

        # Create the distance matrix in the format required by the class
        self.matrix = {}
        self.origins = {}
        self.destinations = {}

        # TODO: The next loops can be optimized
        for route in self.routes_matrix.keys():
            for origin in self.routes_matrix[route].keys():
                self.origins[origin] = {
                    "name": origin,
                    "latitude": self.routes_matrix[route][origin]["latitude"],
                    "longitude": self.routes_matrix[route][origin]["longitude"],
                }
                self.matrix[f"{origin}-{route}"] = {}
                for destination in self.routes_matrix[route].keys():
                    self.destinations[destination] = {
                        "name": destination,
                        "latitude": self.routes_matrix[route][destination]["latitude"],
                        "longitude": self.routes_matrix[route][destination][
                            "longitude"
                        ],
                    }
                    self.matrix[f"{origin}-{route}"][destination] = self.routes_matrix[
                        route
                    ][destination]["distance_to_next(km)"]

        print("Awesome, the distance matrix loaded successfully!")
        print("The routes matrix was also loaded and saved as an attribute.")

        return None
