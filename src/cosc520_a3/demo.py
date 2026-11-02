"""Run all four algorithms on the included demonstration graph."""

from pathlib import Path

from .coloring import basic_greedy_coloring, smallest_last_coloring
from .graph import read_dimacs
from .validation import is_valid_coloring, is_vertex_cover
from .vertex_cover import basic_vertex_cover, randomized_vertex_cover


def main() -> None:
    """Load the sample graph, run every algorithm, and print verified results."""
    root = Path(__file__).resolve().parents[2]
    graph = read_dimacs(root / "data" / "sample_graph.col")

    basic_cover = basic_vertex_cover(graph)
    random_cover = randomized_vertex_cover(graph, seed=520)
    basic_colors = basic_greedy_coloring(graph, seed=520)
    smallest_last = smallest_last_coloring(graph)

    print(f"Graph: |V|={graph.vertex_count}, |E|={graph.edge_count}")
    print(f"Basic vertex cover: size={basic_cover.size}, valid={is_vertex_cover(graph, basic_cover.cover)}")
    print(f"Randomized vertex cover: size={random_cover.size}, valid={is_vertex_cover(graph, random_cover.cover)}")
    print(f"Basic greedy coloring: colors={basic_colors.color_count}, valid={is_valid_coloring(graph, basic_colors.colors)}")
    print(f"Smallest-last coloring: colors={smallest_last.color_count}, valid={is_valid_coloring(graph, smallest_last.colors)}")


if __name__ == "__main__":
    main()

