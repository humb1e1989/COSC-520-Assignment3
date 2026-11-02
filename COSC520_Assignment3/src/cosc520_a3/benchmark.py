"""Benchmark vertex-cover and graph-coloring algorithms on DIMACS graphs."""

from __future__ import annotations

import argparse
import csv
import gc
import json
from pathlib import Path
import platform
from statistics import median
from time import perf_counter_ns

from .coloring import basic_greedy_coloring, smallest_last_coloring
from .graph import UndirectedGraph, read_dimacs
from .validation import is_valid_coloring, is_vertex_cover
from .vertex_cover import basic_vertex_cover, randomized_vertex_cover


ALGORITHMS = (
    "vc_basic",
    "vc_randomized",
    "coloring_basic",
    "coloring_smallest_last",
)

RAW_FIELDS = (
    "dataset",
    "vertices",
    "edges",
    "algorithm",
    "trial",
    "seed",
    "runtime_ns",
    "solution_value",
    "valid",
)

SUMMARY_FIELDS = (
    "dataset",
    "vertices",
    "edges",
    "algorithm",
    "trials",
    "median_runtime_ns",
    "median_solution_value",
    "min_solution_value",
    "max_solution_value",
    "all_valid",
)


def run_algorithm(graph: UndirectedGraph, name: str, seed: int) -> tuple[int, bool]:
    """Run one named algorithm and return its objective value and validity."""
    if name == "vc_basic":
        result = basic_vertex_cover(graph)
        return result.size, is_vertex_cover(graph, result.cover)
    if name == "vc_randomized":
        result = randomized_vertex_cover(graph, seed=seed)
        return result.size, is_vertex_cover(graph, result.cover)
    if name == "coloring_basic":
        result = basic_greedy_coloring(graph, seed=seed)
        return result.color_count, is_valid_coloring(graph, result.colors)
    if name == "coloring_smallest_last":
        result = smallest_last_coloring(graph)
        return result.color_count, is_valid_coloring(graph, result.colors)
    raise ValueError(f"unknown algorithm: {name}")


def timed_trial(graph: UndirectedGraph, name: str, seed: int) -> dict[str, int | bool | str]:
    """Time one algorithm call and return a validated raw measurement row."""
    gc.collect()
    gc.disable()
    try:
        start = perf_counter_ns()
        solution_value, valid = run_algorithm(graph, name, seed)
        runtime_ns = perf_counter_ns() - start
    finally:
        gc.enable()
    if not valid:
        raise AssertionError(f"{name} returned an invalid solution")
    return {
        "algorithm": name,
        "seed": seed,
        "runtime_ns": runtime_ns,
        "solution_value": solution_value,
        "valid": valid,
    }


def summarize(rows: list[dict[str, int | bool | str]]) -> list[dict[str, int | float | bool | str]]:
    """Aggregate raw rows by dataset and algorithm using medians and ranges."""
    summary: list[dict[str, int | float | bool | str]] = []
    datasets = sorted({str(row["dataset"]) for row in rows})
    for dataset in datasets:
        for name in ALGORITHMS:
            group = [row for row in rows if row["dataset"] == dataset and row["algorithm"] == name]
            if not group:
                continue
            first = group[0]
            runtimes = [int(row["runtime_ns"]) for row in group]
            values = [int(row["solution_value"]) for row in group]
            summary.append(
                {
                    "dataset": dataset,
                    "vertices": int(first["vertices"]),
                    "edges": int(first["edges"]),
                    "algorithm": name,
                    "trials": len(group),
                    "median_runtime_ns": median(runtimes),
                    "median_solution_value": median(values),
                    "min_solution_value": min(values),
                    "max_solution_value": max(values),
                    "all_valid": all(bool(row["valid"]) for row in group),
                }
            )
    return summary


def benchmark_files(
    files: list[Path], repetitions: int, base_seed: int, algorithms: tuple[str, ...] = ALGORITHMS
) -> list[dict[str, int | bool | str]]:
    """Benchmark every algorithm on every file and return all raw rows."""
    rows: list[dict[str, int | bool | str]] = []
    for dataset_index, path in enumerate(files):
        graph = read_dimacs(path)
        print(f"Loaded {path.name}: |V|={graph.vertex_count:,}, |E|={graph.edge_count:,}", flush=True)
        for trial in range(1, repetitions + 1):
            trial_seed = base_seed + dataset_index * 100_000 + trial
            offset = (trial - 1) % len(algorithms)
            order = algorithms[offset:] + algorithms[:offset]
            for name in order:
                row = timed_trial(graph, name, trial_seed)
                row.update(
                    {
                        "dataset": path.name,
                        "vertices": graph.vertex_count,
                        "edges": graph.edge_count,
                        "trial": trial,
                    }
                )
                rows.append(row)
                print(
                    f"  trial={trial} {name}: {int(row['runtime_ns']) / 1e6:.3f} ms, "
                    f"value={row['solution_value']}",
                    flush=True,
                )
    return rows


def main() -> None:
    """Parse CLI arguments, run benchmarks, and save raw and summary CSV files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--files", type=Path, nargs="+", required=True)
    parser.add_argument("--repetitions", type=int, default=10)
    parser.add_argument("--seed", type=int, default=520)
    parser.add_argument(
        "--problem",
        choices=("all", "vertex-cover", "coloring"),
        default="all",
        help="run both problem families or only the algorithms relevant to one family",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--prefix", default="benchmark")
    args = parser.parse_args()
    if args.repetitions < 1:
        parser.error("--repetitions must be at least 1")
    missing = [str(path) for path in args.files if not path.is_file()]
    if missing:
        parser.error(f"missing input files: {', '.join(missing)}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = args.output_dir / f"{args.prefix}_raw.csv"
    summary_path = args.output_dir / f"{args.prefix}_summary.csv"
    metadata_path = args.output_dir / f"{args.prefix}_metadata.json"
    if any(path.exists() for path in (raw_path, summary_path, metadata_path)):
        parser.error("output already exists; choose a new --prefix")

    selected_algorithms = {
        "all": ALGORITHMS,
        "vertex-cover": ("vc_basic", "vc_randomized"),
        "coloring": ("coloring_basic", "coloring_smallest_last"),
    }[args.problem]
    rows = benchmark_files(args.files, args.repetitions, args.seed, selected_algorithms)
    with raw_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=RAW_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with summary_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(summarize(rows))

    metadata = {
        "files": [str(path) for path in args.files],
        "algorithms": list(selected_algorithms),
        "problem": args.problem,
        "repetitions": args.repetitions,
        "base_seed": args.seed,
        "algorithm_order": "rotated across trials",
        "timing": "file parsing, validation, and output writing excluded",
        "python": platform.python_version(),
        "platform": platform.platform(),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {raw_path}, {summary_path}, and {metadata_path}")


if __name__ == "__main__":
    main()

