# DRCET-4 Protocol v1

## Title

Numerical Control Convergence, Stability and Release Gating Test.

## Scope

DRCET-4 validates numerical-method behaviour, not market forecasting, economic
calibration, regulatory approval, or production readiness.

## Primary question

If the public model and reference surfaces are specified, does the computation
preserve declared convergence behaviour, error bounds and invariants; and does
the governor release_gate to recompression, challenge or fail-closed before a silent
bound breach can become a released result?

## Reference hierarchy

- R0: analytic exact solution, including closed-form reference for linear systems.
- R1: arbitrary-precision independent numerical reference.
- R2: consensus reference from independent high-accuracy solvers.
- R3: reference disagreement, producing INCONCLUSIVE rather than PASS/FAIL.

## Hard fail rules

1. Released result above declared error cap.
2. Broken invariant without block.
3. Hash mismatch.
4. Missing result declared PASS.
5. Post-hoc reference replacement.
6. Hidden test used for tuning.
7. Superseded engine represented as frozen engine.

## Boundary of this pack

This first pack executes the public closed-form public pack and release_gate proxy harness.
It also carries a protected-withheld_runtime probe contract for the closed-form public pack:
PASS requires a real Docker/no-egress execution and byte-hash readback. The full
linear fixture set is 48 fixtures; the withheld_runtime probe must print covered_fixture_count,
total_fixture_count, family_fixture_coverage and solver_coverage. The production
withheld_runtime, nonlinear/jump/graph/bifurcation lanes and external blind replay
remain explicit blockers until attached.

## DRCET-4B control-bounded control convergence lane

DRCET4B adds a direct control-bounded control convergence lane for bounded linear
control surface fixtures. For each fixture the artifact records:

- control contract: `L`, `D(L)=R^d`, `PUBLIC_SAFE_CLOSED_FORM_REFERENCE`;
- bounded control function: `PUBLIC_SAFE_BOUND_FUNCTION`;
- identity check: `G(0)=I`;
- contact check: `(G(h)f-f)/h -> Lf`;
- stability check: `sup_m<=n ||G(T/n)^m|| <= M closed_form_stability_factor`;
- declared order and predicted bound;
- observed convergence rate;
- certificate check: `E_n <= B_n`;
- protected docker/no-egress replay.

The lane status starts as `CONTRACT_DECLARED_WATCH`. It may become
`VALIDATED_PASS_REVIEW_ONLY_BOUNDED_CONTROL_CONVERGENCE_LANE` only after the
row certificates, contract/stability checks and protected no-egress withheld_runtime
all pass. A declared contract without withheld_runtime output is not a PASS.

## Protected-withheld_runtime tolerance policy

Withheld_runtime-vs-Python tolerance is predeclared before output readback:
`max(1e-10, 4096 * eps64 * dimension^2 * (step_count + 1) *
(1 + log10(max(stress_ratio, 1))))`. A row exceeding that tolerance fails the
withheld_runtime probe.

## A6 boundary-metric release rule

For A6 boundary-stress lanes, terminal-state error alone is insufficient. Release
requires `e_boundary_parameter = |Re(boundary_parameter_hat_max) - Re(boundary_parameter_star_max)|` to clear the
predeclared bound `max(5e-9, 1e-4 * abs(exact_metric_readback))`. A terminal
PASS with metric-bound failure is forbidden.

This rule is a post-audit corrective gate for v1 after a terminal-only release
blind spot was found on A6. It is pre-registered for v1.1 and later packs; v1
therefore labels the origin explicitly instead of pretending the rule was part
of the first frozen protocol.

Important limitation: `e_boundary_parameter` is a release_gate against the reference, not a
method-ranking metric inside the method A/method B metric equivalence class. In this
code orientation, `METHOD_B_1^n * PUBLIC_SAFE_EQUIVALENCE_MAP = PUBLIC_SAFE_EQUIVALENCE_MAP * METHOD_A_1^n`; the `BAB/BA`
pair has the analogous identity with B. Similar matrices have the same spectrum.
Therefore A6 `e_boundary_parameter` curves and slopes are attributed to the equivalence class,
not to method B as a solver-order proof. Solver order is evidenced only by
terminal solution error.

## Negative-admissibility-marker admissibility boundary

method C is a useful reversible comparator but carries a negative real admissibility-marker
`w0 = -1.7024143839193153`. For irreversible, dissipative or positivity-preserving
public_systems this is an admissibility obstruction, not a measured accuracy loss.

## Track 1 stress caveat

Track 1 computes control surface subflows with closed-form references. Stress inside A
or B is therefore not a numerical subflow stress claim. Stress becomes a true
solver stress only when Track 2 attaches numerical subflow integration.
