class BoundingBox:
    """Auxiliary class to store bounding box information."""

    def __init__(self, name: str, lat1: float, lat2: float, lon1: float, lon2: float):
        """Constructor for the bbox class

        Parameters
        ----------
        name : str
            The name of the bounding box
        lat1 : float
            The minimum latitude of the bounding box
        lon1 : float
            The minimum longitude of the bounding box
        lat2 : float
            The maximum latitude of the bounding box
        lon2 : float
            The maximum longitude of the bounding box
        """
        self.name = name
        self.lat_min = min(lat1, lat2)
        self.lon_min = min(lon1, lon2)
        self.lat_max = max(lat1, lat2)
        self.lon_max = max(lon1, lon2)
