# Accuracy-Cost-Energy Pareto V2 - CPU/H100 reconciliation

This pack is fail-closed on timing units. The earlier mixed-unit formula `median(CPU.wall_ms) / median(GPU.wall_ms_per_iter)` is invalidated.

The current accepted protocol is fixed-iteration, warmup-excluded timing on both CPU and H100. The row-level join key is published in `cpu_gpu_unit_matched_common_rows.csv`; `iso_accuracy_common_rows` is the count of joined rows where both sides meet the declared error envelope.

Public claim boundary: no Pareto frontier, no cloud-dollar claim, no withheld_runtime performance claim, and no NVIDIA-grade crossover claim while reference remains internal, CPU RAPL/cloud cost are missing, or the H100 is unsaturated.
