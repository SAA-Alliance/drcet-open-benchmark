# DRCET Open Benchmark

Public-safe benchmark evidence package for the DRCET series.

This repository intentionally publishes synthetic/review-only artifacts only. It does not publish production source, runtime build contexts, credentials, client data, private data-room URLs, hidden adversarial corpora, internal mathematical construction names, protected factors, or commercial production datasets.

## Current Public-Safe Status

| Lane | Status | Boundary |
| --- | --- | --- |
| DRCET-1 tail metrics | PUBLISHED_METHOD_ATTACHED | Method citation/status only in this export. |
| DRCET-2 path functionals | INTERNAL_10M_EVIDENCE_UNPUBLISHED_METHOD | Not exported; internal evidence remains outside the open repo. |
| DRCET-3 attribution/stress | INTERNAL_10M_EVIDENCE_UNPUBLISHED_METHOD | Not exported; internal evidence remains outside the open repo. |
| DRCET-10 Accuracy-Cost-Energy Pareto V2 | CPU_H100_FIXED_ITERATION_5_BUDGET_GPU_LONG_WINDOW_ENERGY_REVIEW_ONLY_DEVICE_UNSATURATED | Fixed-iteration CPU/H100 telemetry attached; speedup/crossover claim locked. |
| DRCET-4A/4B numerical-control evidence | VALIDATED_REVIEW_ONLY_PUBLIC_SAFE_SUMMARY | Public summary only; internal construction names and implementation details withheld. |
| DRCET-4C boundary_control evidence | VALIDATED_REVIEW_ONLY_PUBLIC_SAFE_SUMMARY | Public summary only; internal construction names and implementation details withheld. |
| DRCET-4D public_control refinement | VALIDATED_REVIEW_ONLY_PUBLIC_SAFE_SUMMARY | Public summary only; internal construction names and implementation details withheld. |

## Key Readbacks

- DRCET-10 Pareto V2 status SHA: `sha256:69081cb4badd4b0cedb2e42969f90cb7d865a67b649b7e0be4ece13885ff2316`
- DRCET-10 common rows / iso rows: `19200 / 8781`
- DRCET-10 amortization matched: `true`
- DRCET-10 GPU energy source: `H100_LONG_WINDOW_ENERGY_PACK`
- DRCET-10 GPU energy gate: `PASS_NVML_LONG_WINDOW_SAMPLE_COUNT_RELEASE_QUALITY`
- DRCET-10 H100 power-limit readback: `PASS_NVML_POWER_LIMIT_READBACK`
- DRCET-10 cloud-cost profile: `PARTIAL_H100_RATE_BOUND_CPU_RATE_WITHHELD_DOLLAR_FRONTIER_LOCKED`
- DRCET-10 speedup/crossover claim allowed: `false / false`
- DRCET-4 public status: `VALIDATED_REVIEW_ONLY_PUBLIC_SAFE_SUMMARY`
- DRCET-4C public status: `VALIDATED_REVIEW_ONLY_PUBLIC_SAFE_SUMMARY`
- DRCET-4D public status: `VALIDATED_REVIEW_ONLY_PUBLIC_SAFE_SUMMARY`
- Runtime replay status: `WITHHELD_FROM_OPEN_REPO`
- External blind replay status: `PENDING_EXTERNAL_BLIND_REPLAY`

## Public Wording

Public-safe synthetic lanes validate release discipline and evidence gating. Internal implementation details, construction names, protected factors, and implementation-specific mathematical surfaces are intentionally withheld from this open repository.

See `PUBLIC_DISCLOSURE_BOUNDARY.md` before reusing any claim.
