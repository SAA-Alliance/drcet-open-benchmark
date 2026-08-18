#!/usr/bin/env python3
"""Check DRCET-4 composition convergence evidence pack v1."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_DIR = REPO / "docs/benchmarks/drcet4_numerical_release_control_v1_20260816"
ARTIFACT_ID = "DRCET4_NUMERICAL_RELEASE_CONTROL_CONVERGENCE_V1"
STATUS_FILE = "DRCET4_NUMERICAL_RELEASE_CONTROL_STATUS.json"
EXPECTED_STATUS = "PROTOCOL_AND_LINEAR_EXACT_CORE_ATTACHED_ARIN22_CONTAINER_PENDING"
EXPECTED_STATUS_WITH_CONTAINER = "PROTOCOL_LINEAR_EXACT_CORE_AND_REVIEW_CONTAINER_PROBE_ATTACHED_PRODUCTION_ARIN22_PENDING"
EXPECTED_STATUS_FULL_CONTAINER_A6 = "PROTOCOL_FULL_LINEAR_EXACT_CONTAINER_PROBE_ATTACHED_A6_SPECTRAL_GATE_PRODUCTION_ARIN22_PENDING"
EXPECTED_STATUS_WITH_FOUNDATION = "PROTOCOL_FULL_LINEAR_EXACT_CONTAINER_AND_FOUNDATION_LANE_VALIDATED_PRODUCTION_ARIN22_PENDING"
STEP_COUNTS = [4, 8, 16, 32, 64, 128, 256, 512]
FOUNDATION_STEP_COUNTS = [8, 16, 32, 64, 128, 256, 512, 1024]
SOLVERS = {
    "LIE_AB",
    "LIE_BA",
    "STRANG_ABA",
    "STRANG_BAB",
    "YOSHIDA4",
    "DOP853",
    "BDF",
    "ARIN22_ROUTED_PROXY",
}
REQUIRED_FILES = {
    STATUS_FILE,
    "DRCET4_PROTOCOL_V1.md",
    "fixture_contract.csv",
    "solver_resolution_results.csv",
    "convergence_order_summary.csv",
    "route_confusion_matrix.csv",
    "bound_utilization_summary.csv",
    "a1_commuting_sanity.csv",
    "a6_near_critical_spectral_summary.csv",
    "a6_route_spectral_gate_summary.csv",
    "a6_spectral_step_summary.csv",
    "a6_spectral_slope_summary.csv",
    "a6_spectral_conjugacy_slope_consistency.csv",
    "a6_spectral_slope_bootstrap_summary.csv",
    "route_overhead_summary.csv",
    "pressure_lane_summary.csv",
    "operator_spectral_conjugacy_diagnostics.csv",
    "spectral_conjugacy_class_summary.csv",
    "method_admissibility_summary.csv",
    "a6_solver_pairing_summary.csv",
    "protected_container_linear_exact_input.json",
    "protected_container_linear_exact_output.json",
    "protected_container_linear_exact_probe.json",
    "foundation_product_fixture_contract.csv",
    "foundation_product_convergence_results.csv",
    "foundation_product_convergence_summary.csv",
    "foundation_product_tangent_stability_summary.csv",
    "foundation_product_protected_container_input.json",
    "foundation_product_protected_container_output.json",
    "foundation_product_protected_container_probe.json",
    "production_arin22_foundation_product_container_input.json",
    "production_arin22_foundation_product_container_output.json",
    "production_arin22_foundation_product_container_probe.json",
    "external_blind_replay_request.json",
    "external_blind_replay_receipt.json",
    "invariant_results.csv",
    "hypotheses.json",
    "reference_policy.json",
    "acceptance_rules.json",
    "loglog_convergence_linear_exact.svg",
    "commutator_pressure_vs_bound_utilization.svg",
    "a6_spectral_abscissa_vs_step_count.svg",
    "foundation_product_loglog_convergence.svg",
    "README.md",
    "artifact_manifest.json",
}
REQUIRED_BLOCKERS = {
    "production_arin22_container_not_attached",
    "nonlinear_manufactured_lane_not_executed",
    "jump_regime_discontinuity_lane_not_executed",
    "graph_bifurcation_lanes_not_executed",
    "external_blind_replay_request_published_not_completed",
    "N3_fresh_process_timing_and_energy_not_attached",
}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def as_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def as_float(value: str) -> float | None:
    if value == "":
        return None
    return float(value)


def check_manifest(pack_dir: Path) -> tuple[str, dict[str, Any]]:
    manifest_path = pack_dir / "artifact_manifest.json"
    manifest = read_json(manifest_path)
    if manifest.get("artifact_id") != ARTIFACT_ID:
        fail("artifact_manifest artifact_id mismatch")
    listed = {row.get("path"): row for row in manifest.get("files", [])}
    expected_listed = REQUIRED_FILES - {"artifact_manifest.json"}
    if set(listed) != expected_listed:
        missing = sorted(expected_listed - set(listed))
        extra = sorted(set(listed) - expected_listed)
        fail(f"artifact_manifest file set mismatch missing={missing} extra={extra}")
    for name, row in listed.items():
        path = pack_dir / name
        if not path.exists():
            fail(f"manifest-listed file missing: {name}")
        observed_sha = sha256_file(path)
        observed_len = path.stat().st_size
        if row.get("sha256") != observed_sha:
            fail(f"sha mismatch for {name}: {row.get('sha256')} != {observed_sha}")
        if int(row.get("byte_length", -1)) != observed_len:
            fail(f"byte_length mismatch for {name}")
    return sha256_file(manifest_path), manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Check DRCET-4 composition convergence v1 pack")
    parser.add_argument("--pack-dir", default=str(DEFAULT_DIR))
    args = parser.parse_args()
    pack_dir = Path(args.pack_dir)
    if not pack_dir.exists():
        fail(f"pack directory not found: {pack_dir}")

    missing_files = sorted(name for name in REQUIRED_FILES if not (pack_dir / name).exists())
    if missing_files:
        fail(f"required files missing: {missing_files}")

    status = read_json(pack_dir / STATUS_FILE)
    fixtures = read_csv(pack_dir / "fixture_contract.csv")
    rows = read_csv(pack_dir / "solver_resolution_results.csv")
    order_rows = read_csv(pack_dir / "convergence_order_summary.csv")
    bound_rows = read_csv(pack_dir / "bound_utilization_summary.csv")
    a1_rows = read_csv(pack_dir / "a1_commuting_sanity.csv")
    a6_rows = read_csv(pack_dir / "a6_near_critical_spectral_summary.csv")
    a6_gate_rows = read_csv(pack_dir / "a6_route_spectral_gate_summary.csv")
    a6_step_rows = read_csv(pack_dir / "a6_spectral_step_summary.csv")
    a6_slope_rows = read_csv(pack_dir / "a6_spectral_slope_summary.csv")
    a6_conjugacy_slope_rows = read_csv(pack_dir / "a6_spectral_conjugacy_slope_consistency.csv")
    a6_slope_bootstrap_rows = read_csv(pack_dir / "a6_spectral_slope_bootstrap_summary.csv")
    overhead_rows = read_csv(pack_dir / "route_overhead_summary.csv")
    pressure_rows = read_csv(pack_dir / "pressure_lane_summary.csv")
    conjugacy_rows = read_csv(pack_dir / "operator_spectral_conjugacy_diagnostics.csv")
    conjugacy_class_rows = read_csv(pack_dir / "spectral_conjugacy_class_summary.csv")
    admissibility_rows = read_csv(pack_dir / "method_admissibility_summary.csv")
    a6_pairing_rows = read_csv(pack_dir / "a6_solver_pairing_summary.csv")
    route_rows = read_csv(pack_dir / "route_confusion_matrix.csv")
    foundation_fixture_rows = read_csv(pack_dir / "foundation_product_fixture_contract.csv")
    foundation_result_rows = read_csv(pack_dir / "foundation_product_convergence_results.csv")
    foundation_summary_rows = read_csv(pack_dir / "foundation_product_convergence_summary.csv")
    foundation_tangent_rows = read_csv(pack_dir / "foundation_product_tangent_stability_summary.csv")
    manifest_sha, _manifest = check_manifest(pack_dir)

    if status.get("artifact_id") != ARTIFACT_ID:
        fail("status artifact_id mismatch")
    if status.get("status") not in {EXPECTED_STATUS, EXPECTED_STATUS_WITH_CONTAINER, EXPECTED_STATUS_FULL_CONTAINER_A6, EXPECTED_STATUS_WITH_FOUNDATION}:
        fail(f"unexpected pack status: {status.get('status')}")
    if status.get("linear_exact_fixture_count") != 48:
        fail("status linear_exact_fixture_count must be 48")
    if len(fixtures) != 48:
        fail(f"fixture_contract rows must be 48, got {len(fixtures)}")
    if status.get("step_counts") != STEP_COUNTS:
        fail("status step_counts mismatch")
    if {int(r["step_count"]) for r in rows} != set(STEP_COUNTS):
        fail("solver row step_count set mismatch")
    if {r["solver"] for r in rows} != SOLVERS:
        fail("solver set mismatch")
    expected_rows = 48 * len(STEP_COUNTS) * len(SOLVERS)
    if len(rows) != expected_rows:
        fail(f"solver rows mismatch: expected {expected_rows}, got {len(rows)}")
    route_proxy_rows = [r for r in rows if r["solver"] == "ARIN22_ROUTED_PROXY"]
    expected_route_rows = 48 * len(STEP_COUNTS)
    if len(route_proxy_rows) != expected_route_rows:
        fail(f"route proxy rows mismatch: expected {expected_route_rows}, got {len(route_proxy_rows)}")
    if status.get("solver_resolution_rows") != expected_rows:
        fail("status solver_resolution_rows mismatch")
    if status.get("arin22_proxy_rows") != expected_route_rows:
        fail("status arin22_proxy_rows mismatch")

    blockers = set(status.get("blockers", []))
    if not REQUIRED_BLOCKERS.issubset(blockers):
        fail(f"required blockers missing: {sorted(REQUIRED_BLOCKERS - blockers)}")
    boundary = status.get("protected_kernel_boundary", {})
    if boundary.get("production_arin22_container_attached") is not False:
        fail("production ARIN22 container must be explicitly unattached")
    if boundary.get("public_route_proxy_used") is not True:
        fail("public route proxy boundary missing")
    if "not the protected production implementation" not in boundary.get("statement", ""):
        fail("route proxy boundary statement is not explicit enough")
    if "production_ARIN22_solver_superiority" not in status.get("must_not_claim", []):
        fail("must_not_claim must forbid production ARIN22 superiority")

    silent_rows = []
    released_bound_breaches = []
    for row in route_proxy_rows:
        if as_bool(row["silent_bound_breach"]):
            silent_rows.append(row)
        err = as_float(row["terminal_abs_error"])
        bound = as_float(row["declared_error_bound"])
        if as_bool(row["released"]) and err is not None and bound is not None and err > bound + 1e-15:
            released_bound_breaches.append(row)
        if row["status"] == "FAIL_SILENT_BOUND_BREACH":
            released_bound_breaches.append(row)
    if silent_rows:
        fail(f"silent_bound_breach rows present: {len(silent_rows)}")
    if released_bound_breaches:
        fail(f"released E>B rows present: {len(released_bound_breaches)}")
    if status.get("silent_bound_breach_released_count") != 0:
        fail("status silent_bound_breach_released_count must be 0")
    if status.get("invariant_failure_released_count") != 0:
        fail("status invariant_failure_released_count must be 0")

    family_counts = Counter(r["family"] for r in fixtures)
    expected_families = {
        "A1_commuting_control": 4,
        "A2_rotation_shear": 8,
        "A3_random_stable": 12,
        "A4_stiff_stable": 8,
        "A5_positivity_preserving": 8,
        "A6_near_critical": 8,
    }
    if dict(family_counts) != expected_families:
        fail(f"fixture family counts mismatch: {dict(family_counts)}")

    medians = status.get("smooth_canonical_observed_order_median", {})
    lie = medians.get("LIE_AB")
    strang = medians.get("STRANG_ABA")
    if not isinstance(lie, (int, float)) or not isinstance(strang, (int, float)):
        fail("smooth canonical median orders must be numeric")
    if not strang > lie:
        fail(f"Strang median order should exceed Lie median order, got Lie={lie}, Strang={strang}")
    if len(order_rows) != 48 * len(SOLVERS):
        fail(f"convergence_order_summary rows must be 384, got {len(order_rows)}")
    order_counts = Counter(r["status"] for r in order_rows)
    if order_counts.get("NOT_APPLICABLE_ADAPTIVE_MONOLITHIC_ORDER_NOT_GRID_DEFINED", 0) != 96:
        fail(f"adaptive N/A order rows must be 96, got {order_counts}")
    if order_counts.get("NOT_APPLICABLE_NEGATIVE_SUBSTEPS_ON_POSITIVITY_LANE", 0) != 8:
        fail(f"Yoshida positivity N/A order rows must be 8, got {order_counts}")
    if status.get("convergence_order_summary_rows") != 48 * len(SOLVERS):
        fail("status convergence_order_summary_rows mismatch")
    if not bound_rows or not any(r["family"] == "ALL" for r in bound_rows):
        fail("bound_utilization_summary missing ALL row")
    all_bound = next(r for r in bound_rows if r["family"] == "ALL")
    if int(all_bound["rows"]) != expected_route_rows:
        fail("bound utilization ALL row count mismatch")
    if float(all_bound["fraction_r_gt_0_90_released"]) < 0:
        fail("bound utilization fraction not populated")
    if not a1_rows or len(a1_rows) != len(SOLVERS):
        fail("a1_commuting_sanity must cover all solvers")
    split_a1 = [r for r in a1_rows if r["solver"] not in {"DOP853", "BDF"}]
    if max(float(r["max_terminal_abs_error"]) for r in split_a1) > 1e-10:
        fail("A1 split sanity is above rounding-floor tolerance")
    if not a6_rows:
        fail("a6_near_critical_spectral_summary is empty")
    if max(float(r["max_spectral_abscissa_abs_error"]) for r in a6_rows) <= 0:
        fail("A6 spectral-abscissa error was not populated")
    if len(a6_gate_rows) != 1:
        fail("a6_route_spectral_gate_summary must contain one ALL-A6 row")
    a6_gate = a6_gate_rows[0]
    if int(a6_gate["route_rows"]) != 8 * len(STEP_COUNTS):
        fail("A6 route spectral gate row count mismatch")
    if int(a6_gate["spectral_triggered_route_rows"]) <= 0:
        fail("A6 spectral gate must trigger at least one route/recompression decision")
    for row in route_proxy_rows:
        if row["family"] != "A6_near_critical":
            continue
        bound = as_float(row.get("spectral_abscissa_declared_bound", ""))
        err = as_float(row.get("spectral_abscissa_abs_error", ""))
        if as_bool(row["released"]) and bound is not None and err is not None and err > bound + 1e-15:
            fail(f"A6 released with spectral-abscissa bound breach: {row['case_id']} n={row['step_count']}")
    if "Track 1 computes exp(hA)" not in status.get("track1_stiffness_caveat", ""):
        fail("Track 1 stiffness caveat missing")
    expected_a6_step_rows = 6 * len(STEP_COUNTS)
    if len(a6_step_rows) != expected_a6_step_rows:
        fail(f"a6_spectral_step_summary rows must be {expected_a6_step_rows}, got {len(a6_step_rows)}")
    if len(a6_slope_rows) != 6:
        fail(f"a6_spectral_slope_summary rows must be 6, got {len(a6_slope_rows)}")
    lie_slope_row = next((r for r in a6_slope_rows if r["solver"] == "LIE_AB"), None)
    if not lie_slope_row:
        fail("A6 slope summary missing LIE_AB")
    lie_primary = as_float(lie_slope_row["slope_primary_window"])
    if lie_primary is None or not (1.7 <= lie_primary <= 2.3):
        fail(f"A6 AB conjugacy-class LIE_AB e_lambda diagnostic must decay near h^2 on primary window, got {lie_primary}")
    if lie_slope_row["finding"] != "AB_CONJUGACY_CLASS_A6_E_LAMBDA_DECAYS_AS_H2_NOT_METHOD_RANKING":
        fail("LIE_AB A6 slope finding must preserve conjugacy/not-ranking boundary")
    strang_slope_row = next((r for r in a6_slope_rows if r["solver"] == "STRANG_ABA"), None)
    if not strang_slope_row:
        fail("A6 slope summary missing STRANG_ABA")
    strang_primary = as_float(strang_slope_row["slope_primary_window"])
    if strang_primary is None or not (1.7 <= strang_primary <= 2.3):
        fail(f"A6 AB conjugacy-class e_lambda diagnostic must decay near h^2 on primary window, got {strang_primary}")
    if strang_slope_row["finding"] != "AB_CONJUGACY_CLASS_A6_E_LAMBDA_DECAYS_AS_H2_NOT_METHOD_RANKING":
        fail("A6 slope finding must preserve conjugacy/not-ranking boundary")
    if abs(lie_primary - strang_primary) >= 0.02:
        fail(f"LIE_AB and STRANG_ABA A6 e_lambda slopes must remain in the same conjugacy-class window, got {lie_primary} vs {strang_primary}")
    yoshida_slope_row = next((r for r in a6_slope_rows if r["solver"] == "YOSHIDA4"), None)
    if not yoshida_slope_row or yoshida_slope_row["finding"] != "YOSHIDA4_A6_E_LAMBDA_DECAYS_HIGH_ORDER_BEFORE_REFERENCE_FLOOR":
        fail("Yoshida A6 finding must record high-order decay before reference floor")
    if len(a6_conjugacy_slope_rows) != 2:
        fail("a6_spectral_conjugacy_slope_consistency must contain AB/BA rows")
    for row in a6_conjugacy_slope_rows:
        if row["status"] != "PASS_CONJUGACY_CLASS_SLOPE_RECORDED_NOT_METHOD_RANKING":
            fail(f"A6 conjugacy slope row must pass/not-rank: {row}")
    if len(a6_slope_bootstrap_rows) != 6:
        fail("a6_spectral_slope_bootstrap_summary must cover 6 A6 spectral solvers")
    yoshida_boot = next((r for r in a6_slope_bootstrap_rows if r["solver"] == "YOSHIDA4"), None)
    if not yoshida_boot:
        fail("a6_spectral_slope_bootstrap_summary missing YOSHIDA4")
    if int(yoshida_boot["bootstrap_replicates_used"]) < 1000:
        fail("Yoshida A6 spectral slope bootstrap must use at least 1000 replicates")
    if as_float(yoshida_boot["ci95_low"]) is None or as_float(yoshida_boot["ci95_high"]) is None:
        fail("Yoshida A6 spectral slope bootstrap CI missing")
    proxy_overhead = next((r for r in overhead_rows if r["solver"] == "ARIN22_ROUTED_PROXY"), None)
    if not proxy_overhead:
        fail("route_overhead_summary missing ARIN22_ROUTED_PROXY")
    p95_ratio = as_float(proxy_overhead["proxy_vs_strang_aba_p95_ratio"])
    if p95_ratio is None or not (7.0 <= p95_ratio <= 20.0):
        fail(f"proxy p95 overhead ratio must preserve material routing/governor overhead vs Strang, got {p95_ratio}")
    pressure_by_family = {r["family"]: r for r in pressure_rows}
    if set(pressure_by_family) != {"A2_rotation_shear", "A5_positivity_preserving"}:
        fail(f"pressure_lane_summary must contain A2/A5 only, got {sorted(pressure_by_family)}")
    a2_pressure = pressure_by_family["A2_rotation_shear"]
    a5_pressure = pressure_by_family["A5_positivity_preserving"]
    if as_float(a2_pressure["max_r_all"]) is None or as_float(a2_pressure["max_r_all"]) < 31.0:
        fail("A2 pressure lane max r must preserve 31.7-class bound pressure")
    if int(a2_pressure["safe_fail_closed"]) != 19:
        fail(f"A2 pressure lane safe_fail_closed must be 19, got {a2_pressure['safe_fail_closed']}")
    if as_float(a5_pressure["max_r_all"]) is None or as_float(a5_pressure["max_r_all"]) < 18.0:
        fail("A5 pressure lane max r must preserve 18.4-class bound pressure")
    if int(a5_pressure["safe_fail_closed"]) != 11:
        fail(f"A5 pressure lane safe_fail_closed must be 11, got {a5_pressure['safe_fail_closed']}")
    article_findings = status.get("article_readiness_findings") or {}
    if article_findings.get("a6_conjugacy_class_e_lambda_h2_observed") is not True:
        fail("article_readiness_findings must record A6 conjugacy-class h^2 e_lambda diagnostic")
    if article_findings.get("a6_e_lambda_slope_use") != "gate_diagnostic_only_not_method_ranking":
        fail("article_readiness_findings must forbid using A6 e_lambda slope as method ranking")
    if article_findings.get("a6_e_lambda_slope_attribution") != "conjugacy_class_not_strang_order":
        fail("article_readiness_findings must attribute A6 e_lambda slope to conjugacy class, not Strang order")
    if article_findings.get("method_order_evidence_basis") != "terminal_solution_error_not_e_lambda":
        fail("article_readiness_findings must bind method order evidence to terminal solution error")
    if article_findings.get("overhead_public_claim_allowed") is not False:
        fail("route overhead ratio must remain blocked as a public claim until N>=3 timing")
    yoshida_ci = article_findings.get("a6_yoshida_spectral_slope_bootstrap_ci95") or {}
    if as_float(yoshida_ci.get("ci95_low")) is None or as_float(yoshida_ci.get("ci95_high")) is None:
        fail("article_readiness_findings must expose Yoshida A6 spectral slope bootstrap CI")
    if article_findings.get("production_kernel_boundary") != "production ARIN22 container remains untested":
        fail("article_readiness_findings must preserve production kernel boundary")
    expected_conjugacy_rows = 48 * len(STEP_COUNTS) * 2
    expected_conjugacy_formula = f"48 fixtures * {len(STEP_COUNTS)} step counts * 2 Lie/Strang conjugacy pairs = {expected_conjugacy_rows}"
    expected_conjugacy_pairs = [
        "AB_LIE_STRANG_SIMILAR_PROPAGATOR_CLASS:LIE_AB~STRANG_ABA",
        "BA_LIE_STRANG_SIMILAR_PROPAGATOR_CLASS:LIE_BA~STRANG_BAB",
    ]
    conjugacy_summary = status.get("spectral_conjugacy_verification") or {}
    if conjugacy_summary.get("diagnostic_rows") != expected_conjugacy_rows:
        fail("spectral_conjugacy_verification must expose the 768 diagnostic-row count")
    if conjugacy_summary.get("denominator_formula") != expected_conjugacy_formula:
        fail("spectral_conjugacy_verification must expose the 768-row denominator formula")
    if conjugacy_summary.get("fixture_count") != 48 or conjugacy_summary.get("step_counts_per_fixture") != STEP_COUNTS:
        fail("spectral_conjugacy_verification must expose fixture count and step counts")
    if conjugacy_summary.get("conjugacy_pair_count") != 2 or conjugacy_summary.get("pairs_checked") != expected_conjugacy_pairs:
        fail("spectral_conjugacy_verification must expose both Lie/Strang conjugacy pairs")
    if len(conjugacy_rows) != expected_conjugacy_rows:
        fail(f"operator_spectral_conjugacy_diagnostics rows must be {expected_conjugacy_rows}, got {len(conjugacy_rows)}")
    max_conjugacy_residual = max(float(r["relative_conjugacy_residual"]) for r in conjugacy_rows)
    max_eigen_delta = max(float(r["max_eigenvalue_abs_delta"]) for r in conjugacy_rows)
    if max_conjugacy_residual >= 1e-12:
        fail(f"Lie/Strang conjugacy residual must be <1e-12, got {max_conjugacy_residual}")
    if max_eigen_delta >= 1e-12:
        fail(f"Lie/Strang eigenvalue delta must be <1e-12, got {max_eigen_delta}")
    class_by_id = {r["conjugacy_class"]: r for r in conjugacy_class_rows}
    for class_id in {"AB_LIE_STRANG_SIMILAR_PROPAGATOR_CLASS", "BA_LIE_STRANG_SIMILAR_PROPAGATOR_CLASS"}:
        row = class_by_id.get(class_id)
        if not row or row["status"] != "PASS" or row["e_lambda_method_ranking_allowed"].lower() != "false":
            fail(f"spectral conjugacy class summary invalid for {class_id}: {row}")
    yoshida_adm = next((r for r in admissibility_rows if r["solver"] == "YOSHIDA4"), None)
    if not yoshida_adm:
        fail("method_admissibility_summary missing YOSHIDA4")
    if yoshida_adm["negative_substep_present"].lower() != "true" or yoshida_adm["admissible_on_irreversible"].lower() != "false":
        fail("Yoshida4 must be marked negative-substep/non-admissible on irreversible lanes")
    proxy_adm = next((r for r in admissibility_rows if r["solver"] == "ARIN22_ROUTED_PROXY"), None)
    if not proxy_adm or proxy_adm["layer_tested"] != "routing_governor_proxy" or proxy_adm["kernel_construction_exercised"].lower() != "false":
        fail("ARIN22_ROUTED_PROXY must be explicitly routing layer only with kernel_construction_exercised=false")
    if len(a6_pairing_rows) != len(SOLVERS):
        fail("a6_solver_pairing_summary must cover all solvers")
    for row in a6_pairing_rows:
        if int(row["row_count"]) != 64 or row["status"] != "PASS_PAIRED_A6_ROWS":
            fail(f"A6 pairing failed for {row['solver']}: {row}")
    if article_findings.get("e_lambda_method_ranking_allowed") is not False:
        fail("article_readiness_findings must forbid e_lambda method ranking")
    if article_findings.get("lie_strang_spectral_conjugacy_confirmed") is not True:
        fail("article_readiness_findings must confirm Lie/Strang spectral conjugacy")
    if article_findings.get("yoshida4_negative_substep_present") is not True or article_findings.get("yoshida4_admissible_on_irreversible") is not False:
        fail("article_readiness_findings must preserve Yoshida4 negative-substep boundary")
    if article_findings.get("spectral_conjugacy_denominator_formula") != expected_conjugacy_formula:
        fail("article_readiness_findings must expose the 768-row conjugacy denominator formula")
    if not route_rows:
        fail("route_confusion_matrix is empty")

    probe = read_json(pack_dir / "protected_container_linear_exact_probe.json")
    probe_input = read_json(pack_dir / "protected_container_linear_exact_input.json")
    probe_output = read_json(pack_dir / "protected_container_linear_exact_output.json")
    if probe_input.get("schema_id") != "saa.benchmark.drcet4.linear_exact_container_input.v1":
        fail("protected container input schema mismatch")
    if probe_output.get("schema_id") != "saa.benchmark.drcet4.linear_exact_container_output.v1":
        fail("protected container output schema mismatch")
    if probe.get("input_sha256") != sha256_file(pack_dir / "protected_container_linear_exact_input.json"):
        fail("protected container input sha mismatch")
    if probe.get("output_sha256") != sha256_file(pack_dir / "protected_container_linear_exact_output.json"):
        fail("protected container output sha mismatch")
    probe_status = probe.get("status")
    if probe_status == "PASS_REVIEW_ONLY_NO_EGRESS_CONTAINER_LINEAR_EXACT_CORE":
        if boundary.get("protected_linear_exact_container_attached") is not True:
            fail("container PASS must set protected_linear_exact_container_attached=true")
        if "protected_linear_exact_container_not_attached" in blockers:
            fail("container PASS must remove protected_linear_exact_container_not_attached blocker")
        if probe.get("container_runtime") != "docker" or probe.get("network_mode") != "none":
            fail("container PASS must be docker/no-egress")
        if probe.get("covered_fixture_count") != 48 or probe.get("total_fixture_count") != 48:
            fail("container PASS must cover all 48 linear fixtures")
        if abs(float(probe.get("coverage_fraction", 0)) - 1.0) > 1e-12:
            fail("container PASS coverage_fraction must be 1.0")
        if probe.get("case_count") != 48 * 2:
            fail("container PASS must include 96 cases: 48 fixtures x 2 solvers")
        expected_family_coverage = {
            "A1_commuting_control": 4,
            "A2_rotation_shear": 8,
            "A3_random_stable": 12,
            "A4_stiff_stable": 8,
            "A5_positivity_preserving": 8,
            "A6_near_critical": 8,
        }
        observed_family_coverage = probe.get("family_fixture_coverage") or {}
        for family, total in expected_family_coverage.items():
            row = observed_family_coverage.get(family) or {}
            if row.get("covered_fixtures") != total or row.get("total_fixtures") != total:
                fail(f"container family coverage mismatch for {family}: {row}")
        if "4096 * eps64" not in json.dumps(probe.get("delta_tolerance_policy", {})):
            fail("container tolerance policy is missing or not predeclared")
        delta = probe.get("max_abs_delta_vs_python_linear_core")
        ratio = probe.get("max_delta_to_tolerance_ratio")
        if not isinstance(delta, (int, float)) or not isinstance(ratio, (int, float)) or float(ratio) > 1.0:
            fail("container PASS delta missing or above predeclared tolerance")
        delta_row = probe.get("max_abs_delta_row") or {}
        ratio_row = probe.get("max_delta_to_tolerance_ratio_row") or {}
        if not isinstance(delta_row, dict) or not isinstance(ratio_row, dict):
            fail("container PASS must disclose max delta and max delta/tolerance rows")
        for label, row in {"max_abs_delta_row": delta_row, "max_delta_to_tolerance_ratio_row": ratio_row}.items():
            if not row.get("case_id") or not row.get("solver"):
                fail(f"container {label} missing case_id/solver")
            if as_float(row.get("delta")) is None or as_float(row.get("delta_tolerance")) is None or as_float(row.get("delta_to_tolerance_ratio")) is None:
                fail(f"container {label} missing delta/tolerance/ratio")
        if abs(float(delta) - float(delta_row["delta"])) > 1e-18:
            fail("container max_abs_delta must equal max_abs_delta_row.delta")
        row_ratio = float(ratio_row["delta"]) / max(float(ratio_row["delta_tolerance"]), 1e-300)
        if abs(row_ratio - float(ratio_row["delta_to_tolerance_ratio"])) > 1e-15:
            fail("container ratio row must satisfy delta_to_tolerance_ratio = delta / delta_tolerance")
        if abs(float(ratio) - float(ratio_row["delta_to_tolerance_ratio"])) > 1e-18:
            fail("container max_delta_to_tolerance_ratio must equal the ratio row value")
        same_row = delta_row.get("case_id") == ratio_row.get("case_id") and delta_row.get("solver") == ratio_row.get("solver")
        expected_relation = "same_row" if same_row else "different_rows"
        if probe.get("max_delta_ratio_case_relation") != expected_relation:
            fail(f"container delta/ratio case relation must be {expected_relation}, got {probe.get('max_delta_ratio_case_relation')}")
        if probe.get("max_delta_and_ratio_same_row") is not same_row:
            fail("container max_delta_and_ratio_same_row must match row identity")
        if "row-wise max(delta / row_delta_tolerance)" not in str(probe.get("max_delta_to_tolerance_ratio_interpretation")):
            fail("container ratio interpretation must state row-wise formula")
        if probe_output.get("case_count") != len(probe_input.get("cases") or []):
            fail("container PASS output case count mismatch")
    else:
        if boundary.get("protected_linear_exact_container_attached") is not False:
            fail("non-PASS probe must set protected_linear_exact_container_attached=false")
        if "protected_linear_exact_container_not_attached" not in blockers:
            fail("non-PASS probe must keep protected_linear_exact_container_not_attached blocker")
        if not probe.get("blockers"):
            fail("non-PASS probe must list blockers")

    if len(foundation_fixture_rows) != 6:
        fail(f"foundation_product_fixture_contract rows must be 6, got {len(foundation_fixture_rows)}")
    if len(foundation_result_rows) != 6 * len(FOUNDATION_STEP_COUNTS):
        fail(f"foundation_product_convergence_results rows must be {6 * len(FOUNDATION_STEP_COUNTS)}, got {len(foundation_result_rows)}")
    if len(foundation_tangent_rows) != 6:
        fail(f"foundation_product_tangent_stability_summary rows must be 6, got {len(foundation_tangent_rows)}")
    if len(foundation_summary_rows) != 1:
        fail("foundation_product_convergence_summary must contain exactly one row")
    if {int(r["step_count_n"]) for r in foundation_result_rows} != set(FOUNDATION_STEP_COUNTS):
        fail("foundation step counts mismatch")
    if {r["foundation_function_G"] for r in foundation_fixture_rows} != {"I + tL"}:
        fail("foundation fixture contract must bind G(t)=I+tL")
    if {r["semigroup_reference"] for r in foundation_fixture_rows} != {"expm(tL)"}:
        fail("foundation fixture contract must bind S(t)=exp(tL)")
    if any(r["operator_contract_L"] != "bounded_matrix_generator" for r in foundation_fixture_rows):
        fail("foundation operator contract must be bounded_matrix_generator for this lane")
    for row in foundation_result_rows:
        if row["lane_id"] != "DRCET4B_FOUNDATION_PRODUCT_CONVERGENCE_LANE":
            fail("foundation lane_id mismatch")
        if row["status"] != "PASS":
            fail(f"foundation result row did not PASS: {row['case_id']} n={row['step_count_n']} status={row['status']}")
        if not as_bool(row["tangent_check_pass"]):
            fail(f"foundation tangent check failed for {row['case_id']} n={row['step_count_n']}")
        if not as_bool(row["stability_check_pass"]):
            fail(f"foundation stability check failed for {row['case_id']} n={row['step_count_n']}")
        if not as_bool(row["certificate_E_n_le_B_n"]):
            fail(f"foundation E_n <= B_n failed for {row['case_id']} n={row['step_count_n']}")
        if as_float(row["S0_identity_error"]) is None or as_float(row["S0_identity_error"]) > 1e-14:
            fail(f"foundation S(0)=I check failed for {row['case_id']}")
        if as_float(row["bound_utilization_E_over_B"]) is None or as_float(row["bound_utilization_E_over_B"]) > 1.0:
            fail(f"foundation bound utilization above 1 for {row['case_id']} n={row['step_count_n']}")
    for row in foundation_tangent_rows:
        if row["status"] != "PASS":
            fail(f"foundation tangent/stability row did not PASS: {row['case_id']}")
        observed = as_float(row["observed_convergence_rate"])
        if observed is None or not (0.75 <= observed <= 1.25):
            fail(f"foundation observed convergence rate outside first-order band for {row['case_id']}: {observed}")
        if int(row["certificate_failures"]) != 0:
            fail(f"foundation certificate failures present for {row['case_id']}")

    foundation_summary = status.get("drcet4b_foundation_product_convergence_lane") or {}
    if foundation_summary.get("lane_id") != "DRCET4B_FOUNDATION_PRODUCT_CONVERGENCE_LANE":
        fail("status missing DRCET4B lane summary")
    if foundation_summary.get("fixture_count") != 6 or foundation_summary.get("result_rows") != 6 * len(FOUNDATION_STEP_COUNTS):
        fail("DRCET4B lane summary fixture/result counts mismatch")
    if foundation_summary.get("step_counts") != FOUNDATION_STEP_COUNTS:
        fail("DRCET4B lane summary step counts mismatch")
    csv_lane_status = foundation_summary_rows[0].get("status")
    if csv_lane_status != foundation_summary.get("status"):
        fail("DRCET4B CSV summary status must match JSON status")
    foundation_probe = read_json(pack_dir / "foundation_product_protected_container_probe.json")
    foundation_probe_input = read_json(pack_dir / "foundation_product_protected_container_input.json")
    foundation_probe_output = read_json(pack_dir / "foundation_product_protected_container_output.json")
    if foundation_probe_input.get("schema_id") != "saa.benchmark.drcet4.foundation_product_container_input.v1":
        fail("foundation container input schema mismatch")
    if foundation_probe_output.get("schema_id") != "saa.benchmark.drcet4.foundation_product_container_output.v1":
        fail("foundation container output schema mismatch")
    if foundation_probe.get("input_sha256") != sha256_file(pack_dir / "foundation_product_protected_container_input.json"):
        fail("foundation container input sha mismatch")
    if foundation_probe.get("output_sha256") != sha256_file(pack_dir / "foundation_product_protected_container_output.json"):
        fail("foundation container output sha mismatch")
    foundation_probe_status = foundation_probe.get("status")
    if foundation_summary.get("status") == "VALIDATED_PASS_REVIEW_ONLY_FOUNDATION_CONVERGENCE_LANE":
        if foundation_probe_status != "PASS_REVIEW_ONLY_NO_EGRESS_CONTAINER_FOUNDATION_LANE":
            fail("DRCET4B VALIDATED/PASS requires protected no-egress container PASS")
        if foundation_probe.get("container_runtime") != "docker" or foundation_probe.get("network_mode") != "none":
            fail("DRCET4B container PASS must be docker/no-egress")
        if foundation_probe.get("case_count") != 6 * len(FOUNDATION_STEP_COUNTS):
            fail("DRCET4B container case count mismatch")
        if foundation_probe.get("covered_fixture_count") != 6 or foundation_probe.get("total_fixture_count") != 6:
            fail("DRCET4B container fixture coverage mismatch")
        ratio = foundation_probe.get("max_delta_to_tolerance_ratio")
        if not isinstance(ratio, (int, float)) or float(ratio) > 1.0:
            fail("DRCET4B container delta ratio missing or above tolerance")
        if status.get("status") != EXPECTED_STATUS_WITH_FOUNDATION:
            fail("overall DRCET-4 status must include foundation validation when DRCET4B passes")
    else:
        if foundation_summary.get("status") != "CONTRACT_DECLARED_WATCH":
            fail(f"unexpected DRCET4B non-pass status: {foundation_summary.get('status')}")
        if foundation_probe_status == "PASS_REVIEW_ONLY_NO_EGRESS_CONTAINER_FOUNDATION_LANE":
            fail("DRCET4B container PASS cannot leave lane in CONTRACT_DECLARED_WATCH")
        if "drcet4b_foundation_product_convergence_lane_not_validated" not in blockers:
            fail("DRCET4B watch status must keep not_validated blocker")

    production_probe = read_json(pack_dir / "production_arin22_foundation_product_container_probe.json")
    production_input = read_json(pack_dir / "production_arin22_foundation_product_container_input.json")
    production_output = read_json(pack_dir / "production_arin22_foundation_product_container_output.json")
    production_summary = status.get("production_arin22_foundation_product_container_probe") or {}
    nested_production_summary = foundation_summary.get("production_arin22_protected_container_probe") or {}
    if production_probe.get("status") != "PRODUCTION_ARIN22_CONTAINER_NOT_ATTACHED":
        fail(f"production ARIN22 4B probe should remain pending in public pack, got {production_probe.get('status')}")
    if production_summary.get("status") != production_probe.get("status"):
        fail("production ARIN22 4B summary/probe status mismatch")
    if nested_production_summary.get("status") != production_probe.get("status"):
        fail("production ARIN22 4B nested summary/probe status mismatch")
    if production_input.get("schema_id") != "saa.benchmark.drcet4b.production_arin22_container_input.v1":
        fail("production ARIN22 4B input schema mismatch")
    if production_output.get("input_sha256") != sha256_file(pack_dir / "production_arin22_foundation_product_container_input.json"):
        fail("production ARIN22 4B output input_sha mismatch")
    if boundary.get("production_arin22_container_probe_attached") is not False:
        fail("production ARIN22 probe attached flag must remain false without real protected container execution")

    replay_request = read_json(pack_dir / "external_blind_replay_request.json")
    replay_receipt = read_json(pack_dir / "external_blind_replay_receipt.json")
    external_summary = status.get("external_blind_replay") or {}
    if replay_request.get("schema_id") != "saa.benchmark.drcet4.external_blind_replay_request.v1":
        fail("external blind replay request schema mismatch")
    if replay_receipt.get("status") != "PENDING_EXTERNAL_BLIND_REPLAY":
        fail("external blind replay receipt must remain pending until a third-party response attaches")
    if replay_receipt.get("request_sha256") != sha256_file(pack_dir / "external_blind_replay_request.json"):
        fail("external blind replay request sha mismatch")
    if external_summary.get("status") != replay_receipt.get("status"):
        fail("external blind replay summary/receipt status mismatch")

    print(json.dumps({
        "status": "PASS",
        "pack_dir": str(pack_dir),
        "pack_status": status["status"],
        "status_sha256": sha256_file(pack_dir / STATUS_FILE),
        "artifact_manifest_sha256": manifest_sha,
        "fixture_rows": len(fixtures),
        "solver_resolution_rows": len(rows),
        "route_proxy_rows": len(route_proxy_rows),
        "route_status_counts": status.get("route_status_counts"),
        "convergence_order_status_counts": status.get("convergence_order_status_counts"),
        "bound_utilization_distribution": status.get("bound_utilization_distribution"),
        "a6_route_spectral_gate_summary": status.get("a6_route_spectral_gate_summary"),
        "a6_spectral_step_slope_summary": status.get("a6_spectral_step_slope_summary"),
        "route_overhead_summary": status.get("route_overhead_summary"),
        "pressure_lane_summary": status.get("pressure_lane_summary"),
        "spectral_conjugacy_verification": status.get("spectral_conjugacy_verification"),
        "article_readiness_findings": status.get("article_readiness_findings"),
        "protected_container_linear_exact_probe": status.get("protected_container_linear_exact_probe"),
        "drcet4b_foundation_product_convergence_lane": status.get("drcet4b_foundation_product_convergence_lane"),
        "smooth_canonical_observed_order_median": medians,
        "claim_boundary": status.get("claim_boundary"),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
