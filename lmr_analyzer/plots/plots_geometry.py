from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import osmnx as ox


def plot_graphs(
    graphs: dict,  # TODO: specify format of this dict
    grid: bool = True,
    savefig: bool = False,
    dpi: float = 300,
    figsize: Tuple[float] = (8, 8),
):
    """Plots the graphs for each neighborhood or polygon. It can be used to
    generate either a grid of plots or a single plot for each graph."""
    if not grid:
        for key, value in graphs.items():
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
                    fig.savefig(f"graph_{key}.pdf", dpi=dpi)
                else:
                    plt.show()
                plt.close()

        return None

    # Find the number of rows and columns
    number_of_graphs = len([graph for graph in graphs.values() if graph])
    number_of_rows = int(np.ceil(np.sqrt(number_of_graphs)))
    number_of_columns = int(np.ceil(number_of_graphs / number_of_rows))
    # del_axes = number_of_rows * number_of_columns - number_of_graphs

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
    for key, value in graphs.items():
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
            ax[ax_index // number_of_columns, ax_index % number_of_columns].set_title(
                " ".join(key.split(" ", 2)[:2])
            )
            ax_index += 1

    plt.tight_layout()
    # fig.delaxes(ax[-1][del_axes])

    if savefig:
        fig.savefig("graphs_grid.pdf", dpi=dpi)
    else:
        plt.show()

    plt.close()


def plot_street_orientation_polar(
    street_orientation_dict: dict,  # TODO: specify format of this dict
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

    sorted_dict = dict(
        sorted(
            street_orientation_dict.items(),
            key=lambda item: item[1]["quadratic_sum_deviation"],
        )
    )

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

        # Add annotation to the plot with the mean and median
        ax.annotate(
            f"\u03B4: {value['quadratic_sum_deviation']:.1f}",
            xy=(0.90, 0.005),
            xycoords="axes fraction",
            fontsize=14,
            horizontalalignment="center",
            verticalalignment="center",
            color="White",
            # Add a background to the text
            bbox={
                "facecolor": "black",
                "alpha": 0.7,
                "boxstyle": "round,pad=0.5",
                "edgecolor": "none",
            },
        )

        if savefig:
            key = key.replace("/", "-")
            fig.savefig(f"{counter} - polar_hist_street_orientation_{key}.pdf", dpi=dpi)
        else:
            plt.show()

        plt.close()
