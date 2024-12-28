import networkx as nx
import pytest

from postman import core


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
    graph.add_nodes_from(range(4))
    graph.add_edges_from(
        [
            (0, 1, {"id": "a", "testweight": 1}),
            (0, 2, {"id": "b", "testweight": 1}),
            (1, 2, {"id": "c", "testweight": 1}),
            (1, 3, {"id": "d", "testweight": 1}),
            (2, 3, {"id": "e", "testweight": 1}),
        ]
    )
    return graph


def test_unweighted(graph):
    result = nx.eulerize(graph)
    # for u, v, key in result.edges(data=True):
    #     print(u, v, key)
    # the simplest way to eulerize this graph is to duplicate edge c
    assert len(result.edges) == 6
    assert len(result[1][2]) == 2


def test_weighted_algorithm_with_even_weights(graph):
    result = core.weighted_eulerize(graph, "testweight")
    # this should give the same result as the unweighted algorithm
    assert len(result.edges) == 6
    assert len(result[1][2]) == 2


def test_weighted_algorithm_with_uneven_weights(graph):
    graph[0][1][0]["testweight"] = 0.1
    graph[0][2][0]["testweight"] = 0.1
    result = core.weighted_eulerize(graph, "testweight")
    assert len(result.edges) == 7
    assert len(result[0][1]) == 2
    assert len(result[0][2]) == 2
