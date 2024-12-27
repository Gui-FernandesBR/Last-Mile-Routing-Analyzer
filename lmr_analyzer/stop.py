from datetime import datetime
from typing import Tuple

from lmr_analyzer.enums import LocationType
from lmr_analyzer.package import Package, PackageStatus


class Stop:
    """
    Class to hold the information of a stop. A stop is a location where a
    vehicle must stop to either pick up or deliver packages. The stop can be a
    depot, a pickup location, or a delivery location.
    """

    def __init__(
        self,
        name: str,
        location: Tuple[float, float],  # lat, lon
        location_type: LocationType,
        time_window: Tuple[datetime, datetime],
        packages: list[Package],
    ):
        """Initializes the stop object."""
        self.name = name
        self.location = location
        self.location_type = location_type
        self.time_window = time_window
        self.packages = packages

        self.__validate_time_window()
        self.__validate_location_type()

        self.__initialize_packages_list()
        self.__initialize_status_list()

    def __validate_time_window(self):
        if self.time_window[0] > self.time_window[1]:
            raise ValueError(
                "Invalid time window: start time is greater than end time."
            )

    def __validate_location_type(self):
        if self.location_type not in ["depot", "pickup", "delivery"]:
            raise ValueError(
                "Invalid stop location type: must be one of the following: "
                "'depot', 'pickup', 'delivery'."
            )

    def __initialize_packages_list(self):
        if isinstance(self.packages, dict):
            self.packages_list = list(self.packages.values())
        elif isinstance(self.packages, list) and all(
            isinstance(pck, Package) for pck in self.packages
        ):
            self.packages_list = self.packages
        else:
            raise TypeError("Invalid packages type: must be a list or a dictionary.")

    def __initialize_status_list(self):
        self.status_list: list[PackageStatus] = [
            package.status for package in self.packages_list
        ]

    @property
    def delivery_time(self):
        return self.time_window[1] - self.time_window[0]

    @property
    def number_of_delivered_packages(self) -> int:
        return self.status_list.count("delivered")

    @property
    def number_of_rejected_packages(self) -> int:
        return self.status_list.count("rejected")

    @property
    def number_of_failed_attempted_packages(self) -> int:
        return self.status_list.count("attempted")

    @property
    def number_of_to_be_delivered_packages(self) -> int:
        return self.status_list.count("to-be-delivered")

    @property
    def number_of_packages(self) -> int:
        """The number of packages at the stop."""
        return len(self.packages)

    @property
    def total_volume_of_packages(self) -> float:
        """The total volume of the packages at the stop."""
        return sum(package.volume for package in self.packages_list)

    @property
    def average_volume_of_packages(self) -> float:
        """The average volume per package at the stop."""
        return (
            self.total_volume_of_packages / len(self.packages_list)
            if len(self.packages_list) > 0
            else 0
        )

    @property
    def total_volume_of_delivered_packages(self) -> float:
        """The total volume of the delivered packages at the stop."""
        return sum(
            package.volume
            for package in self.packages_list
            if package.status == PackageStatus.DELIVERED.value
        )

    @property
    def total_volume_of_rejected_packages(self) -> float:
        """The total volume of the rejected packages at the stop."""
        return sum(
            package.volume
            for package in self.packages_list
            if package.status == "rejected"
        )

    @property
    def total_volume_of_failed_attempted_packages(self) -> float:
        """Returns the total volume of the packages at the stop."""
        return sum(
            package.volume
            for package in self.packages_list
            if package.status == "attempted"
        )

    @property
    def total_weight_of_packages(self) -> float:
        """The total weight of the packages at the stop."""
        return sum(package.weight for package in self.packages_list)

    @property
    def average_weight_of_packages(self) -> float:
        """The average weight of the packages at the stop."""
        return (
            self.total_weight_of_packages / len(self.packages_list)
            if len(self.packages_list) > 0
            else 0
        )

    @property
    def total_price_of_packages(self) -> float:
        """The total price of the packages at the stop."""
        return sum(package.price for package in self.packages_list)

    @property
    def average_price_of_packages(self) -> float:
        """Returns the average price of the packages at the stop."""
        return (
            self.total_price_of_packages / len(self.packages_list)
            if len(self.packages_list) > 0
            else 0
        )
