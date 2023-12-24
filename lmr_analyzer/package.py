"""This module contains the Package class, which is used to store information
about a package. A package is understood as a product that is to be delivered
to a customer.
"""


class Package:
    """Class to store package information"""

    def __init__(
        self,
        name: str,
        dimensions: tuple,
        status: str,
        weight: float = 0,
        price: float = 0,
    ):
        """Initializes the Package object.

        Parameters
        ----------
        name : str
            The name of the package.
        dimensions : tuple
            A tuple containing the dimensions of the package. The tuple must be
            in the form (depth, height, width).
        status : str
            The status of the package. The status must be one of the following:
            'to-be-delivered', 'rejected', 'attempted', 'delivered'.
        weight : int, optional
            The weight of the package, in grams. The default is 0.
        price : int, optional
            The price of the package, in monetary units. The default is 0.
        """

        # Save arguments as attributes
        self.name, self.dimensions, self.status, self.weight, self.price = (
            name,
            dimensions,
            status,
            weight,
            price,
        )

        # Check if status is valid
        if status not in ["to-be-delivered", "rejected", "attempted", "delivered"]:
            raise ValueError(
                "Invalid package status: must be one of the following: "
                + "'to-be-delivered', 'rejected', 'attempted', 'delivered'."
            )

    @property
    def volume(self):
        """Calculates the volume of the package, given its dimensions.

        Parameters
        ----------
        None

        Returns
        -------
        float
            The volume of the package.
        """
        return self.dimensions[0] * self.dimensions[1] * self.dimensions[2]

    def modify_status(self, status):
        """Modifies the status of the package.

        Parameters
        ----------
        status : str
            The status of the package. The status must be one of the following:
            'rejected', 'attempted', 'delivered'.

        Returns
        -------
        None
        """
        self.status = status

    def print_info(self):
        """Prints the package information.

        Returns
        -------
        None
        """
        print(
            f"Package name: {self.name}\nDimensions: {self.dimensions}\nStatus: "
            + f"{self.status}\nWeight: {self.weight}\nPrice: {self.price}\n"
            + f"Volume: {self.volume}"
        )
