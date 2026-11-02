"""Smoke tests for benchmark execution and aggregation."""

from pathlib import Path

from cosc520_a3.benchmark import ALGORITHMS, benchmark_files, summarize


def test_benchmark_sample_graph():
    root = Path(__file__).resolve().parents[1]
    rows = benchmark_files([root / "data" / "sample_graph.col"], repetitions=2, base_seed=520)
    assert len(rows) == len(ALGORITHMS) * 2
    assert all(row["valid"] for row in rows)
    summary = summarize(rows)
    assert len(summary) == len(ALGORITHMS)
    assert all(row["trials"] == 2 for row in summary)

