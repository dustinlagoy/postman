import sys
from itertools import combinations

import geopandas
import momepy
import networkx as nx
import numpy as np
import shapely.plotting


def fix_trails(trails: geopandas.GeoDataFrame):
    # remove any empty geometries
    new = trails.drop(trails[trails.geometry == None].index)
    # fix bad connections, the order seems to matter here
    new = momepy.extend_lines(new, 1.0)
    new.geometry = momepy.close_gaps(new, 0.1)
    new = momepy.remove_false_nodes(new)
    new = fix_nans(trails, new)
    new.geometry = momepy.close_gaps(new, 0.1)
    return new


def fix_nans(old, new):
    keys = [
        "name",
        "number",
        "distance",
        "max_elevat",
        "min_elevat",
        "deniv_pos",
        "deniv_neg",
        "kme",
    ]
    for i, row in new.iterrows():
        if np.isnan(row["distance"]):
            distance = row["geometry"].length
            # print(i, distance)
            for j, other in old.iterrows():
                if abs(other["distance"] - distance) < 0.1:
                    # print("    ", j, other["distance"])
                    for key in keys:
                        new.at[i, key] = other[key]
    return new


def to_graph(trails):
    return momepy.gdf_to_nx(
        trails, approach="primal", integer_labels=True, preserve_index=True
    )
