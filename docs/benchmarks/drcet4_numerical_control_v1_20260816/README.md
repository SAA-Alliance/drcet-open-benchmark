# DRCET-4 Numerical Control Convergence v1

Status: `PROTOCOL_FULL_CLOSED_FORM_WITHHELD_RUNTIME_AND_BOUNDED_CONTROL_LANE_VALIDATED_WITHHELD_RUNTIME_PENDING`

This pack starts DRCET-4 as a governed numerical-method benchmark. It attaches a
protocol freeze draft, 48 closed-form fixtures, solver-resolution rows and a
public public release_gate proxy. It does **not** benchmark the sealed withheld_runtime
production withheld_runtime and does **not** create production validation, regulatory
approval or market-forecast evidence.

## Current executable scope

- Closed-form structured systems: `48` fixtures.
- Step counts: `4, 8, 16, 32, 64, 128, 256, 512`.
- Solver-resolution rows: `3072`.
- Order-summary rows: `384`.
- Release Gate proxy rows: `384`.
- Silent bound breaches released: `0`.
- Sealed replay runtime closed-form probe: `PASS_REVIEW_ONLY_NO_EGRESS_WITHHELD_RUNTIME_CLOSED_FORM_CORE`.
- Sealed replay runtime fixture coverage: `48` / `48`.
- Sealed replay runtime delta/tolerance: row-wise ratio; max-delta and max-ratio rows are disclosed separately in `sealed_replay_closed_form_probe.json`.
- A6 metric gate: `4` metric fail-closed release_gate rows.
- control-bounded control lane: `VALIDATED_PASS_REVIEW_ONLY_BOUNDED_CONTROL_CONVERGENCE_LANE`.
- control-bounded control rows: `48`.
- control-bounded control withheld_runtime: `PASS_REVIEW_ONLY_NO_EGRESS_WITHHELD_RUNTIME_BOUNDED_CONTROL_LANE`.

## New audit guards

- Bound utilization summary: `bound_utilization_summary.csv`.
- A1 control sanity: `a1_control_sanity.csv`.
- A6 boundary-stress boundary-metric error: `a6_boundary_metric_summary.csv`.
- A6 release_gate metric gate: `a6_release_gate_metric_gate_summary.csv`.
- A6 e_boundary_parameter vs step count: `a6_metric_step_summary.csv`.
- A6 e_boundary_parameter gate-diagnostic slopes, not method order: `a6_metric_slope_summary.csv`.
- A6 e_boundary_parameter equivalence slope consistency: `a6_metric_equivalence_slope_consistency.csv`.
- A6 e_boundary_parameter bootstrap CI: `a6_metric_slope_bootstrap_summary.csv`.
- Release Gate/governor overhead internal smoke: `release_gate_overhead_summary.csv`.
- A2/A5 pressure lanes: `pressure_lane_summary.csv`.
- method A/method B metric equivalence diagnostics: `metric_equivalence_diagnostics.csv`.
- method A/method B metric equivalence denominator: `48 fixtures * 8 step counts * 2 method A/method B equivalence pairs = 768`.
- Metric equivalence class summary: `metric_equivalence_class_summary.csv`.
- Method admissibility summary: `method_admissibility_summary.csv`.
- A6 paired-row check: `a6_solver_pairing_summary.csv`.
- Protected/no-egress withheld_runtime probe: `sealed_replay_closed_form_probe.json`.
- control-bounded control fixture contract: `bounded_control_fixture_contract.csv`.
- control-bounded control row certificates: `bounded_control_convergence_results.csv`.
- control-bounded control contract/stability summary: `bounded_control_contract_stability_summary.csv`.
- control-bounded control no-egress withheld_runtime probe: `bounded_control_sealed_replay_probe.json`.
- Withheld_runtime tolerance policy: `max(floor, 4096 * eps64 * dimension^2 * (step_count + 1) * (1 + log10(max(stress_ratio, 1))))`
- Track-1 stress caveat: `Track 1 computes closed-form component maps exactly; stress inside subflows is not a numerical subflow stress claim until Track 2 attaches.`
- Article-readiness finding: `valid release_gate against the reference; forbidden as intermethod ranking inside method A/method B equivalence classes`.
- Method-order basis: `terminal_solution_error_not_e_boundary_parameter`.
- Release Gate overhead public claim: `WITHHELD until N>=3 fresh-process timing; exact ratio remains internal smoke`.

## Claim boundary

`review_only_numerical_method_validation_scaffold_not_external_certification_not_withheld_runtime_benchmark`

## Next blockers

- `withheld_runtime_not_attached`
- `nonlinear_manufactured_lane_not_executed`
- `jump_regime_discontinuity_lane_not_executed`
- `graph_bifurcation_lanes_not_executed`
- `external_blind_replay_request_published_not_completed`
- `N3_fresh_process_timing_and_energy_not_attached`
