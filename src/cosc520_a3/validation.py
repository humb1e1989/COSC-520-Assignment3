"""Independent validators for vertex-cover and coloring results."""

from collections.abc import Collection, Sequence

from .graph import UndirectedGraph


def is_vertex_cover(graph: UndirectedGraph, cover: Collection[int]) -> bool:
    """Return whether every graph edge has at least one endpoint in cover."""
    chosen = set(cover)
    return all(first in chosen or second in chosen for first, second in graph.edges())


def is_valid_coloring(graph: UndirectedGraph, colors: Sequence[int]) -> bool:
    """Return whether colors assigns a nonnegative legal color to each vertex."""
    if len(colors) != graph.vertex_count or any(color < 0 for color in colors):
        return False
    return all(colors[first] != colors[second] for first, second in graph.edges())

