# DRCET-4C Chernoff-Remizov Resolvent v1

Status: `VALIDATED_PASS_WITH_ORDER_FLOOR_GATE_AND_QUADRATURE_WATCH_CHERNOFF_REMIZOV_RESOLVENT_LANE_PRODUCTION_ARIN22_PENDING`

This pack closes the DRCET-4B object mismatch by adding a resolvent lane. It is
public-safe and review-only: it exercises a bounded synthetic five-factor
palindromic Chernoff surrogate, not the protected production ARIN22 kernel and
not protected production operator factors.

## Executed scope

- Fixtures: `4`.
- Lambda sweep points per fixture: `15`.
- Step counts: `4, 8, 16, 32, 64`.
- Lambda sweep rows: `300`.
- Status counts: `{'PASS_RECOMPRESSED_NEAR_BOUNDARY': 115, 'PASS_RESOLVENT_CONVERGENCE': 40, 'SAFE_FAIL_CLOSED_NON_CONVERGENT': 25, 'SAFE_FAIL_CLOSED_OUTSIDE_CERTIFIED_RESOLVENT_HALF_PLANE': 120}`.
- Count interpretation: `grid coverage, not empirical frequency`.
- Released rows: `155`.
- Fail-closed outside certified resolvent half-plane: `120`.
- Fail-closed non-convergent rows: `25`.
- Order-floor release gate: `inside-half-plane rows require observed_resolvent_order >= 1.5; otherwise status=SAFE_FAIL_CLOSED_NON_CONVERGENT`.
- Order-floor transitions: `25` released rows moved to fail-closed.
- Silent non-convergent releases: `0`.
- Silent releases outside certified resolvent half-plane: `0`.
- Max released E/B: `1.9310420813980992e-05`.
- Certificate interpretation: `CONSERVATIVE_SAFETY_ENVELOPE_NOT_TIGHT_ERROR_ESTIMATE`.
- Relative-error readback: lambda rows include `reference_resolvent_norm` and `E_over_reference_resolvent_norm`.
- Tangency/product rows: `4`.
- Resolvent convergence rows: `36`.
- Resolvent order bootstrap CI: `1.9757862057800821` to `1.9923747660316546`.
- No-egress container: `PASS_REVIEW_ONLY_NO_EGRESS_CONTAINER_REMIZOV_RESOLVENT_LANE`.
- Container cases: `180`.

## What is validated

- Contract execution uses a symmetric product surrogate, not `I+tL`.
- `G(0)=I`, generator tangency and second-order product behaviour are checked.
- `R_lambda,n^G g = integral_0^infty exp(-lambda t) [G(t/n)]^n g dt` is compared with `(lambda I-H)^(-1)g`.
- `Re(lambda) > omega_contract` is treated as the certified release half-plane.
- `Re(lambda) <= omega_contract` is fail-closed before release.
- Error budget is explicit: `B_total = B_product + B_quadrature + B_tail + B_reference + B_floating`.
- The a-priori certificate is a conservative theorem-domain safety envelope, not a tight error estimate.
- Gauss-Laguerre is used on the infinite interval; `B_tail=0` is marked as not applicable for finite tail truncation in this bounded v1 lane.
- Finite-dimensional exact matrix resolvent may be diagnostic-available below the certified half-plane; release remains withheld because theorem-domain authority is not established.

## Boundary

`review_only_bounded_contract_surrogate_resolvent_validation_not_production_arin22_kernel_not_external_certification`

## Next blockers

- `production_arin22_container_not_attached`
- `protected_production_operator_factors_not_published_by_design`
- `unbounded_continuum_spatial_refinement_lane_not_executed`
- `external_blind_replay_request_published_not_completed`
