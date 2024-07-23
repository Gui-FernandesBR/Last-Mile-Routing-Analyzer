# %%
# import libraries
import osmnx as ox
import networkx as nx
import pandas as pd
from lmr_analyzer import Haversine
import json

# start timer for the loop
import time

# %%
# define the filename
filename = "route_id_0.csv"  # "docs/notebooks/osmnx/route_id_0_test.csv"

# %%
# import the csv file and store it in a pd.dataframe
df = pd.read_csv(filename)

# check the header
df.head()

# %%
area_dict = dict()

# %%
# iterate over the df and calculate the area of each bounding box
area_dict = dict()
for i in range(df.shape[0]):
    area = (
        Haversine(
            lat1=df["bbox_north"][i],
            lon1=df["bbox_west"][i],
            lat2=df["bbox_south"][i],
            lon2=df["bbox_west"][i],
        )
        * Haversine(
            lat1=df["bbox_north"][i],
            lon1=df["bbox_west"][i],
            lat2=df["bbox_north"][i],
            lon2=df["bbox_east"][i],
        )
    ) * (1000**2)
    area_dict[df["route_id"][i]] = area

# %%
graph_dict = dict()

# %%
# create graphs for each bounding box
count = 1
start = time.time()
end_it = start

for key, value in df.iterrows():
    start_it = time.time()
    graph_dict[value["route_id"]] = ox.graph.graph_from_bbox(
        north=value["bbox_north"],
        south=value["bbox_south"],
        east=value["bbox_east"],
        west=value["bbox_west"],
        network_type="drive",
        simplify=True,
        retain_all=False,
        truncate_by_edge=False,
        clean_periphery=True,
        custom_filter=None,
    )
    print(
        f"\rGraph done {count:4} out of {len(df)}, {(100*count/len(df)):.2f} % - Estimated time remaining: {(end_it-start)*((len(df)-count)/(60*count)):.2f} min",
        end="",
        flush=True,
    )
    count += 1
    end_it = time.time()

# %%
# iterate through the graph_dict and convert the graphs to undirected graphs
for key, value in graph_dict.items():
    graph_dict[key] = nx.to_undirected(value)

# %%
# calculate basic stats for each graph
stats_dict = dict()
count = 1
for key, value in graph_dict.items():
    stats_dict[key] = ox.basic_stats(value, area=area_dict[key])
    print(
        f"\rStats done {count:4} out of {len(df)}, {(100*count/len(df)):.2f} %",
        end="",
        flush=True,
    )
    count += 1

# %%
# calculate orientation and entropy for each graph
entropy_dict = dict()

# %%
count = 1

start = time.time()
start_it = start

for key, value in graph_dict.items():
    graph_dict[key] = ox.bearing.add_edge_bearings(value)
    entropy_dict[key] = ox.bearing.orientation_entropy(value)
    end_it = time.time()
    print(
        f"\rBearing done {count:4} out of {len(df)}, {(100*count/len(df)):.2f} % - Estimated time remaining: {(end_it-start)*((len(df)-count)/(60*count)):.2f} min",
        end="",
        flush=True,
    )
    count += 1
    start_it = time.time()

# %%
# combine stats and entropy into one dict
stats_entropy_dict = dict()

# %%
count = 1
for key, value in stats_dict.items():
    stats_entropy_dict[key] = {
        "street_length_total": value["street_length_total"],
        "street_density_km": value["street_density_km"],
        "intersection_count": value["intersection_count"],
        "intersection_density_km": value["intersection_density_km"],
        "k_avg": value["k_avg"],
        "street_density_km": value["street_density_km"],
        "entropy": entropy_dict[key],
    }
    print(
        f"\rDone {count:4} out of {len(df)}, {(100*count/len(df)):.2f} %",
        end="",
        flush=True,
    )
    count += 1

# %%
# save the final dictionary as a json file
with open(f"stats_entropy_dict{filename[-5]}.json", "w") as fp:
    json.dump(stats_entropy_dict, fp)
