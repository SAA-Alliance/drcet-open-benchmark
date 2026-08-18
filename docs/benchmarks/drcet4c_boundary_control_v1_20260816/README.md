# DRCET-4C bounded release-control Boundary Control v1

Status: `VALIDATED_PASS_WITH_ORDER_FLOOR_GATE_AND_REFERENCE_GRID_WATCH_BOUNDARY_CONTROL_LANE_WITHHELD_RUNTIME_PENDING`

This pack closes the DRCET-4B object mismatch by adding a boundary_control lane. It is
public-safe and review-only: it exercises a bounded synthetic multi-factor
bounded bounded control surrogate, not the sealed withheld_runtime engine and
not sealed production internal factors.

## Executed scope

- Fixtures: `4`.
- Lambda sweep points per fixture: `15`.
- Step counts: `4, 8, 16, 32, 64`.
- Lambda sweep rows: `300`.
- Status counts: `{'PASS_RECOMPRESSED_NEAR_BOUNDARY': 115, 'PASS_BOUNDARY_CONTROL_CONVERGENCE': 40, 'SAFE_FAIL_CLOSED_NON_CONVERGENT': 25, 'SAFE_FAIL_CLOSED_OUTSIDE_CERTIFIED_BOUNDARY_DOMAIN': 120}`.
- Count interpretation: `grid coverage, not empirical frequency`.
- Released rows: `155`.
- Fail-closed outside certified release domain: `120`.
- Fail-closed non-convergent rows: `25`.
- Order-floor release_gate: `inside-domain rows require observed_boundary_control_order >= 1.5; otherwise status=SAFE_FAIL_CLOSED_NON_CONVERGENT`.
- Order-floor transitions: `25` released rows moved to fail-closed.
- Silent non-convergent releases: `0`.
- Silent releases outside certified release domain: `0`.
- Max released E/B: `1.9310420813980992e-05`.
- Certificate interpretation: `CONSERVATIVE_SAFETY_ENVELOPE_NOT_TIGHT_ERROR_ESTIMATE`.
- Relative-error readback: boundary_parameter rows include `reference_boundary_control_norm` and `E_over_reference_boundary_control_norm`.
- Contact/product rows: `4`.
- Boundary Control convergence rows: `36`.
- Boundary Control order bootstrap CI: `1.9757862057800821` to `1.9923747660316546`.
- No-egress withheld_runtime: `PASS_REVIEW_ONLY_NO_EGRESS_WITHHELD_RUNTIME_BOUNDARY_CONTROL_LANE`.
- Withheld_runtime cases: `180`.

## What is validated

- Contract execution uses a symmetric product surrogate, not `PUBLIC_SAFE_BOUND_STEP`.
- `G(0)=I`, generator contact and second-order product behaviour are checked.
- `R_boundary_parameter,n^G g = PUBLIC_SAFE_INTEGRAL public_weight(t) [G(t/n)]^n g dt` is compared with `PUBLIC_SAFE_BOUNDARY_REFERENCE`.
- `Re(boundary_parameter) > omega_contract` is treated as the certified release domain.
- `Re(boundary_parameter) <= omega_contract` is fail-closed before release.
- Error budget is explicit: `B_total = B_product + B_reference_grid + B_tail + B_reference + B_floating`.
- The a-priori certificate is a conservative theorem-domain safety envelope, not a tight error estimate.
- reference_grid is used on the infinite interval; `B_tail=0` is marked as not applicable for finite tail truncation in this bounded v1 lane.
- Finite-dimensional exact matrix boundary_control may be diagnostic-available below the certified domain; release remains withheld because theorem-domain authority is not established.

## Boundary

`review_only_bounded_contract_surrogate_boundary_control_validation_not_withheld_runtime_engine_not_external_certification`

## Next blockers

- `withheld_runtime_not_attached`
- `withheld_internal_surfaces_not_published_by_design`
- `unbounded_public_control_refinement_lane_not_executed`
- `external_blind_replay_request_published_not_completed`
