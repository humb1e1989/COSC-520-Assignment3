# Benchmark data

`sample_graph.col` is a small DIMACS graph for demonstrations and tests. It is
not intended to support the report's performance conclusions.

The `bhoslib/` directory contains one selected instance for each of five FRB
sizes. The files were obtained from the official BHOSLIB page:

https://rb-bench.github.io/benchmarks/hidden-opt-graph.html

The `mis/` files support the vertex-cover comparison, while the complementary
`clq/` files support the graph-coloring comparison. The final report should link
to the official dataset page and identify the exact filenames used. If GitHub
rejects the data or repository size is a concern, omit `data/bhoslib/` from Git
and retain this official download link in the README and report.

