# DRCET Open Benchmark

Public-safe benchmark evidence package for the DRCET series.

This repository intentionally publishes synthetic/review-only artifacts only.
It does not publish production ARIN22 kernel source, protected container build
contexts, credentials, client data, private data-room URLs, hidden adversarial
corpora or commercial production datasets.

## Current Public-Safe Status

| Lane | Status | Boundary |
| --- | --- | --- |
| DRCET-1 tail metrics | PUBLISHED_METHOD_ATTACHED | Method citation/status only in this export. |
| DRCET-2 path functionals | INTERNAL_10M_EVIDENCE_UNPUBLISHED_METHOD | Not exported; internal evidence remains outside the open repo. |
| DRCET-3 attribution/stress | INTERNAL_10M_EVIDENCE_UNPUBLISHED_METHOD | Not exported; internal evidence remains outside the open repo. |
| DRCET-10 Accuracy-Cost-Energy Pareto V2 | CPU_H100_FIXED_ITERATION_5_BUDGET_GPU_LONG_WINDOW_ENERGY_REVIEW_ONLY_DEVICE_UNSATURATED | Fixed-iteration CPU/H100 telemetry attached; speedup/crossover claim locked. |
| DRCET-4 operator splitting + 4B Chernoff convergence | PROTOCOL_FULL_LINEAR_EXACT_CONTAINER_AND_REMIZOV_CHERNOFF_LANE_VALIDATED_PRODUCTION_ARIN22_PENDING | Foundation/routing validated; production ARIN22 pending. |
| DRCET-4C Chernoff-Remizov resolvent | VALIDATED_PASS_WITH_ORDER_FLOOR_GATE_AND_QUADRATURE_WATCH_CHERNOFF_REMIZOV_RESOLVENT_LANE_PRODUCTION_ARIN22_PENDING | Bounded contract-surrogate; production ARIN22 pending. |
| DRCET-4D continuum spatial refinement | VALIDATED_PASS_PUBLIC_SAFE_CONTINUUM_SPATIAL_REFINEMENT_LANE_PRODUCTION_ARIN22_PENDING | Public-safe unbounded/continuum surrogate; production ARIN22 pending. |

## Key Readbacks

- DRCET-4 status SHA: `sha256:298a49ff8071e54c90f52ca49d45b153f446644ee4a71fc92675a3e4f82e421d`
- DRCET-10 Pareto V2 status SHA: `sha256:92ffc4bd5732d148a0ed85896a29967abc428dc5be63881c6d5dbca3ef13b6e6`
- DRCET-10 common rows / iso rows: `19200` / `8781`
- DRCET-10 amortization matched: `True`
- DRCET-10 GPU energy source: `H100_LONG_WINDOW_ENERGY_PACK`
- DRCET-10 GPU energy gate: `PASS_NVML_LONG_WINDOW_SAMPLE_COUNT_RELEASE_QUALITY`
- DRCET-10 cloud-cost profile: `PARTIAL_H100_RATE_BOUND_CPU_RATE_WITHHELD_DOLLAR_FRONTIER_LOCKED`
- DRCET-10 speedup/crossover claim allowed: `False` / `False`
- DRCET-4B status: `VALIDATED_PASS_REVIEW_ONLY_REMIZOV_CHERNOFF_CONVERGENCE_LANE`
- DRCET-4C status SHA: `sha256:61d7266d4625cef0aa21bc270b1a58c382c4b820c346e30fa44d72b0b447182f`
- DRCET-4C released rows: `155`
- DRCET-4C non-convergent fail-closed rows: `25`
- DRCET-4C silent non-convergent releases: `0`
- DRCET-4C order-floor gate: `PASS_NONCONVERGENT_ROWS_FAIL_CLOSED`
- DRCET-4D status SHA: `sha256:82f6b92871ad59bc2ec5bec803869068ac2fb49ee578f728c423505dcfd01af6`
- DRCET-4D observed spatial order median: `2.0007826398221917`
- DRCET-4D max E/B: `0.39999116019618314`
- Production ARIN22 container status: `PRODUCTION_ARIN22_CONTAINER_NOT_ATTACHED`
- External blind replay status: `PENDING_EXTERNAL_BLIND_REPLAY`

## Public Wording

Foundation and governed routing are validated on public-safe synthetic lanes.
The production ARIN22 kernel remains pending until a protected production
container is attached and replayed under the same lane contracts.

See `PUBLIC_DISCLOSURE_BOUNDARY.md` before reusing any claim.
