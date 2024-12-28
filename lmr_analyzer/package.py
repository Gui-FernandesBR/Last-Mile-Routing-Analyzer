from lmr_analyzer.enums import PackageStatus


class Package:
    """Class to store package information"""

    def __init__(
        self,
        name: str,
        dimensions: tuple[float, float, float],  # depth, height, width
        status: PackageStatus,
        weight: float = 0,
        price: float = 0,
    ):
        """Initializes the Package object."""

        self.name = name
        self.dimensions = dimensions
        self.status = status
        self.weight = weight
        self.price = price

        self.__validate_status()

    def __validate_status(self):
        if self.status not in PackageStatus.get_members():
            raise ValueError(
                f"Invalid package status '{self.status}'. "
                f"Must be one of the following: {PackageStatus.get_members()}"
            )

    @property
    def volume(self) -> float:
        """The volume of the package given its dimensions."""
        return self.dimensions[0] * self.dimensions[1] * self.dimensions[2]

    def modify_status(self, status: PackageStatus) -> None:
        """Modifies the status of the package."""
        self.status = status

    def print_info(self) -> None:
        """Prints the package information to the console."""

        print(f"Package name: {self.name}")
        print(f"Dimensions: {self.dimensions}")
        print(f"Status: {self.status}")
        print(f"Weight: {self.weight}")
        print(f"Price: {self.price}")
        print(f"Volume: {self.volume}")
