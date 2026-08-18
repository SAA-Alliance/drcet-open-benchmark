# Accuracy-Cost-Energy Pareto V2 - CPU Contabo windowed lane

This pack adds fixed-window CPU measurements so CPU and H100 rows can be reconciled in comparable units. It is not a standalone CPU/GPU speedup claim.

Target formula: `4 dimensions x 5 confidence levels x 8 regimes x 2 metrics = 320 target rows`.

Timing boundary: generation to loss materialization, amortized over a fixed wall-time window. VaR/ES reduction is outside the timer, matching the H100 lane.

Public claim boundary: no public Pareto frontier, crossover, cloud-dollar or NVIDIA claim from this pack alone.
