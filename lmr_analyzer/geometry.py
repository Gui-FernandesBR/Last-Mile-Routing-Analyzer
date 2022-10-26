# Define the geometry bu reading a shapefile
# define a method as --> def add_layer(self, layer):

import osmnx as ox


class geometry:
    def __init__(self, shapefile):
        """_summary_

        Parameters
        ----------
        shapefile : str
            The path to the shapefile.

        Returns
        -------
        None
        """
        self.shapefile = shapefile

        return None

    def add_layer(self, layer):
        return None

    def plot_layer(self, layer):
        return None

    def attribute_table(self):
        return None

    def plot_geometry(self):
        return None
