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
