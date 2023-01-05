__author__ = "Guilherme Fernandes Alves"
__email__ = "gf10.alves@gmail.com"
__license__ = "Mozilla Public License 2.0"


class package:
    """Class to store package information"""

    def __init__(
        self,
        name: str,
        dimensions: tuple,
        status: str,
        weight: float = 0,
        price: float = 0,
    ):
        """_summary_

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
                "Invalid package status: must be one of the following: 'to-be-delivered', 'rejected', 'attempted', 'delivered'."
            )

        return None

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
        return None

    def print_info(self):
        """Prints the package information.

        Returns
        -------
        None
        """
        print(
            f"Package name: {self.name}\nDimensions: {self.dimensions}\nStatus: {self.status}\nWeight: {self.weight}\nPrice: {self.price}\nVolume: {self.volume}"
        )
        return None