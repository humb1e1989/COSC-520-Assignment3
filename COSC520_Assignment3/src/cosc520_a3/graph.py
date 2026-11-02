"""Immutable undirected graph representation and ASCII DIMACS parser."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path


class UndirectedGraph:
    """Store a simple undirected graph using immutable adjacency sets."""

    def __init__(self, adjacency: Iterable[Iterable[int]]) -> None:
        """Create a graph from zero-based adjacency lists.

        Input: one iterable of neighboring vertex IDs per vertex.
        Output: a validated immutable graph object.
        """
        frozen = tuple(frozenset(neighbors) for neighbors in adjacency)
        n = len(frozen)
        for vertex, neighbors in enumerate(frozen):
            if vertex in neighbors:
                raise ValueError(f"self-loop at vertex {vertex}")
            for neighbor in neighbors:
                if not 0 <= neighbor < n:
                    raise ValueError(f"neighbor {neighbor} is outside 0..{n - 1}")
                if vertex not in frozen[neighbor]:
                    raise ValueError(f"edge ({vertex}, {neighbor}) is not symmetric")
        self._adjacency = frozen
        self._edge_count = sum(len(neighbors) for neighbors in frozen) // 2

    @classmethod
    def from_edges(cls, vertex_count: int, edges: Iterable[tuple[int, int]]) -> "UndirectedGraph":
        """Build a simple graph from zero-based edges and return it.

        Input: a nonnegative vertex count and an iterable of endpoint pairs.
        Output: an undirected graph with duplicate edges removed.
        """
        if vertex_count < 0:
            raise ValueError("vertex_count must be nonnegative")
        adjacency = [set() for _ in range(vertex_count)]
        for first, second in edges:
            if not 0 <= first < vertex_count or not 0 <= second < vertex_count:
                raise ValueError(f"edge ({first}, {second}) uses an unknown vertex")
            if first == second:
                raise ValueError(f"self-loop at vertex {first}")
            adjacency[first].add(second)
            adjacency[second].add(first)
        return cls(adjacency)

    @property
    def vertex_count(self) -> int:
        """Return the number of vertices in the graph."""
        return len(self._adjacency)

    @property
    def edge_count(self) -> int:
        """Return the number of undirected edges in the graph."""
        return self._edge_count

    @property
    def vertices(self) -> range:
        """Return the zero-based vertex range."""
        return range(self.vertex_count)

    def neighbors(self, vertex: int) -> frozenset[int]:
        """Return the immutable neighbor set of a zero-based vertex."""
        return self._adjacency[vertex]

    def degree(self, vertex: int) -> int:
        """Return the degree of a vertex."""
        return len(self._adjacency[vertex])

    def edges(self) -> Iterator[tuple[int, int]]:
        """Yield every undirected edge exactly once in sorted order."""
        for first, neighbors in enumerate(self._adjacency):
            for second in sorted(neighbors):
                if first < second:
                    yield first, second


def read_dimacs(path: str | Path) -> UndirectedGraph:
    """Read an ASCII DIMACS edge graph and return an undirected graph.

    Input: path to a DIMACS `.clq`, `.col`, `.mis`, or text graph file.
    Output: an immutable graph using zero-based internal vertex IDs.
    """
    source = Path(path)
    vertex_count: int | None = None
    declared_edges: int | None = None
    edges: list[tuple[int, int]] = []

    with source.open(encoding="utf-8") as stream:
        for line_number, raw_line in enumerate(stream, start=1):
            line = raw_line.strip()
            if not line or line.startswith("c"):
                continue
            fields = line.split()
            if fields[0] == "p":
                if len(fields) < 4:
                    raise ValueError(f"{source}:{line_number}: invalid problem line")
                vertex_count = int(fields[-2])
                declared_edges = int(fields[-1])
            elif fields[0] in {"e", "a"}:
                if len(fields) < 3:
                    raise ValueError(f"{source}:{line_number}: invalid edge line")
                edges.append((int(fields[1]) - 1, int(fields[2]) - 1))
            else:
                raise ValueError(f"{source}:{line_number}: unsupported DIMACS record {fields[0]!r}")

    if vertex_count is None:
        raise ValueError(f"{source}: missing DIMACS problem line")
    graph = UndirectedGraph.from_edges(vertex_count, edges)
    if declared_edges is not None and graph.edge_count != declared_edges:
        raise ValueError(
            f"{source}: declared {declared_edges} edges but parsed {graph.edge_count} unique edges"
        )
    return graph

