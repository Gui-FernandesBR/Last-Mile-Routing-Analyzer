__author__ = "Guilherme Fernandes Alves"
__license__ = "Mozilla Public License 2.0"

import osmnx as ox
import geopandas as gpd


class geometry:
    """
    This class is responsible for handling the geometry of the analysis.

    """

    def __init__(self, name, place=None, shapefile=None, bbox=None):
        """Initialize the geometry class.

        Parameters
        ----------
        name : str
            Name of the geometry.
        place : str, optional
            The name of the place to be analyzed. The default is None. If the
            place is not None, the shapefile and bbox parameters will be ignored.
        shapefile : str
            The path to the shapefile. This should point to the .shp file. If
            used with the place parameter, the place parameter will be ignored.
            If used with the bbox parameter, the bbox parameter will be used to
            cut the shapefile. The default is None.
        bbox : list, optional
            The bounding box of the geometry. [north, south, east, west]
            North and south are the latitude, east and west are the longitude
            boundaries of the geometry.

        Returns
        -------
        None
        """

        # Save arguments as attributes
        self.name = name
        self.place, self.shapefile, self.bbox = (place, shapefile, bbox)

        # Create the major graph
        if place is not None:
            self.__create_graph_from_place()
        else:
            if bbox and not shapefile:
                self.__create_graph_from_bbox()
            elif shapefile:
                self.__create_graphs_from_shapefile()
                if bbox:
                    self.__cut_graph_to_bbox()
            else:
                raise ValueError(
                    "You must provide either a shapefile, place query or a bounding box, otherwise there is no way to create the geometry."
                )

        return None

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

    # Evaluation and manipulation methods

    def evaluate_basic_stats(self):

        self.stats_dict = {}
        initial_cpu_time = process_time()
        output = display("Starting", display_id=True)

        for key, value in self.graphs.items():
            self.stats_dict[key] = ox.stats.basic_stats(
                value, area=None, clean_int_tol=None
            )
            output.update(
                f"Basic statistics for '{key}' calculated! Completed: {len(self.stats_dict)} of {self.number_of_polygons}",
            )
        # TODO: Discover how to get the area of the graph

        output.update(
            "Completed {} basic stats calculation using a total CPU time of: {:.1f} s".format(
                len(self.stats_dict),
                process_time() - initial_cpu_time,
            )
        )

        # Calculate the number of graphs created that are not None
        self.number_of_stats = len([graph for graph in self.graphs.values() if graph])
        self.basic_stats_quality_percentage = (
            100 * self.number_of_stats / self.number_of_polygons
        )
        print(
            f"It was possible to create a graph for {self.number_of_stats} of {self.number_of_polygons} polygons."
        )
        print(
            "Basic stats quality: {:.0f} %".format(self.basic_stats_quality_percentage)
        )

        self.__create_attribute_table()

        return None

    def __create_attribute_table(self):
        """Create a pandas data frame with the basic stats of each graph.

        Returns
        -------
        None
        """

        self.attribute_table = pd.DataFrame.from_dict(self.stats_dict, orient="index")
        names_list = [" ".join(x.split(" ", 2)[:2]) for x in list(self.graphs.keys())]
        self.attribute_table["name"] = names_list

        return None

    def evaluate_street_orientation(self):

        # Evaluate bearing at each and convert to a data frame
        self.edges_dict = {
            i: j.edges(keys=True, data=True) for i, j in self.graphs.items()
        }
        self.bearing_dict = {i: j["bearing"] for i, j in self.edges_dict.items()}

        return None

    # Plot methods

    def plot_attribute_table(self, x="name", y=None, kind="scatter", color="red"):
        """Plot the attribute table.

        Returns
        -------
        None
        """
        if self.attribute_table is None:
            raise ValueError(
                "The attribute table is empty, Please run the method 'evaluate_basic_stats' first."
            )

        # if x == "name":
        #     self.attribute_table.sort_values(y, ascending=False)
        # elif y == "name":
        #     self.attribute_table.sort_values(x, ascending=False)

        return self.attribute_table.plot(kind=kind, x=x, y=x, color=color)

    def plot_graphs(self, grid=True):

        if not grid:
            for key, value in self.graphs.items():
                if value is not None:
                    fig = plt.figure(figsize=(8, 8), clear=True)
                    ax = fig.add_subplot(111)
                    ox.plot_graph(
                        value,
                        ax=ax,
                        figsize=None,
                        bgcolor="#FFFFFF",
                        node_color="blue",
                        node_size=5,
                        node_alpha=None,
                        node_edgecolor="none",
                        node_zorder=1,
                        edge_color="#000000",
                        edge_linewidth=1,
                        edge_alpha=None,
                        show=False,
                        close=False,
                        save=False,
                        filepath=None,
                        dpi=300,
                        bbox=None,
                    )
                    ax.set_title(key)
                    plt.show()

            plt.close("all")
            return None

        # Find the number of rows and columns
        number_of_rows = int(np.ceil(np.sqrt(self.number_of_graphs)))
        number_of_columns = int(np.ceil(self.number_of_graphs / number_of_rows))

        # Create the figure
        fig, ax = plt.subplots(
            number_of_rows,
            number_of_columns,
            figsize=(20, 20),
            sharex=False,
            sharey=False,
        )
        title = self.place if self.place else self.shapefile
        fig.suptitle(f"Graphs from {title}", fontsize=16)

        # Plot the graphs
        ax_index = 0
        for key, value in self.graphs.items():
            if value is not None:
                ox.plot_graph(
                    value,
                    ax=ax[ax_index // number_of_columns, ax_index % number_of_columns],
                    figsize=None,
                    bgcolor="#FFFFFF",
                    node_color="blue",
                    node_size=5,
                    node_alpha=None,
                    node_edgecolor="none",
                    node_zorder=1,
                    edge_color="#000000",
                    edge_linewidth=1,
                    edge_alpha=None,
                    show=False,
                    close=False,
                    save=False,
                    filepath=None,
                    dpi=300,
                    bbox=None,
                )
                # fig.add_subplot(ox_ax)
                ax[
                    ax_index // number_of_columns, ax_index % number_of_columns
                ].set_title(" ".join(key.split(" ", 2)[:2]))
                ax_index += 1

        # Show the figure
        plt.tight_layout()
        plt.show()
        plt.close()

        return None

    def add_layer(self, layer):
        return None

    # Export methods

    def save_graphs_to_shapefile(self, path):
        """_summary_

        Parameters
        ----------
        graphs : list, dict, or osmnx.graph
            Can be a list of graphs, a dictionary of graphs, or a single graph.
        path : str
            The path to save the shapefile. This should not include the file format.

        Returns
        -------
        _type_
            _description_
        """

        for key, value in self.graphs.items():
            ox.save_graph_shapefile(value, filename=path + f"_{key}")

        return None

    def attribute_table(self):
        return None

    # Pickle object to save time in the future

    def save(self, filename="geometry"):
        """Save the geometry object to a file so it can be used later.

        Parameters
        ----------
        filename : str, optional
            Name of the file where to be saved, by default "geometry"
        Returns
        -------
        None
        """
        # Save the object using cloudpickle
        pickled_obj = cloudpickle.dumps(object)

        # Save the pickled route dict into a file
        with open(filename, "wb") as f:
            f.write(pickled_obj)
        print("Your geometry object was saved, check it out: " + filename)

        return None

    @classmethod
    def load(self, filename="geometry"):
        """Load a previously saved geometry pickled file.
        Example: city = geometry.load("filename").

        Parameters
        ----------
        filename : str, optional
            Name of the previous saved file, by default "geometry"
        Returns
        -------
        lmr_analyzer.geometry object
        """
        # Load the pickled object
        with open(filename, "rb") as f:
            pickled_obj = f.read()

        # Unpickle the object
        obj = cloudpickle.loads(pickled_obj)

        return obj
