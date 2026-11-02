"""Tests for graph construction and DIMACS parsing."""

from pathlib import Path

import pytest

from cosc520_a3.graph import UndirectedGraph, read_dimacs


def test_graph_from_edges_removes_duplicates():
    graph = UndirectedGraph.from_edges(4, [(0, 1), (1, 0), (1, 2), (2, 3)])
    assert graph.vertex_count == 4
    assert graph.edge_count == 3
    assert list(graph.edges()) == [(0, 1), (1, 2), (2, 3)]


def test_graph_rejects_self_loop():
    with pytest.raises(ValueError, match="self-loop"):
        UndirectedGraph.from_edges(2, [(0, 0)])


def test_read_dimacs(tmp_path: Path):
    source = tmp_path / "tiny.col"
    source.write_text("c test\np edge 3 2\ne 1 2\ne 2 3\n", encoding="utf-8")
    graph = read_dimacs(source)
    assert graph.vertex_count == 3
    assert graph.edge_count == 2
    assert graph.neighbors(1) == frozenset({0, 2})


def test_read_dimacs_rejects_edge_count_mismatch(tmp_path: Path):
    source = tmp_path / "bad.col"
    source.write_text("p edge 3 3\ne 1 2\ne 2 3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="declared 3 edges"):
        read_dimacs(source)

