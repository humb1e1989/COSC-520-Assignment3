"""Correctness tests for greedy and smallest-last coloring."""

import pytest

from cosc520_a3.coloring import basic_greedy_coloring, greedy_coloring, smallest_last_coloring, smallest_last_order
from cosc520_a3.graph import UndirectedGraph
from cosc520_a3.validation import is_valid_coloring


@pytest.mark.parametrize(
    "graph",
    [
        UndirectedGraph.from_edges(0, []),
        UndirectedGraph.from_edges(1, []),
        UndirectedGraph.from_edges(3, [(0, 1), (1, 2), (2, 0)]),
        UndirectedGraph.from_edges(4, [(0, 1), (1, 2), (2, 3), (3, 0)]),
        UndirectedGraph.from_edges(5, [(0, 1), (0, 2), (0, 3), (0, 4)]),
    ],
)
def test_basic_greedy_coloring_is_valid(graph):
    result = basic_greedy_coloring(graph)
    assert is_valid_coloring(graph, result.colors)


def test_smallest_last_order_is_permutation():
    graph = UndirectedGraph.from_edges(6, [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4)])
    order = smallest_last_order(graph)
    assert len(order) == graph.vertex_count
    assert set(order) == set(graph.vertices)


def test_smallest_last_coloring_is_valid():
    graph = UndirectedGraph.from_edges(7, [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (4, 5), (5, 6), (6, 3)])
    result = smallest_last_coloring(graph)
    assert is_valid_coloring(graph, result.colors)


def test_seeded_basic_coloring_is_reproducible():
    graph = UndirectedGraph.from_edges(6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (1, 4)])
    assert basic_greedy_coloring(graph, seed=42) == basic_greedy_coloring(graph, seed=42)


def test_complete_graph_requires_one_color_per_vertex():
    n = 6
    graph = UndirectedGraph.from_edges(n, [(i, j) for i in range(n) for j in range(i + 1, n)])
    assert basic_greedy_coloring(graph).color_count == n
    assert smallest_last_coloring(graph).color_count == n


def test_greedy_rejects_invalid_order():
    graph = UndirectedGraph.from_edges(3, [(0, 1)])
    with pytest.raises(ValueError, match="every vertex"):
        greedy_coloring(graph, [0, 1, 1])

