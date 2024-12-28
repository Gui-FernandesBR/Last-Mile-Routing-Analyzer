import json

import numpy as np
import pytest

from lmr_analyzer.distance_matrix import DistanceMatrix


def test_calculate_matrix_statistics():
    distances = [5.0, 15.0, 25.0]
    dm = DistanceMatrix()
    dm.distances = distances
    dm.calculate_matrix_statistics()

    assert dm.max_distance == 25.0
    assert dm.min_distance == 5.0
    assert dm.average_distance == 15.0
    assert dm.std_distance == np.std(distances)
