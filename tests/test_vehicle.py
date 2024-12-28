def test_vehicle_initialization(example_vehicle):
    assert example_vehicle.name == "Van"
    assert example_vehicle.capacity == 500.0


def test_vehicle_repr(example_vehicle):
    assert repr(example_vehicle) == "'Vehicle(name=Van, capacity=500.0)'"
