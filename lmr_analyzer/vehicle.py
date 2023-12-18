"""This module contains the vehicle class, which is used to store information
about a vehicle. A vehicle is understood as a transportation unit that is used
to deliver packages to customers.
"""


class vehicle:
    """Class to store vehicle information"""

    def __init__(self, name, capacity):
        """Initializes the vehicle object.

        Parameters
        ----------
        name : str
            The name of the vehicle.
        capacity : scalar
            The capacity of the vehicle, in m^3.

        Returns
        -------
        None
        """

        self.name = name
        self.capacity = capacity
