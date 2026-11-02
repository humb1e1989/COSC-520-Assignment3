"""Create runtime and solution-quality plots from benchmark summary CSV."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


LABELS = {
    "vc_basic": "Basic vertex cover",
    "vc_randomized": "Randomized vertex cover",
    "coloring_basic": "Basic greedy coloring",
    "coloring_smallest_last": "Smallest-last coloring",
}


def _series(rows: list[dict[str, str]], algorithms: tuple[str, ...], field: str):
    """Yield labeled, vertex-sorted point series for selected algorithms."""
    for name in algorithms:
        points = sorted(
            (int(row["vertices"]), float(row[field]))
            for row in rows
            if row["algorithm"] == name
        )
        if points:
            yield name, points


def plot_runtime(rows: list[dict[str, str]], algorithms: tuple[str, ...], title: str, output: Path) -> None:
    """Plot median runtime by graph size and save PNG and PDF copies."""
    figure, axis = plt.subplots(figsize=(7.2, 4.8))
    for name, points in _series(rows, algorithms, "median_runtime_ns"):
        axis.plot(
            [x for x, _ in points],
            [value / 1e6 for _, value in points],
            marker="o",
            linewidth=1.8,
            label=LABELS[name],
        )
    axis.set_title(title)
    axis.set_xlabel("Number of vertices")
    axis.set_ylabel("Median runtime (ms)")
    axis.set_yscale("log")
    axis.grid(True, which="both", alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output.with_suffix(".png"), dpi=180)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def plot_quality(rows: list[dict[str, str]], algorithms: tuple[str, ...], ylabel: str, title: str, output: Path) -> None:
    """Plot median objective values and observed ranges by graph size."""
    figure, axis = plt.subplots(figsize=(7.2, 4.8))
    for name in algorithms:
        group = sorted(
            (row for row in rows if row["algorithm"] == name),
            key=lambda row: int(row["vertices"]),
        )
        if not group:
            continue
        x = [int(row["vertices"]) for row in group]
        y = [float(row["median_solution_value"]) for row in group]
        lower = [value - float(row["min_solution_value"]) for value, row in zip(y, group)]
        upper = [float(row["max_solution_value"]) - value for value, row in zip(y, group)]
        axis.errorbar(x, y, yerr=[lower, upper], marker="o", capsize=3, label=LABELS[name])
    axis.set_title(title)
    axis.set_xlabel("Number of vertices")
    axis.set_ylabel(ylabel)
    axis.grid(True, alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output.with_suffix(".png"), dpi=180)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def main() -> None:
    """Read a summary CSV and create four report-ready figures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("plots"))
    parser.add_argument("--prefix", default="benchmark")
    args = parser.parse_args()
    with args.input.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if not rows:
        parser.error("input summary is empty")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    vc = ("vc_basic", "vc_randomized")
    coloring = ("coloring_basic", "coloring_smallest_last")
    present = {row["algorithm"] for row in rows}
    if present.intersection(vc):
        plot_runtime(rows, vc, "Vertex-cover runtime", args.output_dir / f"{args.prefix}_vc_runtime")
        plot_quality(rows, vc, "Cover size (smaller is better)", "Vertex-cover solution size", args.output_dir / f"{args.prefix}_vc_quality")
    if present.intersection(coloring):
        plot_runtime(rows, coloring, "Graph-coloring runtime", args.output_dir / f"{args.prefix}_coloring_runtime")
        plot_quality(rows, coloring, "Number of colors (smaller is better)", "Graph-coloring solution quality", args.output_dir / f"{args.prefix}_coloring_quality")
    print(f"Saved plots in {args.output_dir}")


if __name__ == "__main__":
    main()

