import sys
from itertools import combinations

import geopandas
import matplotlib
import matplotlib.pyplot as plt
import momepy
import networkx as nx
import numpy as np
import shapely.plotting

from postman import datatypes, utils


def trail_tour(graph: nx.MultiGraph, start: int) -> datatypes.Tour:
    weight_with_elevation(graph, 10)
    euler = weighted_eulerize(graph, "weight")
    path = nx.eulerian_circuit(euler, start, keys=True)
    tour = [(u, v, euler.get_edge_data(u, v)[k]) for u, v, k in path]
    fix_segment_direction(tour, graph)
    return tour


def weight_with_elevation(graph: nx.MultiGraph, scale=1.0):
    for u, v, data in graph.edges(data=True):
        data["weight"] = (
            data["distance"]
            + (data["elevation_gain"] * scale + data["elevation_loss"] * scale) / 2
        )
        # print(utils.label_len(data), data["weight"])


def fix_segment_direction(tour, graph):
    for i, (u, v, data) in enumerate(tour):
        x, y = data["geometry"].coords.xy
        dx = abs(graph.nodes[u]["x"] - x[0])
        dy = abs(graph.nodes[u]["y"] - y[0])
        if dx + dy > 0.1:
            # start of path is not alighned with node, it must be backwards
            tmp = data["elevation_gain"]
            data["elevation_gain"] = data["elevation_loss"]
            data["elevation_loss"] = tmp
            data["geometry"] = data["geometry"].reverse()


def weighted_eulerize(G, weight="weight"):
    if G.order() == 0:
        raise nx.NetworkXPointlessConcept("Cannot Eulerize null graph")
    if not nx.is_connected(G):
        raise nx.NetworkXError("G is not connected")
    odd_degree_nodes = [n for n, d in G.degree() if d % 2 == 1]
    # print("odd degree nodes", len(odd_degree_nodes))
    G = nx.MultiGraph(G)
    if len(odd_degree_nodes) == 0:
        return G

    # get all shortest paths between vertices of odd degree
    odd_deg_pairs_paths = [
        (m, {n: nx.shortest_path(G, source=m, target=n, weight=weight)})
        for m, n in combinations(odd_degree_nodes, 2)
    ]
    # print(odd_deg_pairs_paths)
    # print("odd degree pairs", len(odd_deg_pairs_paths))

    # use the number of vertices in a graph + 1 as an upper bound on
    # the maximum length of a path in G
    # upper_bound_on_max_path_length = len(G) + 1
    upper_bound_on_max_path_length = (
        sum(x[weight] for _, _, x in G.edges(data=True)) + 1
    )
    # TODO keep updating below

    # use "len(G) + 1 - len(P)",
    # where P is a shortest path between vertices n and m,
    # as edge-weights in a new graph
    # store the paths in the graph for easy indexing later
    Gp = nx.Graph()
    for n, Ps in odd_deg_pairs_paths:
        for m, P in Ps.items():
            if n != m:
                # note should just remove longer paths between nodes (as they
                # will never be part of a shortest path) before finding shorter
                # paths above as noted in
                # https://groups.google.com/g/networkx-discuss/c/87uC9F0ug8Y/m/CrNNYEHLZfIJ
                # instead assume that is what the shortest path algorithm did
                length = multigraph_path_length(G, P, weight)
                # print(n, m, P, length)
                Gp.add_edge(
                    m, n, weight=upper_bound_on_max_path_length - length, path=P
                )

    # find the minimum weight matching of edges in the weighted graph
    best_matching = nx.Graph(list(nx.max_weight_matching(Gp)))

    # duplicate each edge along each path in the set of paths in Gp
    for m, n in best_matching.edges():
        path = multigraph_shortest_path(G, Gp[m][n]["path"], weight)
        # print(m, n, end="")
        # for u, v, p in path:
        #     print(" ", u, v, label_len(p), end="")
        # print()
        # G.add_edges_from(nx.utils.pairwise(path))
        G.add_edges_from(path)
    return G


def multigraph_path_length(G, P, weight="weight"):
    length = 0
    for i in range(len(P) - 1):
        minimum = None
        for _, data in G.get_edge_data(P[i], P[i + 1]).items():
            if minimum is None:
                minimum = data[weight]
            else:
                minimum = min(minimum, data[weight])
        assert minimum is not None
        length += minimum
    return length


def multigraph_shortest_path(G, P, weight="weight"):
    out_path = []
    for i in range(len(P) - 1):
        m = P[i]
        n = P[i + 1]
        minimum = None
        for _, data in G.get_edge_data(m, n).items():
            if minimum is None:
                minimum = data
            elif data[weight] < minimum[weight]:
                minimum = data
        assert minimum is not None
        out_path.append((m, n, minimum))
    return out_path
