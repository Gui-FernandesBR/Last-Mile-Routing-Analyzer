def test_bounding_box_initialization(example_bbox):
    assert example_bbox.name == "TestBox"
    assert example_bbox.lat_min == 10.0
    assert example_bbox.lat_max == 20.0
    assert example_bbox.lon_min == 30.0
    assert example_bbox.lon_max == 40.0


def test_bounding_box_min_max_latitude(example_bbox):
    assert example_bbox.lat_min == 10.0
    assert example_bbox.lat_max == 20.0


def test_bounding_box_min_max_longitude(example_bbox):
    assert example_bbox.lon_min == 30.0
    assert example_bbox.lon_max == 40.0
