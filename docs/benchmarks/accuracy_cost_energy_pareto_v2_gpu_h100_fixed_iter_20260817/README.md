# Accuracy-Cost-Energy Pareto V2 - H100 fixed-iteration lane

This pack replaces fixed-window amortization for CPU/GPU timing reconciliation. Warmup is excluded and exactly the same measured iteration count is used as the CPU fixed-iteration lane.

Fixed iterations: `16`; warmup iterations excluded: `2`.

Public claim boundary: no public Pareto frontier, crossover, cloud-dollar or production ARIN22 claim from this pack alone.
## Energy telemetry quality gate

GPU wall time remains measured under the fixed-iteration protocol, but joules are withheld unless `nvml_sample_count >= 20`. Current accepted energy rows: `720`; withheld energy rows: `6960`; sample count median: `2.0`. A separate long-window energy lane is required before publishing energy or perf-per-watt claims.
