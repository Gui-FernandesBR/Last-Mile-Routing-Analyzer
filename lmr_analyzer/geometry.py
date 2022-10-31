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

    # Create graph methods

    def __create_graph_from_place(self):
        """Create the graph from the place name.

        Returns
        -------
        None
        """
        self.graphs = {
            self.place: ox.graph_from_place(
                self.place,
                network_type="drive",
                simplify=True,
                retain_all=False,
                truncate_by_edge=True,
                clean_periphery=True,
                custom_filter=None,
                retain_invalid=False,
                name=None,
                timeout=180,
                memory=None,
                max_query_area_size=50 * 1000 * 50 * 1000,
            )
        }

        return None

    def __create_graphs_from_shapefile(self):
        """Read the shapefile and save it as osmnx graph.

        Returns
        -------
        None

        Raises
        ------
        FileNotFoundError
            If the shapefile or shapefile associated files do not exist. Usually
            this means that the shapefile path is wrong. Check the path and try
            again. You should point to the .shp file, however, the other files
            should be in the same folder (e.g. .shx, .dbf, and .prj).
        """
        # Check if all files associated with the shapefile exist
        shapefile = self.shapefile  # Just to make the code more readable
        if shapefile is not None:
            if not os.path.exists(shapefile):
                raise FileNotFoundError("The shapefile does not exist.")
            if not os.path.exists(shapefile[:-3] + "shx"):
                raise FileNotFoundError("The shapefile index does not exist.")
            if not os.path.exists(shapefile[:-3] + "dbf"):
                raise FileNotFoundError("The shapefile database does not exist.")
            if not os.path.exists(shapefile[:-3] + "prj"):
                raise FileNotFoundError("The shapefile projection does not exist.")
        self.geo_data_frame = gpd.read_file(self.shapefile)  # .shp extension
        self.number_of_polygons = len(self.geo_data_frame.values)

        self.__create_multiple_graphs(keys="Name", values="geometry")

        return None

    def __create_graph_from_bbox(self):
        # north (float) – northern latitude of bounding box
        # south (float) – southern latitude of bounding box
        # east (float) – eastern longitude of bounding box
        # west (float) – western longitude of bounding box

        north, south, east, west = self.bbox  # Just to make the code more readable

        # Check if the bbox is valid
        if north < south:
            raise ValueError("The north latitude is smaller than the south latitude.")
        if east < west:
            raise ValueError("The east longitude is smaller than the west longitude.")

        self.graphs = ox.graph.graph_from_bbox(
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

        return None

    def __create_multiple_graphs(self, keys="Name", values="geometry"):
        """Create a graph for each minor geometry, usually a neighborhood.

        Parameters
        ----------
        keys : str, optional
            The attribute name to be used as keys, by default "Name"
        values : str, optional
            The attribute name to be used as values, by default "geometry"
        attribute_name : str, optional
            The name of the attribute to be used to store the separated geometries,
            by default "neighborhoods"

        Returns
        -------
        None
        """
        # Create a dictionary with the keys and values
        self.polygons = self.geo_data_frame.set_index(keys)[values].to_dict()

        # Save the number of minor geometries created
        self.number_of_polygons = len(self.polygons)

        # Get the dictionary with the minor geometries
        self.graphs = {}
        self.areas = {}
        initial_cpu_time = process_time()
        output = display("Starting", display_id=True)

        for key, value in self.polygons.items():
            # start_time = process_time()
            try:
                self.areas[key] = value.area
                self.graphs[key] = ox.add_edge_bearings(
                    ox.graph_from_polygon(
                        polygon=value,
                        network_type="drive",
                        simplify=False,
                        retain_all=True,
                        truncate_by_edge=False,
                        clean_periphery=True,
                        custom_filter=None,
                    )
                )
                output.update(
                    f"Graph for '{key}' created! Completed: {len(self.graphs)} of {self.number_of_polygons}",
                )
            except Exception as e:
                print(f"Error with {key}.")
                print(e)
                self.graphs[key] = None

        # Update the total time to create the graphs
        output.update(
            "Completed {:.0f} graphs using a total CPU time of: {:.1f} s".format(
                float(len(self.graphs)),
                process_time() - initial_cpu_time,
            )
        )

        # Calculate the number of graphs created that are not None
        self.number_of_graphs = len([graph for graph in self.graphs.values() if graph])
        self.shapefile_quality_percentage = (
            100 * self.number_of_graphs / self.number_of_polygons
        )
        print(
            f"It was possible to create a graph for {self.number_of_graphs} of {self.number_of_polygons} polygons."
        )
        print("Shapefile quality: {:.0f} %".format(self.shapefile_quality_percentage))

        return None

    def __cut_graph_to_bbox(self):
        """Cut the geometry using the bounding box.

        Returns
        -------
        _type_
            _description_
        """
        return None

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
