import os
from time import process_time
from typing import Tuple

import cloudpickle
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import osmnx as ox
import pandas as pd
from IPython.display import display

# plt.style.use("seaborn-v0_8-dark-palette")


class Geometry:
    """This class is responsible for handling the geometry of the analysis."""

    def __init__(
        self,
        name: str,
        place=None,
        shapefile=None,
        bbox=None,
        graph_key: str = "Name",
        polygon=None,
    ):
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
        """

        # Save arguments as attributes
        self.name, self.graph_key = name, graph_key
        self.place, self.shapefile, self.bbox = (place, shapefile, bbox)

        # Create the major graph
        if place is not None:
            self.__create_graph_from_place()
        else:
            if bbox and not shapefile:
                self.__create_graph_from_bbox()
            elif polygon:
                self.__create_graph_from_polygon(polygon)
            elif shapefile:
                self.__create_graphs_from_shapefile()
            else:
                raise ValueError(
                    "You must provide either a shapefile, place query or a bounding "
                    "box, otherwise there is no way to create the geometry."
                )

        self.bearing_dict = None

    # Create graph methods

    def __create_graph_from_place(self) -> None:
        """Create the graph from the place name."""
        self.graphs = {
            self.place: ox.graph_from_place(
                self.place,
                network_type="drive",
                simplify=True,
                retain_all=False,
                truncate_by_edge=True,
                clean_periphery=True,
                custom_filter=None,
            )
        }

    def __create_graphs_from_shapefile(self):
        """Read the shapefile and save it as osmnx graph."""
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

        self.__create_multiple_graphs(keys=self.graph_key, values="geometry")

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

    def __create_multiple_graphs(self, keys="Name", values="geometry"):
        """Create a graph for each minor geometry, usually a neighborhood.

        Parameters
        ----------
        keys : str, optional
            The attribute name to be used as keys, by default "Name"
        values : str, optional
            The attribute name to be used as values, by default "geometry"
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
            f"Completed {len(self.graphs):.0f} graphs using a total CPU time of: "
            f"{process_time() - initial_cpu_time:.1f} s"
        )

        # Calculate the number of graphs created that are not None
        self.number_of_graphs = len([graph for graph in self.graphs.values() if graph])
        self.shapefile_quality_percentage = (
            100 * self.number_of_graphs / self.number_of_polygons
        )
        print(
            f"It was possible to create a graph for {self.number_of_graphs} of "
            f"{self.number_of_polygons} polygons."
        )
        print(f"Shapefile quality: {self.shapefile_quality_percentage:.0f} %")

    def __create_graph_from_polygon(self, polygon):
        graph = ox.graph_from_polygon(
            polygon, network_type="drive", truncate_by_edge=True
        )
        if not graph:
            raise ValueError("The polygon is not valid. Please check input.")
        self.graphs = {self.name: graph}
        self.number_of_polygons = 1

    # Evaluation and manipulation methods

    def evaluate_basic_stats(self):
        self.stats_dict = {}
        initial_cpu_time = process_time()
        # output = display("Starting", display_id=True)

        for key, value in self.graphs.items():
            try:
                self.stats_dict[key] = ox.stats.basic_stats(
                    value, area=None, clean_int_tol=None
                )
                # output.update(
                #     f"Basic statistics for '{key}' calculated! Completed: {len(self.stats_dict)} of {self.number_of_polygons}",
                # )
            except Exception as e:
                print(f"Error with {key}.")
                print(e)
                self.stats_dict[key] = None
        # TODO: Discover how to get the area of the graph

        # output.update(
        #     "Completed {} basic stats calculation using a total CPU time of: {:.1f} s".format(
        #         len(self.stats_dict),
        #         process_time() - initial_cpu_time,
        #     )
        # )

        # Calculate the number of graphs created that are not None
        self.number_of_stats = len([graph for graph in self.graphs.values() if graph])
        self.basic_stats_quality_percentage = (
            100 * self.number_of_stats / self.number_of_polygons
        )
        # print(
        #     f"It was possible to create a graph for {self.number_of_stats} of {self.number_of_polygons} polygons."
        # )
        # print(
        #     f"Basic stats quality: {self.basic_stats_quality_percentage:.0f} %"
        # )

    def create_attribute_table(self) -> None:
        """Create a pandas data frame with the basic stats of each graph."""

        self.attribute_table = pd.DataFrame.from_dict(self.stats_dict, orient="index")
        # Join data from the areas dictionary
        self.attribute_table = self.attribute_table.join(
            pd.DataFrame.from_dict(self.areas, orient="index", columns=["area"])
        )
        # Join data from the street_orientation_dict
        self.attribute_table = self.attribute_table.join(
            pd.DataFrame.from_dict(self.street_orientation_dict, orient="index")
        )

        names_list = [" ".join(x.split(" ", 2)[:2]) for x in list(self.graphs.keys())]
        self.attribute_table["name"] = names_list

    def evaluate_street_orientation(self) -> None:
        """Evaluate the street orientation of each graph."""
        street_orientation_dict = {}

        # Add edge bearings to graph
        # Add time to process
        initial_cpu_time = process_time()
        # output = display("Starting", display_id=True)
        for key, graph in self.graphs.items():
            # Update the display
            # output.update(
            #     f"Street orientation for '{key}' calculated! Completed: {len(street_orientation_dict)} of {self.number_of_polygons}",
            # )
            try:
                graph = ox.add_edge_bearings(graph)
            except Exception as e:
                print(f"Error with {key}.")
                print(e)
                street_orientation_dict[key] = None
                continue

            bearings = pd.Series(
                [edge[3].get("bearing") for edge in graph.edges(keys=True, data=True)]
            )
            original_bearings = bearings.copy()

            # Calculate the mean and standard deviation of the bearings
            bins = np.arange(0, 180, 10)
            # Find the center of each bin
            bin_centers = bins[:-1] + np.diff(bins) / 2
            # Find the cosine and sine of the center of each bin
            bin_cos = np.cos(np.deg2rad(bin_centers))

            # Iterate through the bearings and if the angle is greater than 180, subtract 180
            for index, value in enumerate(bearings):
                if value > 180:
                    bearings[index] = value - 180

            # Count the number of edges in each bearing bin
            counts = bearings.groupby(pd.cut(bearings, bins), observed=False).count()

            # Calculate the mean and standard deviation of the bearings counts
            mean = np.sum(counts * bin_cos) / np.sum(counts)
            std = np.sqrt(np.sum(counts * (bin_cos - mean) ** 2) / np.sum(counts))

            # Calculate the skewness of the bearings counts
            skew = np.sum(counts * (bin_cos - mean) ** 3) / np.sum(counts) / std**3

            # Calculate the kurtosis of the bearings counts
            kurt = np.sum(counts * (bin_cos - mean) ** 4) / np.sum(counts) / std**4

            # Count the total number of edges
            total = counts.sum()

            # The number if it was an uniform distribution
            uniform = total / len(bins) * np.ones(len(bins) - 1)

            # Calculate the absolute deviation from the uniform distribution
            deviation = np.abs(counts - uniform) / uniform
            # deviation = deviation / uniform.max()
            mean_deviation = np.mean(deviation)
            # Sum the quadratic deviation from the uniform distribution
            sum_deviation = np.sum(deviation**2)

            # Get the dominant direction
            dominant_direction = counts.idxmax()
            # Get the second dominant direction
            second_dominant_direction = counts.drop(dominant_direction).idxmax()

            # Calculate the percentage of edges in the dominant direction
            dominant_percentage = counts[dominant_direction] / counts.sum() * 100

            # Calculate the percentage of edges in the second dominant direction
            second_dominant_percentage = (
                counts[second_dominant_direction] / counts.sum() * 100
            )

            # Add the results to the dictionary
            street_orientation_dict[key] = {
                "graph": graph,
                "bearings_0_180": bearings,
                "bearings_0_360": original_bearings,
                "counts_0_180": counts,
                "dominant_direction": dominant_direction,
                "second_dominant_direction": second_dominant_direction,
                "dominant_percentage": dominant_percentage,
                "second_dominant_percentage": second_dominant_percentage,
                "uniform_value": uniform.max(),
                "mean_deviation": mean_deviation,
                "quadratic_sum_deviation": sum_deviation,
                "mean": mean,
                "std": std,
                "skew": skew,
                "kurt": kurt,
            }

        # output.update(
        #     "Completed {} street orientation calculation using a total CPU time of: {:.1f} s".format(
        #         len(street_orientation_dict),
        #         process_time() - initial_cpu_time,
        #     )
        # )

        self.street_orientation_dict = street_orientation_dict

    # Plot methods

    def plot_attribute_table(self, x="name", y=None, kind="scatter", color="red"):
        """Plot the attribute table."""
        if self.attribute_table is None:
            raise ValueError(
                "The attribute table is empty, Please run the method 'evaluate_basic_stats' first."
            )

        return self.attribute_table.plot(kind=kind, x=x, y=y, color=color)

    def plot_graphs(
        self,
        grid: bool = True,
        savefig: bool = False,
        dpi: float = 300,
        figsize: Tuple[float] = (8, 8),
    ):
        """Plots the graphs for each neighborhood or polygon. It can be used to
        generate either a grid of plots or a single plot for each graph."""
        if not grid:
            for key, value in self.graphs.items():
                if value is not None:
                    fig = plt.figure(figsize=figsize, clear=True)
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
                    if savefig:
                        try:
                            fig.savefig(f"graph_{key}.pdf", dpi=dpi)
                            # print(f"Graph '{key}' saved!")
                        except Exception as e:
                            print(f"Graph '{key}' could not be saved!" + str(e))
                    else:
                        plt.show()
                    plt.close()

            # plt.close("all")
            return None

        # Find the number of rows and columns
        number_of_rows = int(np.ceil(np.sqrt(self.number_of_graphs)))
        number_of_columns = int(np.ceil(self.number_of_graphs / number_of_rows))
        # del_axes = number_of_rows * number_of_columns - self.number_of_graphs

        # Create the figure
        fig, ax = plt.subplots(
            number_of_rows,
            number_of_columns,
            figsize=figsize,
            sharex=False,
            sharey=False,
        )
        # title = self.place if self.place else self.shapefile
        # fig.suptitle(f"Graphs from {title}", fontsize=16)

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
        # fig.delaxes(ax[-1][del_axes])
        if savefig:
            fig.savefig("graphs_grid.pdf", dpi=dpi)
        else:
            plt.show()
        plt.close()

    def plot_street_orientation_linear(
        self,
        grid: bool = False,
        savefig: bool = False,
        dpi: int = 300,
        figsize: tuple[float, float] = (12, 4),
    ):
        """Plots the street orientation for each neighborhood or polygon. It can
        be used to generate either a grid of plots or a single plot for each graph.
        """
        if grid:
            raise NotImplementedError("The grid option is not implemented yet.")

        for key, value in self.street_orientation_dict.items():
            fig = plt.figure(figsize=figsize, clear=True)
            ax = value["bearings_0_360"].hist(bins=36, figsize=figsize)
            ax.set_xticks(np.arange(0, 361, 20))
            ax.set_xlim(0, 360)
            ax.set_title(f"{key} street network edge bearings")

            if savefig:
                fig.savefig(f"linear_hist_street_orientation_{key}.pdf", dpi=dpi)
            else:
                plt.show()

            plt.close()

    def plot_street_orientation_polar(
        self,
        grid: bool = False,
        savefig: bool = False,
        dpi: int = 300,
        figsize: tuple[float, float] = (5, 5),
    ):
        """Plots the street orientation for each neighborhood or polygon. It
        can be used to generate either a grid of plots or a single plot for
        each graph.
        """

        if grid:
            raise NotImplementedError("The grid option is not implemented yet.")

        # First, let's sort the dictionary by the quadratic_sum_deviation
        sorted_dict = {
            k: v
            for k, v in sorted(
                self.street_orientation_dict.items(),
                key=lambda item: item[1]["quadratic_sum_deviation"],
            )
        }

        counter = 0
        for key, value in sorted_dict.items():
            counter += 1
            fig = plt.figure(figsize=figsize, clear=True)
            ax = fig.add_subplot(111, projection="polar")
            ax.set_title(f"{key} street network edge bearings")
            ax.set_axisbelow(True)
            ax.set_theta_zero_location("N")
            ax.set_theta_direction(-1)
            ax.set_xticks(np.arange(0, 2 * np.pi, np.pi / 8))
            ax.hist(
                value["bearings_0_360"] * np.pi / 180,
                bins=36,
                # color="blue",
                alpha=0.95,
                zorder=1,
            )

            # Add anotation to the plot with the mean and median
            ax.annotate(
                f"\u03B4: {value['quadratic_sum_deviation']:.1f}",
                xy=(0.90, 0.005),
                xycoords="axes fraction",
                fontsize=14,
                horizontalalignment="center",
                verticalalignment="center",
                color="White",
                # Add a background to the text
                bbox=dict(
                    facecolor="black",
                    alpha=0.7,
                    boxstyle="round,pad=0.5",
                    edgecolor="none",
                ),
            )

            # Save the figure if savefig is True, show otherwise
            if savefig:
                key = key.replace("/", "-")
                fig.savefig(
                    f"{counter} - polar_hist_street_orientation_{key}.pdf", dpi=dpi
                )
            else:
                plt.show()
            plt.close()

    # Export methods

    def save_graphs_to_shapefile(self, path: str):
        """Saves the graphs to a shapefile."""
        for key, value in self.graphs.items():
            ox.save_graph_shapefile(value, filepath=path + f"_{key}")

    def export_street_orientation_to_csv(self, filename: str):
        """Exports the street orientation to a csv file."""

        export_dict = {}
        for key, value in self.street_orientation_dict.items():
            export_dict[key] = {
                "mean": value["mean"].round(3),
                "std": value["std"].round(3),
                "number_of_edges": (value["uniform_value"] * 18).round(3),
                "quadratic_sum_deviation": value["quadratic_sum_deviation"].round(3),
                "dominant_direction": str(value["dominant_direction"]),
                "dominant_percentage": value["dominant_percentage"].round(3),
                "second_dominant_direction": str(value["second_dominant_direction"]),
                "second_dominant_percentage": value["second_dominant_percentage"].round(
                    3
                ),
                "mean_deviation": value["mean_deviation"].round(3),
                "skew": value["skew"].round(3),
                "kurtosis": value["kurt"].round(3),
            }

        df = pd.DataFrame.from_dict(export_dict, orient="index")
        df.to_csv(filename)

    def export_basic_stats_to_csv(self, filename: str):

        export_dict = {}

        for key, value in self.stats_dict.items():
            export_dict[key] = {
                "count_of_nodes_in_graph": value["n"],
                "count_of_edges_in_graph": value["m"],
                "k_avg": round(value["k_avg"], 3),
                "edge_length_total": round(value["edge_length_total"], 3),
                "edge_length_avg": round(value["edge_length_avg"], 3),
                "streets_per_node_avg": round(value["streets_per_node_avg"], 3),
                # "streets_per_node_counts": value["streets_per_node_counts"],
                # "streets_per_node_proportions": value["streets_per_node_proportions"],
                "intersection_count": value["intersection_count"],
                "street_length_total": round(value["street_length_total"], 3),
                "street_segment_count": value["street_segment_count"],
                "street_length_avg": round(value["street_length_avg"], 3),
                "circuity_avg": round(value["circuity_avg"], 3),
                "self_loop_proportion": round(value["self_loop_proportion"], 3),
            }

        df = pd.DataFrame.from_dict(export_dict, orient="index")
        df.to_csv(filename)

    # Pickle object to save time in the future

    def save(self, filename: str = "geometry") -> None:
        """Save the geometry object to a file so it can be used later."""

        pickled_obj = cloudpickle.dumps(object)

        with open(filename, "wb") as f:
            f.write(pickled_obj)
        print("Your geometry object was saved, check it out: " + filename)

    @classmethod
    def load(self, filename: str = "geometry") -> "Geometry":
        """Load a previously saved geometry pickled file.
        Example: city = geometry.load("filename").
        """
        # Load the pickled object
        with open(filename, "rb") as f:
            pickled_obj = f.read()

        # Unpickle and return the object
        return cloudpickle.loads(pickled_obj)
