# Accuracy-Cost-Energy Pareto V2 - H100 long-window energy lane

This pack closes the fixed-iteration NVML sample-count defect by measuring H100 joules in a separate long-window lane. It is joined to the fixed-iteration timing pack by workload key and must not be used as the CPU/H100 speedup timing source.

Workload formula: `4 dimensions x 8 regimes x 4 H100 methods x 5 path budgets x 3 repeats = 1920 workload windows`.
Minimum NVML samples: `40`; minimum wall window: `2.0` seconds.

Public claim boundary: H100 joules are measured for review-only workload rows, but CPU joules, cloud-dollar frontier, external/multi-engine reference and production ARIN22 performance remain locked.
