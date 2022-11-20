__author__ = "Guilherme Fernandes Alves"
__email__ = "gf10.alves@gmail.com"
__license__ = "Mozilla Public License 2.0"

from .package import package


class stop:
    """Class to hold the information of a stop.

    Attributes
    ----------
    name : str
        The name of the stop.
    location : tuple
        A tuple containing the coordinates of the stop. The tuple must be
        in the form (latitude, longitude).
    location_type : str
        The location_type of the stop. The location_type must be one of the following:
        'depot', 'pickup', 'delivery'.
    time_window : tuple
        A tuple containing the time window of the stop. The tuple must be
        in the form (start_time, end_time).
    packages : list, dict
        A list or a dictionary containing the packages to be delivered at the stop.
    packages_list : list
        A list containing the packages to be delivered at the stop.

    Properties
    ----------
    delivery_time : float
        The delivery time of the stop.
    ...

    """

    # TODO: Document the class and its methods.
    def __init__(
        self, name, location, location_type, time_window, planned_service_time, packages
    ):
        """Initializes the stop object.

        Parameters
        ----------
        name : str
            The name of the stop.
        location : tuple
            A tuple containing the coordinates of the stop. The tuple must be
            in the form (latitude, longitude).
        location_type : str
            The location_type of the stop. The location_type must be one of the following:
            'depot', 'pickup', 'delivery'.
        time_window : tuple
            A tuple containing the time window of the stop. The tuple must be
            in the form (start_time, end_time).
        planned_service_time : float
            The planned service time of the stop.
        packages : list, dict
            A list or a dictionary containing the packages to be delivered at the stop.

        Returns
        -------
        None
        """
        # Save arguments as attributes
        (
            self.name,
            self.location,
            self.location_type,
            self.time_window,
            self.packages,
            self.planned_service_time,
        ) = (
            name,
            location,
            location_type,
            time_window,
            packages,
            planned_service_time,
        )

        # Check if time window is valid
        if time_window[0] > time_window[1]:
            raise ValueError(
                "Invalid time window: start time is greater than end time."
            )
        # Check if location type is valid
        if location_type not in ["depot", "pickup", "delivery"]:
            raise ValueError(
                "Invalid stop location type: must be one of the following: 'depot', 'pickup', 'delivery'."
            )

        # Evaluate other attributes
        ## Create packages list
        if isinstance(packages, dict):
            self.packages_list = list(packages.values())
        elif isinstance(packages, list) and all(
            isinstance(pck, package) for pck in packages
        ):
            self.packages_list = packages
        else:
            raise TypeError("Invalid packages type: must be a list or a dictionary.")

        # The self.status_list will be used by the properties
        self.status_list = [package.status for package in self.packages_list]

        return None

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
        """Returns the number of packages at the stop.

        Returns
        -------
        int
            The number of packages at the stop.
        """
        # Count the number of packages
        return len(self.packages)

    @property
    def total_volume_of_packages(self) -> float:
        """Returns the total volume of the packages at the stop.

        Returns
        -------
        float
            The total volume of the packages at the stop.
        """
        # Count the total volume of the packages
        return sum([package.volume for package in self.packages_list])

    @property
    def average_volume_of_packages(self) -> float:
        """Returns the average volume of the packages at the stop.

        Returns
        -------
        float
            The average volume of the packages at the stop.
        """
        # Count the average volume of the packages
        return (
            self.total_volume_of_packages / len(self.packages_list)
            if len(self.packages_list) > 0
            else 0
        )

    @property
    def total_volume_of_delivered_packages(self) -> float:
        """Returns the total volume of the delivered packages at the stop.

        Returns
        -------
        float
            The total volume of the delivered packages at the stop.
        """
        # Count the total volume of the delivered packages
        return sum(
            [
                package.volume
                for package in self.packages_list
                if package.status == "delivered"
            ]
        )

    @property
    def total_volume_of_rejected_packages(self) -> float:
        """Returns the total volume of the rejected packages at the stop.

        Returns
        -------
        float
            The total volume of the rejected packages at the stop.
        """
        # Count the total volume of the rejected packages
        return sum(
            [
                package.volume
                for package in self.packages_list
                if package.status == "rejected"
            ]
        )

    @property
    def total_volume_of_failed_attempted_packages(self) -> float:
        """Returns the total volume of the packages at the stop.

        Returns
        -------
        float
            The total volume of the packages at the stop.
        """
        # Count the total volume of the packages
        return sum(
            [
                package.volume
                for package in self.packages_list
                if package.status == "attempted"
            ]
        )

    @property
    def total_volume_of_packages(self) -> float:
        """Returns the total volume of the packages at the stop.

        Returns
        -------
        float
            The total volume of the packages at the stop.
        """
        # Count the total volume of the packages
        return sum(
            [
                package.volume
                for package in self.packages_list
                if package.status == "to-be-delivered"
            ]
        )

    @property
    def total_weight_of_packages(self) -> float:
        """Returns the total weight of the packages at the stop.

        Returns
        -------
        float
            The total weight of the packages at the stop.
        """
        # Count the total weight of the packages
        return sum([package.weight for package in self.packages_list])

    @property
    def average_weight_of_packages(self) -> float:
        """Returns the average weight of the packages at the stop.

        Returns
        -------
        float
            The average weight of the packages at the stop.
        """
        # Count the average weight of the packages
        return (
            self.total_weight_of_packages / len(self.packages_list)
            if len(self.packages_list) > 0
            else 0
        )

    @property
    def total_price_of_packages(self) -> float:
        """Returns the total price of the packages at the stop.

        Returns
        -------
        float
            The total price of the packages at the stop.
        """
        # Count the total price of the packages
        return sum([package.price for package in self.packages_list])

    @property
    def average_price_of_packages(self) -> float:
        """Returns the average price of the packages at the stop.

        Returns
        -------
        float
            The average price of the packages at the stop.
        """
        # Count the average price of the packages
        return (
            self.total_price_of_packages / len(self.packages_list)
            if len(self.packages_list) > 0
            else 0
        )
