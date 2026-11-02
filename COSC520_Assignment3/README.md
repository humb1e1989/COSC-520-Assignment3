# COSC 520 Assignment 3

This project implements and benchmarks four graph algorithms without using
library implementations of vertex cover or graph coloring:

- Basic 2-approximation vertex cover
- Randomized endpoint vertex cover
- Basic greedy graph coloring in a seeded arbitrary order
- Greedy graph coloring with smallest-last ordering

The code accepts undirected graphs in ASCII DIMACS format, including the
`.clq`, `.col`, and `.mis` files distributed with BHOSLIB/FRB.

## Setup

Python 3.10 or newer is required.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Run the tests

```sh
python -m pytest
```

## Run the included demonstration

```sh
python -m cosc520_a3.demo
```

## Benchmark the sample graph

```sh
python -m cosc520_a3.benchmark \
  --files data/sample_graph.col \
  --problem all \
  --repetitions 5 \
  --prefix sample

python -m cosc520_a3.plot_results \
  --input results/sample_summary.csv \
  --prefix sample
```

The benchmark writes raw measurements, a median summary, and reproducibility
metadata to `results/`. The plotting command writes runtime and solution-quality
figures to `plots/`.

Runtime depends on the machine and operating environment. Generate the values
used in the submitted report on your own computer, and report that hardware and
software configuration; do not substitute timing data produced on another
machine.

## Benchmark BHOSLIB/FRB data

The project bundle includes one ASCII DIMACS instance at each of five graph
sizes, obtained from the official BHOSLIB page:

https://rb-bench.github.io/benchmarks/hidden-opt-graph.html

The selected size progression is:

- `frb30-15-mis` or `frb30-15-clq` (450 vertices)
- `frb35-17-mis` or `frb35-17-clq` (595 vertices)
- `frb40-19-mis` or `frb40-19-clq` (760 vertices)
- `frb45-21-mis` or `frb45-21-clq` (945 vertices)
- `frb50-23-mis` or `frb50-23-clq` (1,150 vertices)

Use the MIS family for the vertex-cover experiment and the complementary CLQ
family for graph coloring. To reproduce the complete experiment, run:

```sh
python -m cosc520_a3.benchmark \
  --files data/bhoslib/mis/frb30-15-1.mis \
          data/bhoslib/mis/frb35-17-1.mis \
          data/bhoslib/mis/frb40-19-1.mis \
          data/bhoslib/mis/frb45-21-1.mis \
          data/bhoslib/mis/frb50-23-1.mis \
  --problem vertex-cover \
  --repetitions 10 \
  --seed 520 \
  --prefix bhoslib_vc_full

python -m cosc520_a3.benchmark \
  --files data/bhoslib/clq/frb30-15-1.clq \
          data/bhoslib/clq/frb35-17-1.clq \
          data/bhoslib/clq/frb40-19-1.clq \
          data/bhoslib/clq/frb45-21-1.clq \
          data/bhoslib/clq/frb50-23-1.clq \
  --problem coloring \
  --repetitions 10 \
  --seed 520 \
  --prefix bhoslib_coloring_full

python -m cosc520_a3.plot_results \
  --input results/bhoslib_vc_full_summary.csv \
  --prefix bhoslib_vc_full

python -m cosc520_a3.plot_results \
  --input results/bhoslib_coloring_full_summary.csv \
  --prefix bhoslib_coloring_full
```

Use one consistent graph family within each report figure so graph density and
size changes are interpretable.

## Output interpretation

For vertex cover, a smaller `solution_value` is better. For graph coloring, a
smaller value means fewer colors. `valid` must be `True` in every raw row.
The randomized vertex-cover method and the arbitrary-order greedy-coloring
baseline use a different recorded seed in each repetition. The other methods
are deterministic and are repeated to measure runtime variability.

## Project structure

```text
src/cosc520_a3/
  graph.py          Graph representation and DIMACS parser
  vertex_cover.py   Two vertex-cover algorithms
  coloring.py       Basic greedy and smallest-last coloring
  validation.py     Independent correctness checks
  benchmark.py      Repeated timing and CSV output
  plot_results.py   Runtime and solution-quality plots
  demo.py           Small end-to-end demonstration
tests/               Unit and smoke tests
data/                Sample graph and benchmark instructions
```

## Reproducibility notes

- Randomized runs use explicit seeds.
- Each algorithm receives the same immutable graph.
- Timed regions exclude file parsing and CSV writing.
- Every returned cover and coloring is validated before a row is recorded.
- Raw trials are retained instead of reporting only aggregated values.

