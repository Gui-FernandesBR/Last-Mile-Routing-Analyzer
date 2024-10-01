from datetime import datetime

from lmr_analyzer.stop import Stop


def test_stop_object(example_stop):
    """Test the stop object by calling its main attributes

    Parameters
    ----------
    example_stop : stop
        Example stop object.
    """
    # Check if the object is a stop
    assert isinstance(example_stop, Stop)

    # Check if the object attributes are correct
    assert example_stop.name == "example_stop"
    assert example_stop.location == (0, 0)
    assert example_stop.location_type == "delivery"
    assert example_stop.time_window == (
        datetime(2022, 11, 20, 10),
        datetime(2022, 11, 20, 12),
    )
    assert example_stop.planned_service_time == 60
    assert len(example_stop.packages_list) == 2


def test_properties(example_stop):
    """Test all the properties of the stop object.

    Parameters
    ----------
    example_stop : stop
        Example stop object.
    """
    # Check if the delivery time is correct
    assert example_stop.delivery_time.seconds == 7200

    # Check if the number of delivered packages is correct
    assert example_stop.number_of_delivered_packages == 2

    # Check if the number of rejected packages is correct
    assert example_stop.number_of_rejected_packages == 0

    # Check if the number of failed attempted packages is correct
    assert example_stop.number_of_failed_attempted_packages == 0

    # Check if the number of to-be-delivered packages is correct
    assert example_stop.number_of_to_be_delivered_packages == 0

    # Check if the number of packages is correct
    assert example_stop.number_of_packages == 2

    # Check the total volume of the packages
    assert example_stop.total_volume_of_packages == 2

    # Check the total weight of the packages
    assert example_stop.total_weight_of_packages == 1

    # Check the average weight of the packages
    assert example_stop.average_weight_of_packages == 0.5

    # Check the total price of the packages
    assert example_stop.total_price_of_packages == 20

    # Check the average price of the packages
    assert example_stop.average_price_of_packages == 10
