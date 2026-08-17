# Accuracy-Cost-Energy Pareto V2 - H100 long-window energy lane

This pack closes the fixed-iteration NVML sample-count defect by measuring H100 joules in a separate long-window lane. It is joined to the fixed-iteration timing pack by workload key and must not be used as the CPU/H100 speedup timing source.

Workload formula: `4 dimensions x 8 regimes x 4 H100 methods x 5 path budgets x 3 repeats = 1920 workload windows`.
Minimum NVML samples: `40`; minimum wall window: `2.0` seconds.

Public claim boundary: H100 joules are measured for review-only workload rows, but CPU joules, cloud-dollar frontier, external/multi-engine reference and production ARIN22 performance remain locked.

Power/saturation readback: H100 long-window energy lane is the primary saturation basis. At D=1000, median device-compute power is 119.58 W out of 350.00 W (34.2% of TDP); device saturation and crossover extrapolation remain locked. Cross-lane power derivation is forbidden: use `gpu_power_draw_w_mean` from the energy lane, not joules divided by timing-lane wall time.
