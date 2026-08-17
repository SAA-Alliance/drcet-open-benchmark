# Accuracy-Cost-Energy Pareto V2 - CPU Contabo measured lane

This pack is a CPU-only measured evidence lane. It does not unlock a public NVIDIA-grade Pareto or CPU/GPU crossover claim.

Target formula: `4 dimensions x 5 confidence levels x 8 regimes x 2 metrics = 320 target rows`.

Measured here: CPU wall time, CPU process time, peak RSS.
Withheld here: CPU joules if RAPL is unavailable, cloud dollars without a dated SKU rate, all GPU telemetry until the GPU node is attached.

Reference tier: R1 internal CPU reference with shard CI. This is useful for engineering calibration, not an external oracle.

Acceptance equation: `abs(method_estimate - reference_estimate) <= predeclared_tolerance + reference_ci_half_width`.

Public claim boundary: no CPU/GPU Pareto frontier, no crossover, no NVIDIA claim from this CPU-only pack.
