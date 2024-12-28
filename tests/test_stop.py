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
    assert len(example_stop.packages_list) == 2


class TestStopProperties:

    def test_delivery_time(self, example_stop):
        assert example_stop.delivery_time.seconds == 7200

    def test_number_of_delivered_packages(self, example_stop):
        assert example_stop.number_of_delivered_packages == 2

    def test_number_of_rejected_packages(self, example_stop):
        assert example_stop.number_of_rejected_packages == 0

    def test_number_of_failed_attempted_packages(self, example_stop):
        assert example_stop.number_of_failed_attempted_packages == 0

    def test_number_of_to_be_delivered_packages(self, example_stop):
        assert example_stop.number_of_to_be_delivered_packages == 0

    def test_number_of_packages(self, example_stop):
        assert example_stop.number_of_packages == 2

    def test_total_volume_of_packages(self, example_stop):
        assert example_stop.total_volume_of_packages == 2

    def test_average_volume_of_packages(self, example_stop):
        assert example_stop.total_weight_of_packages == 1

    def test_total_weight_of_packages(self, example_stop):
        assert example_stop.average_weight_of_packages == 0.5

    def test_total_price_of_packages(self, example_stop):
        assert example_stop.total_price_of_packages == 20

    def test_average_price_of_packages(self, example_stop):
        assert example_stop.average_price_of_packages == 10

    def test_total_volume_of_failed_attempted_packages(self, example_stop):
        assert example_stop.total_volume_of_failed_attempted_packages == 0

    def test_total_volume_of_rejected_packages(self, example_stop):
        assert example_stop.total_volume_of_rejected_packages == 0

    def test_total_volume_of_delivered_packages(self, example_stop):
        assert example_stop.total_volume_of_delivered_packages == 2

    def test_average_volume_of_packages(self, example_stop):
        assert example_stop.average_volume_of_packages == 1
