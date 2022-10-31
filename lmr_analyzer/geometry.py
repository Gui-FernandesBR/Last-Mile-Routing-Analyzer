__author__ = "Guilherme Fernandes Alves"
__license__ = "Mozilla Public License 2.0"

import osmnx as ox
import geopandas as gpd


class geometry:
    def __init__(self, shapefile=None, bbox=None):
        """_summary_

        Parameters
        ----------
        shapefile : str
            The path to the shapefile.
        bbox : list, optional
            The bounding box of the geometry. [north, south, east, west]
            North and south are the latitude, east and west are the longitude
            boundaries of the geometry.

        Returns
        -------
        None
        """
        # Save arguments as attributes
        self.shapefile = shapefile
        self.bbox = bbox

        # Initialize other attributes
        self.geometry = None

        # Calculate additional attributes
        if bbox and not shapefile:
            self.create_geometry_from_bbox(bbox)
        elif shapefile and not bbox:
            self.read_shapefile(shapefile)

        return None

    def read_shapefile(self, shapefile):
        self.geometry = gpd.read_file(shapefile)  # .shp extension
        return None

    def create_geometry_from_bbox(self, bbox):
        # north (float) – northern latitude of bounding box
        # south (float) – southern latitude of bounding box
        # east (float) – eastern longitude of bounding box
        # west (float) – western longitude of bounding box

        north, south, east, west = bbox

        # Check if the bbox is valid
        if north < south:
            raise ValueError("The north latitude is smaller than the south latitude.")
        if east < west:
            raise ValueError("The east longitude is smaller than the west longitude.")

        self.geometry = ox.graph.graph_from_bbox(
            north=north,
            south=south,
            east=east,
            west=west,
            network_type="drive",
            simplify=False,
            retain_all=True,
            truncate_by_edge=False,
            clean_periphery=True,
            custom_filter=None,
        )

        # # save our graph in shapefile
        # ox.save_graph_shapefile(self.geometry,
        #                         filepath=None,
        #                         encoding='utf-8',
        #                         directed=False)

        # simply plot our graph

        # ox.plot_graph(self.geometry,
        #       ax=None,
        #       figsize=(20, 20),
        #       bgcolor='#111111',
        #       node_color='w',
        #       node_size=0,
        #       node_alpha=None,
        #       node_edgecolor='none',
        #       node_zorder=1,
        #       edge_color='#999999',
        #       edge_linewidth=1,
        #       edge_alpha=None,
        #       show=True,
        #       close=False,
        #       save=False,
        #       filepath=None,
        #       dpi=600,
        #       bbox=None)

        # ox.stats.basic_stats(self.geometry,
        #              area=None,
        #              clean_int_tol=None,
        #              clean_intersects=None,
        #              tolerance=None,
        #              circuity_dist=None)

        return None

    def add_layer(self, layer):
        return None

    def plot_layer(self, layer):
        return None

    def attribute_table(self):
        return None

    def plot_geometry(self):
        return None
