"""Correctness tests for the two vertex-cover algorithms."""

import pytest

from cosc520_a3.graph import UndirectedGraph
from cosc520_a3.validation import is_vertex_cover
from cosc520_a3.vertex_cover import basic_vertex_cover, randomized_vertex_cover


@pytest.mark.parametrize(
    "graph",
    [
        UndirectedGraph.from_edges(0, []),
        UndirectedGraph.from_edges(3, [(0, 1), (1, 2)]),
        UndirectedGraph.from_edges(4, [(0, 1), (1, 2), (2, 3), (3, 0)]),
        UndirectedGraph.from_edges(6, [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]),
    ],
)
def test_basic_vertex_cover_is_valid(graph):
    result = basic_vertex_cover(graph)
    assert is_vertex_cover(graph, result.cover)


@pytest.mark.parametrize("seed", [1, 2, 520, 999])
def test_randomized_vertex_cover_is_valid(seed):
    graph = UndirectedGraph.from_edges(
        7,
        [(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5), (5, 6)],
    )
    result = randomized_vertex_cover(graph, seed=seed)
    assert is_vertex_cover(graph, result.cover)


def test_randomized_vertex_cover_is_seed_reproducible():
    graph = UndirectedGraph.from_edges(5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])
    assert randomized_vertex_cover(graph, 42) == randomized_vertex_cover(graph, 42)


def test_basic_cover_is_at_most_twice_maximal_matching_lower_bound():
    graph = UndirectedGraph.from_edges(6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)])
    result = basic_vertex_cover(graph)
    assert result.size == 2 * result.edge_selections

