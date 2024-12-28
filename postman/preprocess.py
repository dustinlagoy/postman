import sys
from itertools import combinations

import geopandas
import momepy
import networkx as nx
import numpy as np
import shapely
import shapely.plotting
import srtm

from postman import utils


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
        "elevation_gain",
        "elevation_loss",
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


def add_elevation_stats(trails):
    for i, row in trails.iterrows():
        geometry = row["geometry"]
        if geometry is None:
            trails.at[i, "distance"] = None
        else:
            up = 0
            down = 0
            last_z = None
            for x, y, z in geometry.coords:
                if last_z is None:
                    last_z = z
                else:
                    delta = z - last_z
                    if delta > 0:
                        up += delta
                    else:
                        down += delta * -1
                    last_z = z
            # print(
            #     "{:3d} {:10.3f} {:8.3f} {:8.3f} {}".format(
            #         i, geometry.length, up, down, utils._name(row)
            #     )
            # )
            trails.at[i, "distance"] = geometry.length
            trails.at[i, "elevation_gain"] = up
            trails.at[i, "elevation_loss"] = down
