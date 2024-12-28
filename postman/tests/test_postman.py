import networkx as nx
import pytest
import shapely

from postman import core, utils


@pytest.fixture()
def graph():
    # this graph with nodes 0-3 and egdes a-e looks like:
    # 1--d--3
    # |\    |
    # | \   |
    # a  c  e
    # |   \ |
    # |    \|
    # 0--b--2
    # where nodes 1 and 2 are odd (have an odd number of edges)
    graph = nx.MultiGraph()
    graph.add_nodes_from(
        [
            (0, {"x": 0, "y": 0}),
            (1, {"x": 0, "y": 1}),
            (2, {"x": 1, "y": 0}),
            (3, {"x": 1, "y": 1}),
        ]
    )
    graph.add_edges_from(
        [
            (
                0,
                1,
                {
                    "name": "a",
                    "distance": 1,
                    "elevation_gain": 0,
                    "elevation_loss": 0,
                    "index_position": 0,
                    "geometry": shapely.LineString([[0, 0], [0, 1]]),
                },
            ),
            (
                0,
                2,
                {
                    "name": "b",
                    "distance": 1,
                    "elevation_gain": 0,
                    "elevation_loss": 0,
                    "index_position": 1,
                    "geometry": shapely.LineString([[0, 0], [1, 0]]),
                },
            ),
            (
                1,
                2,
                {
                    "name": "c",
                    "distance": 1,
                    "elevation_gain": 0,
                    "elevation_loss": 0,
                    "index_position": 2,
                    "geometry": shapely.LineString([[0, 1], [1, 0]]),
                },
            ),
            (
                1,
                3,
                {
                    "name": "d",
                    "distance": 1,
                    "elevation_gain": 0,
                    "elevation_loss": 0,
                    "index_position": 3,
                    "geometry": shapely.LineString([[0, 1], [1, 1]]),
                },
            ),
            (
                2,
                3,
                {
                    "name": "e",
                    "distance": 1,
                    "elevation_gain": 0,
                    "elevation_loss": 0,
                    "index_position": 4,
                    "geometry": shapely.LineString([[1, 0], [1, 1]]),
                },
            ),
        ]
    )
    return graph


def test_solve_with_even_weights(graph):
    tour = core.trail_tour(graph, 0)
    utils.print_tour(tour)
    assert len(tour) == 6
    assert len([x for x in tour if x[2]["name"] == "c"]) == 2


def test_solve_with_uneven_distances(graph):
    graph[0][1][0]["distance"] = 0.1
    graph[0][2][0]["distance"] = 0.1
    tour = core.trail_tour(graph, 0)
    utils.print_tour(tour)
    assert len(tour) == 7
    assert len([x for x in tour if x[2]["name"] == "a"]) == 2
    assert len([x for x in tour if x[2]["name"] == "b"]) == 2


def test_solve_with_uneven_distances_and_elevations(graph):
    graph[0][1][0]["distance"] = 0.1
    graph[0][1][0]["elevation_gain"] = 1.0
    graph[0][1][0]["elevation_loss"] = 0.0
    graph[0][2][0]["distance"] = 0.1
    graph[0][2][0]["elevation_gain"] = 1.0
    graph[0][2][0]["elevation_loss"] = 0.0
    graph[1][3][0]["distance"] = 0.2
    graph[2][3][0]["distance"] = 0.2
    tour = core.trail_tour(graph, 0)
    utils.print_tour(tour)
    # without elevation, a and b should be duplicated, but the slightly longer
    # path via d and e should be choosen here instead
    assert len(tour) == 7
    assert len([x for x in tour if x[2]["name"] == "d"]) == 2
    assert len([x for x in tour if x[2]["name"] == "e"]) == 2
