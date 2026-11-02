"""Greedy graph coloring with input and smallest-last vertex orderings."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import heapq
import random

from .graph import UndirectedGraph


@dataclass(frozen=True)
class ColoringResult:
    """Store per-vertex colors, color count, and the order used."""

    colors: tuple[int, ...]
    color_count: int
    order: tuple[int, ...]


def greedy_coloring(graph: UndirectedGraph, order: Sequence[int]) -> ColoringResult:
    """Color vertices in order using the lowest available color.

    Input: an undirected graph and a permutation of all vertex IDs.
    Output: a legal greedy coloring and the supplied order.
    """
    if len(order) != graph.vertex_count or set(order) != set(graph.vertices):
        raise ValueError("order must contain every vertex exactly once")

    colors = [-1] * graph.vertex_count
    highest_color = -1
    for vertex in order:
        forbidden = {colors[neighbor] for neighbor in graph.neighbors(vertex) if colors[neighbor] >= 0}
        color = 0
        while color in forbidden:
            color += 1
        colors[vertex] = color
        highest_color = max(highest_color, color)
    return ColoringResult(tuple(colors), highest_color + 1, tuple(order))


def basic_greedy_coloring(graph: UndirectedGraph, seed: int | None = None) -> ColoringResult:
    """Return basic greedy coloring under an arbitrary vertex order.

    Input: an undirected graph and an optional reproducibility seed.
    Output: a greedy coloring. When seed is provided, the arbitrary order is a
    seeded random permutation; otherwise, the input order is used.
    """
    order = list(graph.vertices)
    if seed is not None:
        random.Random(seed).shuffle(order)
    return greedy_coloring(graph, order)


def smallest_last_order(graph: UndirectedGraph) -> tuple[int, ...]:
    """Return a smallest-last vertex order using a lazy degree heap.

    Input: an immutable undirected graph.
    Output: vertices in coloring order, which is the reverse of repeatedly
    removing a current minimum-degree vertex.

    The heap implementation uses O((V + E) log V) time and O(V + E) space.
    """
    n = graph.vertex_count
    degrees = [graph.degree(vertex) for vertex in graph.vertices]
    removed = [False] * n
    heap = [(degrees[vertex], vertex) for vertex in graph.vertices]
    heapq.heapify(heap)
    removal_order: list[int] = []

    while heap:
        degree, vertex = heapq.heappop(heap)
        if removed[vertex] or degree != degrees[vertex]:
            continue
        removed[vertex] = True
        removal_order.append(vertex)
        for neighbor in graph.neighbors(vertex):
            if not removed[neighbor]:
                degrees[neighbor] -= 1
                heapq.heappush(heap, (degrees[neighbor], neighbor))

    removal_order.reverse()
    return tuple(removal_order)


def smallest_last_coloring(graph: UndirectedGraph) -> ColoringResult:
    """Return greedy coloring under a computed smallest-last order."""
    return greedy_coloring(graph, smallest_last_order(graph))

