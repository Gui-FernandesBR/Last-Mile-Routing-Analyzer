__author__ = "Guilherme Fernandes Alves"


class stop:
    def __init__(
        self, name, location, location_type, time_window, planned_service_time, packages
    ):
        """_summary_

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
        packages : list # TODO: allow other formats
            A list containing the packages to be delivered at the stop.

        Returns
        -------
        None
        """
        # Save arguments as attributes
        self.name = name
        self.location = location
        self.location_type = location_type
        self.time_window = time_window
        self.packages = packages
        self.planned_service_time = planned_service_time

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
        self.delivery_time = self.time_window[1] - self.time_window[0]

        return None
