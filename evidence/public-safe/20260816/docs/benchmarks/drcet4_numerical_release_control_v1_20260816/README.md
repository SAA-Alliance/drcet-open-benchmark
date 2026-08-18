# DRCET-4 Numerical Release Control Convergence v1

Status: `PROTOCOL_FULL_LINEAR_EXACT_CONTAINER_AND_FOUNDATION_LANE_VALIDATED_PRODUCTION_ARIN22_PENDING`

This pack starts DRCET-4 as a governed numerical-method benchmark. It attaches a
protocol freeze draft, 48 linear exact fixtures, solver-resolution rows and a
public ARIN22 routing proxy. It does **not** benchmark the protected ARIN22
production container and does **not** create production validation, regulatory
approval or market-forecast evidence.

## Current executable scope

- Linear exact non-commuting systems: `48` fixtures.
- Step counts: `4, 8, 16, 32, 64, 128, 256, 512`.
- Solver-resolution rows: `3072`.
- Order-summary rows: `384`.
- Route proxy rows: `384`.
- Silent bound breaches released: `0`.
- Protected container linear exact probe: `PASS_REVIEW_ONLY_NO_EGRESS_CONTAINER_LINEAR_EXACT_CORE`.
- Protected container fixture coverage: `48` / `48`.
- Protected container delta/tolerance: row-wise ratio; max-delta and max-ratio rows are disclosed separately in `protected_container_linear_exact_probe.json`.
- A6 spectral gate: `4` spectral fail-closed route rows.
- foundation lane: `VALIDATED_PASS_REVIEW_ONLY_FOUNDATION_CONVERGENCE_LANE`.
- foundation rows: `48`.
- foundation container: `PASS_REVIEW_ONLY_NO_EGRESS_CONTAINER_FOUNDATION_LANE`.

## New audit guards

- Bound utilization summary: `bound_utilization_summary.csv`.
- A1 commuting-control sanity: `a1_commuting_sanity.csv`.
- A6 near-critical spectral-abscissa error: `a6_near_critical_spectral_summary.csv`.
- A6 route spectral gate: `a6_route_spectral_gate_summary.csv`.
- A6 e_lambda vs step count: `a6_spectral_step_summary.csv`.
- A6 e_lambda gate-diagnostic slopes, not method order: `a6_spectral_slope_summary.csv`.
- A6 e_lambda conjugacy slope consistency: `a6_spectral_conjugacy_slope_consistency.csv`.
- A6 e_lambda bootstrap CI: `a6_spectral_slope_bootstrap_summary.csv`.
- Route/governor overhead internal smoke: `route_overhead_summary.csv`.
- A2/A5 pressure lanes: `pressure_lane_summary.csv`.
- Lie/Strang spectral conjugacy diagnostics: `operator_spectral_conjugacy_diagnostics.csv`.
- Lie/Strang spectral conjugacy denominator: `48 fixtures * 8 step counts * 2 Lie/Strang conjugacy pairs = 768`.
- Spectral conjugacy class summary: `spectral_conjugacy_class_summary.csv`.
- Method admissibility summary: `method_admissibility_summary.csv`.
- A6 paired-row check: `a6_solver_pairing_summary.csv`.
- Protected/no-egress container probe: `protected_container_linear_exact_probe.json`.
- foundation fixture contract: `foundation_product_fixture_contract.csv`.
- foundation row certificates: `foundation_product_convergence_results.csv`.
- foundation tangent/stability summary: `foundation_product_tangent_stability_summary.csv`.
- foundation no-egress container probe: `foundation_product_protected_container_probe.json`.
- Container tolerance policy: `max(floor, 4096 * eps64 * dimension^2 * (step_count + 1) * (1 + log10(max(stiffness_ratio, 1))))`
- Track-1 stiffness caveat: `Track 1 computes exp(hA) and exp(hB) exactly; stiffness inside subflows is not a numerical subflow stress claim until Track 2 attaches.`
- Article-readiness finding: `valid release gate against the reference; forbidden as intermethod ranking inside Lie/Strang conjugacy classes`.
- Method-order basis: `terminal_solution_error_not_e_lambda`.
- Route overhead public claim: `WITHHELD until N>=3 fresh-process timing; exact ratio remains internal smoke`.

## Claim boundary

`review_only_numerical_method_validation_scaffold_not_external_certification_not_production_arin22_benchmark`

## Next blockers

- `production_arin22_container_not_attached`
- `nonlinear_manufactured_lane_not_executed`
- `jump_regime_discontinuity_lane_not_executed`
- `graph_bifurcation_lanes_not_executed`
- `external_blind_replay_request_published_not_completed`
- `N3_fresh_process_timing_and_energy_not_attached`
