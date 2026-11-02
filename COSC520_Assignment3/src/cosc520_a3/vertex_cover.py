"""Basic and randomized approximation-style vertex-cover algorithms."""

from __future__ import annotations

from dataclasses import dataclass
import random

from .graph import UndirectedGraph


@dataclass(frozen=True)
class VertexCoverResult:
    """Store a computed cover and the number of selected uncovered edges."""

    cover: frozenset[int]
    edge_selections: int

    @property
    def size(self) -> int:
        """Return the number of vertices in the cover."""
        return len(self.cover)


def _edge_state(graph: UndirectedGraph) -> tuple[list[tuple[int, int]], list[set[int]], set[int]]:
    """Return indexed edges, incident-edge sets, and active edge IDs."""
    edges = list(graph.edges())
    incident = [set() for _ in graph.vertices]
    for edge_id, (first, second) in enumerate(edges):
        incident[first].add(edge_id)
        incident[second].add(edge_id)
    return edges, incident, set(range(len(edges)))


def _remove_incident(active: set[int], incident: list[set[int]], vertex: int) -> None:
    """Remove every active edge incident to vertex; return nothing."""
    active.difference_update(incident[vertex])


def basic_vertex_cover(graph: UndirectedGraph) -> VertexCoverResult:
    """Return the basic two-endpoint vertex cover.

    Input: an immutable undirected graph.
    Output: a valid cover formed by adding both endpoints of each selected
    uncovered edge. The selected edges form a maximal matching.
    """
    edges, incident, active = _edge_state(graph)
    cover: set[int] = set()
    selections = 0
    cursor = 0

    while active:
        while cursor not in active:
            cursor += 1
        first, second = edges[cursor]
        cover.update((first, second))
        selections += 1
        _remove_incident(active, incident, first)
        _remove_incident(active, incident, second)

    return VertexCoverResult(frozenset(cover), selections)


def randomized_vertex_cover(graph: UndirectedGraph, seed: int = 520) -> VertexCoverResult:
    """Return a randomized one-endpoint vertex cover.

    Input: an immutable graph and a reproducibility seed.
    Output: a valid cover produced by selecting one random endpoint from each
    chosen uncovered edge.
    """
    edges, incident, active = _edge_state(graph)
    rng = random.Random(seed)
    cover: set[int] = set()
    selections = 0
    cursor = 0

    while active:
        while cursor not in active:
            cursor += 1
        first, second = edges[cursor]
        selected = first if rng.getrandbits(1) == 0 else second
        cover.add(selected)
        selections += 1
        _remove_incident(active, incident, selected)

    return VertexCoverResult(frozenset(cover), selections)

