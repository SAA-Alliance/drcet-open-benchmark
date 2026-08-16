# DRCET-4 Protocol v1

## Title

Operator-Splitting Convergence, Stability and Routing Test.

## Scope

DRCET-4 validates numerical-method behaviour, not market forecasting, economic
calibration, regulatory approval, or production readiness.

## Primary question

If the mathematical model and its operators are specified, does the computation
preserve declared convergence behaviour, error bounds and invariants; and does
the governor route to recompression, challenge or fail-closed before a silent
bound breach can become a released result?

## Reference hierarchy

- R0: analytic exact solution, including matrix exponential for linear systems.
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
7. Superseded kernel represented as frozen kernel.

## Boundary of this pack

This first pack executes the public linear exact core and route-proxy harness.
It also carries a protected-container probe contract for the linear exact core:
PASS requires a real Docker/no-egress execution and byte-hash readback. The full
linear fixture set is 48 fixtures; the container probe must print covered_fixture_count,
total_fixture_count, family_fixture_coverage and solver_coverage. The production
ARIN22 container, nonlinear/jump/graph/bifurcation lanes and external blind replay
remain explicit blockers until attached.

## DRCET-4B Remizov-Chernoff convergence lane

DRCET4B adds a direct Remizov-Chernoff convergence lane for bounded linear
operator fixtures. For each fixture the artifact records:

- operator contract: `L`, `D(L)=R^d`, `S(t)=exp(tL)`;
- Chernoff function: `G(t)=I+tL`;
- identity check: `G(0)=I`;
- tangency check: `(G(h)f-f)/h -> Lf`;
- stability check: `sup_m<=n ||G(T/n)^m|| <= M exp(omega T)`;
- declared order and predicted bound;
- observed convergence rate;
- certificate check: `E_n <= B_n`;
- protected docker/no-egress replay.

The lane status starts as `CONTRACT_DECLARED_WATCH`. It may become
`VALIDATED_PASS_REVIEW_ONLY_REMIZOV_CHERNOFF_CONVERGENCE_LANE` only after the
row certificates, tangent/stability checks and protected no-egress container
all pass. A declared contract without container output is not a PASS.

## Protected-container tolerance policy

Container-vs-Python tolerance is predeclared before output readback:
`max(1e-10, 4096 * eps64 * dimension^2 * (step_count + 1) *
(1 + log10(max(stiffness_ratio, 1))))`. A row exceeding that tolerance fails the
container probe.

## A6 spectral-abscissa release rule

For A6 near-critical lanes, terminal-state error alone is insufficient. Release
requires `e_lambda = |Re(lambda_hat_max) - Re(lambda_star_max)|` to clear the
predeclared bound `max(5e-9, 1e-4 * abs(exact_spectral_abscissa))`. A terminal
PASS with spectral-bound failure is forbidden.

This rule is a post-audit corrective gate for v1 after a terminal-only release
blind spot was found on A6. It is pre-registered for v1.1 and later packs; v1
therefore labels the origin explicitly instead of pretending the rule was part
of the first frozen protocol.

Important limitation: `e_lambda` is a release gate against the reference, not a
method-ranking metric inside the Lie/Strang spectral conjugacy class. In this
code orientation, `STRANG_ABA^n * exp(hA/2) = exp(hA/2) * LIE_AB^n`; the `BAB/BA`
pair has the analogous identity with B. Similar matrices have the same spectrum.
Therefore A6 `e_lambda` curves and slopes are attributed to the conjugacy class,
not to Strang as a solver-order proof. Solver order is evidenced only by
terminal solution error.

## Negative-substep admissibility boundary

Yoshida4 is a useful reversible comparator but carries a negative real substep
`w0 = -1.7024143839193153`. For irreversible, dissipative or positivity-preserving
semigroups this is an admissibility obstruction, not a measured accuracy loss.

## Track 1 stiffness caveat

Track 1 computes operator subflows with matrix exponentials. Stiffness inside A
or B is therefore not a numerical subflow stress claim. Stiffness becomes a true
solver stress only when Track 2 attaches numerical subflow integration.
