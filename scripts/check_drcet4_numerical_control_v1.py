#!/usr/bin/env python3
"""Check DRCET-4 numerical-control convergence evidence pack v1."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_DIR = REPO / "docs/benchmarks/drcet4_numerical_control_v1_20260816"
ARTIFACT_ID = "DRCET4_NUMERICAL_CONTROL_V1"
STATUS_FILE = "DRCET4_NUMERICAL_CONTROL_STATUS.json"
EXPECTED_STATUS = "PROTOCOL_AND_CLOSED_FORM_CORE_ATTACHED_withheld_runtime_WITHHELD_RUNTIME_PENDING"
EXPECTED_STATUS_WITH_WITHHELD_RUNTIME = "PROTOCOL_CLOSED_FORM_CORE_AND_REVIEW_WITHHELD_RUNTIME_PROBE_ATTACHED_WITHHELD_RUNTIME_PENDING"
EXPECTED_STATUS_FULL_WITHHELD_RUNTIME_A6 = "PROTOCOL_FULL_CLOSED_FORM_WITHHELD_RUNTIME_PROBE_ATTACHED_A6_METRIC_GATE_WITHHELD_RUNTIME_PENDING"
EXPECTED_STATUS_WITH_CONTROL = "PROTOCOL_FULL_CLOSED_FORM_WITHHELD_RUNTIME_AND_BOUNDED_CONTROL_LANE_VALIDATED_WITHHELD_RUNTIME_PENDING"
STEP_COUNTS = [4, 8, 16, 32, 64, 128, 256, 512]
CONTROL_STEP_COUNTS = [8, 16, 32, 64, 128, 256, 512, 1024]
SOLVERS = {
    "METHOD_A_1",
    "METHOD_A_2",
    "METHOD_B_1",
    "METHOD_B_2",
    "METHOD_C",
    "DOP853",
    "BDF",
    "PUBLIC_RELEASE_GATED_PROXY",
}
REQUIRED_FILES = {
    STATUS_FILE,
    "DRCET4_PROTOCOL_V1.md",
    "fixture_contract.csv",
    "solver_resolution_results.csv",
    "convergence_order_summary.csv",
    "release_gate_confusion_matrix.csv",
    "bound_utilization_summary.csv",
    "a1_control_sanity.csv",
    "a6_boundary_metric_summary.csv",
    "a6_release_gate_metric_gate_summary.csv",
    "a6_metric_step_summary.csv",
    "a6_metric_slope_summary.csv",
    "a6_metric_equivalence_slope_consistency.csv",
    "a6_metric_slope_bootstrap_summary.csv",
    "release_gate_overhead_summary.csv",
    "pressure_lane_summary.csv",
    "metric_equivalence_diagnostics.csv",
    "metric_equivalence_class_summary.csv",
    "method_admissibility_summary.csv",
    "a6_solver_pairing_summary.csv",
    "sealed_replay_closed_form_input.json",
    "sealed_replay_closed_form_output.json",
    "sealed_replay_closed_form_probe.json",
    "bounded_control_fixture_contract.csv",
    "bounded_control_convergence_results.csv",
    "bounded_control_convergence_summary.csv",
    "bounded_control_contract_stability_summary.csv",
    "bounded_control_sealed_replay_input.json",
    "bounded_control_sealed_replay_output.json",
    "bounded_control_sealed_replay_probe.json",
    "withheld_runtime_bounded_control_probe_input.json",
    "withheld_runtime_bounded_control_probe_output.json",
    "withheld_runtime_bounded_control_probe.json",
    "external_blind_replay_request.json",
    "external_blind_replay_receipt.json",
    "invariant_results.csv",
    "hypotheses.json",
    "reference_policy.json",
    "acceptance_rules.json",
    "loglog_convergence_closed_form.svg",
    "stress_pressure_vs_bound_utilization.svg",
    "a6_metric_readback_vs_step_count.svg",
    "bounded_control_loglog_convergence.svg",
    "README.md",
    "artifact_manifest.json",
}
REQUIRED_BLOCKERS = {
    "withheld_runtime_not_attached",
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
    parser = argparse.ArgumentParser(description="Check DRCET-4 numerical-control convergence v1 pack")
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
    a1_rows = read_csv(pack_dir / "a1_control_sanity.csv")
    a6_rows = read_csv(pack_dir / "a6_boundary_metric_summary.csv")
    a6_gate_rows = read_csv(pack_dir / "a6_release_gate_metric_gate_summary.csv")
    a6_step_rows = read_csv(pack_dir / "a6_metric_step_summary.csv")
    a6_slope_rows = read_csv(pack_dir / "a6_metric_slope_summary.csv")
    a6_equivalence_slope_rows = read_csv(pack_dir / "a6_metric_equivalence_slope_consistency.csv")
    a6_slope_bootstrap_rows = read_csv(pack_dir / "a6_metric_slope_bootstrap_summary.csv")
    overhead_rows = read_csv(pack_dir / "release_gate_overhead_summary.csv")
    pressure_rows = read_csv(pack_dir / "pressure_lane_summary.csv")
    equivalence_rows = read_csv(pack_dir / "metric_equivalence_diagnostics.csv")
    equivalence_class_rows = read_csv(pack_dir / "metric_equivalence_class_summary.csv")
    admissibility_rows = read_csv(pack_dir / "method_admissibility_summary.csv")
    a6_pairing_rows = read_csv(pack_dir / "a6_solver_pairing_summary.csv")
    release_gate_rows = read_csv(pack_dir / "release_gate_confusion_matrix.csv")
    bounded_control_fixture_rows = read_csv(pack_dir / "bounded_control_fixture_contract.csv")
    bounded_control_result_rows = read_csv(pack_dir / "bounded_control_convergence_results.csv")
    bounded_control_summary_rows = read_csv(pack_dir / "bounded_control_convergence_summary.csv")
    bounded_control_contact_rows = read_csv(pack_dir / "bounded_control_contract_stability_summary.csv")
    manifest_sha, _manifest = check_manifest(pack_dir)

    if status.get("artifact_id") != ARTIFACT_ID:
        fail("status artifact_id mismatch")
    if status.get("status") not in {EXPECTED_STATUS, EXPECTED_STATUS_WITH_WITHHELD_RUNTIME, EXPECTED_STATUS_FULL_WITHHELD_RUNTIME_A6, EXPECTED_STATUS_WITH_CONTROL}:
        fail(f"unexpected pack status: {status.get('status')}")
    if status.get("closed_form_fixture_count") != 48:
        fail("status closed_form_fixture_count must be 48")
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
    release_gate_proxy_rows = [r for r in rows if r["solver"] == "PUBLIC_RELEASE_GATED_PROXY"]
    expected_release_gate_rows = 48 * len(STEP_COUNTS)
    if len(release_gate_proxy_rows) != expected_release_gate_rows:
        fail(f"release_gate proxy rows mismatch: expected {expected_release_gate_rows}, got {len(release_gate_proxy_rows)}")
    if status.get("solver_resolution_rows") != expected_rows:
        fail("status solver_resolution_rows mismatch")
    if status.get("withheld_runtime_proxy_rows") != expected_release_gate_rows:
        fail("status withheld_runtime_proxy_rows mismatch")

    blockers = set(status.get("blockers", []))
    if not REQUIRED_BLOCKERS.issubset(blockers):
        fail(f"required blockers missing: {sorted(REQUIRED_BLOCKERS - blockers)}")
    boundary = status.get("protected_engine_boundary", {})
    runtime_attached = boundary.get("withheld_runtime_runtime_attached", boundary.get("withheld_runtime runtime_attached"))
    if runtime_attached is not False:
        fail("withheld_runtime must be explicitly unattached")
    proxy_used = boundary.get("public_release_gate_proxy_used", boundary.get("public_release_gate_proxy_used"))
    if proxy_used is not True:
        fail("public release_gate proxy boundary missing")
    statement = boundary.get("statement", "")
    if "not the withheld implementation" not in statement and "withheld implementation" not in statement:
        fail("release_gate proxy boundary statement is not explicit enough")
    must_not_claim = {str(item).replace(" ", "_") for item in status.get("must_not_claim", [])}
    if "withheld_runtime_solver_superiority" not in must_not_claim and "production_withheld_runtime_solver_superiority" not in must_not_claim:
        fail("must_not_claim must forbid withheld_runtime superiority")

    silent_rows = []
    released_bound_breaches = []
    for row in release_gate_proxy_rows:
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
        "A1_control_fixture": 4,
        "A2_rotation_shear": 8,
        "A3_random_stable": 12,
        "A4_stiff_stable": 8,
        "A5_positivity_preserving": 8,
        "A6_boundary_fixture": 8,
    }
    if dict(family_counts) != expected_families:
        fail(f"fixture family counts mismatch: {dict(family_counts)}")

    medians = status.get("smooth_canonical_observed_order_median", {})
    lie = medians.get("METHOD_A_1")
    method_b = medians.get("METHOD_B_1")
    if not isinstance(lie, (int, float)) or not isinstance(method_b, (int, float)):
        fail("smooth canonical median orders must be numeric")
    if not method_b > lie:
        fail(f"method B median order should exceed method A median order, got method A={lie}, method B={method_b}")
    if len(order_rows) != 48 * len(SOLVERS):
        fail(f"convergence_order_summary rows must be 384, got {len(order_rows)}")
    order_counts = Counter(r["status"] for r in order_rows)
    if order_counts.get("NOT_APPLICABLE_ADAPTIVE_MONOLITHIC_ORDER_NOT_GRID_DEFINED", 0) != 96:
        fail(f"adaptive N/A order rows must be 96, got {order_counts}")
    if order_counts.get("NOT_APPLICABLE_ADMISSIBILITY_LIMITS_ON_POSITIVITY_LANE", 0) != 8:
        fail(f"method C positivity N/A order rows must be 8, got {order_counts}")
    if status.get("convergence_order_summary_rows") != 48 * len(SOLVERS):
        fail("status convergence_order_summary_rows mismatch")
    if not bound_rows or not any(r["family"] == "ALL" for r in bound_rows):
        fail("bound_utilization_summary missing ALL row")
    all_bound = next(r for r in bound_rows if r["family"] == "ALL")
    if int(all_bound["rows"]) != expected_release_gate_rows:
        fail("bound utilization ALL row count mismatch")
    if float(all_bound["fraction_r_gt_0_90_released"]) < 0:
        fail("bound utilization fraction not populated")
    if not a1_rows or len(a1_rows) != len(SOLVERS):
        fail("a1_control_sanity must cover all solvers")
    method_pair_a1 = [r for r in a1_rows if r["solver"] not in {"DOP853", "BDF"}]
    if max(float(r["max_terminal_abs_error"]) for r in method_pair_a1) > 1e-10:
        fail("A1 method_pair sanity is above rounding-floor tolerance")
    if not a6_rows:
        fail("a6_boundary_metric_summary is empty")
    if max(float(r["max_metric_readback_abs_error"]) for r in a6_rows) <= 0:
        fail("A6 boundary_metric error was not populated")
    if len(a6_gate_rows) != 1:
        fail("a6_release_gate_metric_gate_summary must contain one ALL-A6 row")
    a6_gate = a6_gate_rows[0]
    if int(a6_gate["release_gate_rows"]) != 8 * len(STEP_COUNTS):
        fail("A6 release_gate metric gate row count mismatch")
    if int(a6_gate["metric_triggered_release_gate_rows"]) <= 0:
        fail("A6 metric gate must trigger at least one release_gate/recompression decision")
    for row in release_gate_proxy_rows:
        if row["family"] != "A6_boundary_fixture":
            continue
        bound = as_float(row.get("metric_readback_declared_bound", ""))
        err = as_float(row.get("metric_readback_abs_error", ""))
        if as_bool(row["released"]) and bound is not None and err is not None and err > bound + 1e-15:
            fail(f"A6 released with boundary_metric bound breach: {row['case_id']} n={row['step_count']}")
    if "Track 1 computes closed-form component map" not in status.get("track1_stress_caveat", ""):
        fail("Track 1 stress caveat missing")
    expected_a6_step_rows = 6 * len(STEP_COUNTS)
    if len(a6_step_rows) != expected_a6_step_rows:
        fail(f"a6_metric_step_summary rows must be {expected_a6_step_rows}, got {len(a6_step_rows)}")
    if len(a6_slope_rows) != 6:
        fail(f"a6_metric_slope_summary rows must be 6, got {len(a6_slope_rows)}")
    lie_slope_row = next((r for r in a6_slope_rows if r["solver"] == "METHOD_A_1"), None)
    if not lie_slope_row:
        fail("A6 slope summary missing METHOD_A_1")
    method_a_primary = as_float(lie_slope_row["slope_primary_window"])
    if method_a_primary is None or not (1.7 <= method_a_primary <= 2.3):
        fail(f"A6 AB equivalence-class METHOD_A_1 e_boundary_parameter diagnostic must decay near h^2 on primary window, got {method_a_primary}")
    if lie_slope_row["finding"] != "AB_EQUIVALENCE_CLASS_A6_E_BOUNDARY_PARAMETER_DECAYS_AS_H2_NOT_METHOD_RANKING":
        fail("METHOD_A_1 A6 slope finding must preserve equivalence/not-ranking boundary")
    method_b_slope_row = next((r for r in a6_slope_rows if r["solver"] == "METHOD_B_1"), None)
    if not method_b_slope_row:
        fail("A6 slope summary missing METHOD_B_1")
    method_b_primary = as_float(method_b_slope_row["slope_primary_window"])
    if method_b_primary is None or not (1.7 <= method_b_primary <= 2.3):
        fail(f"A6 AB equivalence-class e_boundary_parameter diagnostic must decay near h^2 on primary window, got {method_b_primary}")
    if method_b_slope_row["finding"] != "AB_EQUIVALENCE_CLASS_A6_E_BOUNDARY_PARAMETER_DECAYS_AS_H2_NOT_METHOD_RANKING":
        fail("A6 slope finding must preserve equivalence/not-ranking boundary")
    if abs(method_a_primary - method_b_primary) >= 0.02:
        fail(f"METHOD_A_1 and METHOD_B_1 A6 e_boundary_parameter slopes must remain in the same equivalence-class window, got {method_a_primary} vs {method_b_primary}")
    method_c_slope_row = next((r for r in a6_slope_rows if r["solver"] == "METHOD_C"), None)
    if not method_c_slope_row or method_c_slope_row["finding"] != "METHOD_C_A6_E_BOUNDARY_PARAMETER_DECAYS_HIGH_ORDER_BEFORE_REFERENCE_FLOOR":
        fail("method C A6 finding must record high-order decay before reference floor")
    if len(a6_equivalence_slope_rows) != 2:
        fail("a6_metric_equivalence_slope_consistency must contain AB/BA rows")
    for row in a6_equivalence_slope_rows:
        if row["status"] != "PASS_EQUIVALENCE_CLASS_SLOPE_RECORDED_NOT_METHOD_RANKING":
            fail(f"A6 equivalence slope row must pass/not-rank: {row}")
    if len(a6_slope_bootstrap_rows) != 6:
        fail("a6_metric_slope_bootstrap_summary must cover 6 A6 metric solvers")
    method_c_boot = next((r for r in a6_slope_bootstrap_rows if r["solver"] == "METHOD_C"), None)
    if not method_c_boot:
        fail("a6_metric_slope_bootstrap_summary missing METHOD_C")
    if int(method_c_boot["bootstrap_replicates_used"]) < 1000:
        fail("method C A6 metric slope bootstrap must use at least 1000 replicates")
    if as_float(method_c_boot["ci95_low"]) is None or as_float(method_c_boot["ci95_high"]) is None:
        fail("method C A6 metric slope bootstrap CI missing")
    proxy_overhead = next((r for r in overhead_rows if r["solver"] == "PUBLIC_RELEASE_GATED_PROXY"), None)
    if not proxy_overhead:
        fail("release_gate_overhead_summary missing PUBLIC_RELEASE_GATED_PROXY")
    p95_ratio = as_float(proxy_overhead["proxy_vs_method_b_primary_p95_ratio"])
    if p95_ratio is None or not (7.0 <= p95_ratio <= 20.0):
        fail(f"proxy p95 overhead ratio must preserve material release gating/governor overhead vs method B, got {p95_ratio}")
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
    if article_findings.get("a6_equivalence_class_e_boundary_parameter_h2_observed") is not True:
        fail("article_readiness_findings must record A6 equivalence-class h^2 e_boundary_parameter diagnostic")
    if article_findings.get("a6_e_boundary_parameter_slope_use") != "gate_diagnostic_only_not_method_ranking":
        fail("article_readiness_findings must forbid using A6 e_boundary_parameter slope as method ranking")
    if article_findings.get("a6_e_boundary_parameter_slope_attribution") != "equivalence_class_not_method_b_order":
        fail("article_readiness_findings must attribute A6 e_boundary_parameter slope to equivalence class, not method B order")
    if article_findings.get("method_order_evidence_basis") != "terminal_solution_error_not_e_boundary_parameter":
        fail("article_readiness_findings must bind method order evidence to terminal solution error")
    if article_findings.get("overhead_public_claim_allowed") is not False:
        fail("release_gate overhead ratio must remain blocked as a public claim until N>=3 timing")
    method_c_ci = article_findings.get("a6_method_c_metric_slope_bootstrap_ci95") or {}
    if as_float(method_c_ci.get("ci95_low")) is None or as_float(method_c_ci.get("ci95_high")) is None:
        fail("article_readiness_findings must expose method C A6 metric slope bootstrap CI")
    if article_findings.get("withheld_runtime_boundary") != "withheld_runtime remains untested":
        fail("article_readiness_findings must preserve withheld_runtime boundary")
    expected_equivalence_rows = 48 * len(STEP_COUNTS) * 2
    expected_equivalence_formula = f"48 fixtures * {len(STEP_COUNTS)} step counts * 2 method A/method B equivalence pairs = {expected_equivalence_rows}"
    expected_equivalence_pairs = [
        "PAIR_1_METHOD_EQUIVALENCE_CLASS:METHOD_A_1~METHOD_B_1",
        "PAIR_2_METHOD_EQUIVALENCE_CLASS:METHOD_A_2~METHOD_B_2",
    ]
    equivalence_summary = status.get("metric_equivalence_verification") or {}
    if equivalence_summary.get("diagnostic_rows") != expected_equivalence_rows:
        fail("metric_equivalence_verification must expose the 768 diagnostic-row count")
    if equivalence_summary.get("denominator_formula") != expected_equivalence_formula:
        fail("metric_equivalence_verification must expose the 768-row denominator formula")
    if equivalence_summary.get("fixture_count") != 48 or equivalence_summary.get("step_counts_per_fixture") != STEP_COUNTS:
        fail("metric_equivalence_verification must expose fixture count and step counts")
    if equivalence_summary.get("equivalence_pair_count") != 2 or equivalence_summary.get("pairs_checked") != expected_equivalence_pairs:
        fail("metric_equivalence_verification must expose both method A/method B equivalence pairs")
    if len(equivalence_rows) != expected_equivalence_rows:
        fail(f"metric_equivalence_diagnostics rows must be {expected_equivalence_rows}, got {len(equivalence_rows)}")
    max_equivalence_residual = max(float(r["relative_equivalence_residual"]) for r in equivalence_rows)
    max_basis_delta = max(float(r["max_basisvalue_abs_delta"]) for r in equivalence_rows)
    if max_equivalence_residual >= 1e-12:
        fail(f"method A/method B equivalence residual must be <1e-12, got {max_equivalence_residual}")
    if max_basis_delta >= 1e-12:
        fail(f"method A/method B basisvalue delta must be <1e-12, got {max_basis_delta}")
    class_by_id = {r["equivalence_class"]: r for r in equivalence_class_rows}
    for class_id in {"PAIR_1_METHOD_EQUIVALENCE_CLASS", "PAIR_2_METHOD_EQUIVALENCE_CLASS"}:
        row = class_by_id.get(class_id)
        if not row or row["status"] != "PASS" or row["e_boundary_parameter_method_ranking_allowed"].lower() != "false":
            fail(f"metric equivalence class summary invalid for {class_id}: {row}")
    method_c_adm = next((r for r in admissibility_rows if r["solver"] == "METHOD_C"), None)
    if not method_c_adm:
        fail("method_admissibility_summary missing METHOD_C")
    if method_c_adm["admissibility_limit_present"].lower() != "true" or method_c_adm["admissible_on_irreversible"].lower() != "false":
        fail("method C must be marked negative-admissibility_marker/non-admissible on irreversible lanes")
    proxy_adm = next((r for r in admissibility_rows if r["solver"] == "PUBLIC_RELEASE_GATED_PROXY"), None)
    if not proxy_adm or proxy_adm["layer_tested"] != "public_release_gate_proxy" or proxy_adm["engine_construction_exercised"].lower() != "false":
        fail("PUBLIC_RELEASE_GATED_PROXY must be explicitly release gating layer only with engine_construction_exercised=false")
    if len(a6_pairing_rows) != len(SOLVERS):
        fail("a6_solver_pairing_summary must cover all solvers")
    for row in a6_pairing_rows:
        if int(row["row_count"]) != 64 or row["status"] != "PASS_PAIRED_A6_ROWS":
            fail(f"A6 pairing failed for {row['solver']}: {row}")
    if article_findings.get("e_boundary_parameter_method_ranking_allowed") is not False:
        fail("article_readiness_findings must forbid e_boundary_parameter method ranking")
    if article_findings.get("method_pair_metric_equivalence_confirmed") is not True:
        fail("article_readiness_findings must confirm method A/method B metric equivalence")
    if article_findings.get("method_c_admissibility_limit_present") is not True or article_findings.get("method_c_admissible_on_irreversible") is not False:
        fail("article_readiness_findings must preserve method C negative-admissibility_marker boundary")
    if article_findings.get("metric_equivalence_denominator_formula") != expected_equivalence_formula:
        fail("article_readiness_findings must expose the 768-row equivalence denominator formula")
    if not release_gate_rows:
        fail("release_gate_confusion_matrix is empty")

    probe = read_json(pack_dir / "sealed_replay_closed_form_probe.json")
    probe_input = read_json(pack_dir / "sealed_replay_closed_form_input.json")
    probe_output = read_json(pack_dir / "sealed_replay_closed_form_output.json")
    if probe_input.get("schema_id") != "saa.benchmark.drcet4.closed_form_withheld_runtime_input.v1":
        fail("sealed replay runtime input schema mismatch")
    if probe_output.get("schema_id") != "saa.benchmark.drcet4.closed_form_withheld_runtime_output.v1":
        fail("sealed replay runtime output schema mismatch")
    if probe.get("input_sha256") != sha256_file(pack_dir / "sealed_replay_closed_form_input.json"):
        fail("sealed replay runtime input sha mismatch")
    if probe.get("output_sha256") != sha256_file(pack_dir / "sealed_replay_closed_form_output.json"):
        fail("sealed replay runtime output sha mismatch")
    probe_status = probe.get("status")
    if probe_status == "PASS_REVIEW_ONLY_NO_EGRESS_WITHHELD_RUNTIME_CLOSED_FORM_CORE":
        if boundary.get("protected_closed_form_withheld_runtime_attached") is not True:
            fail("withheld_runtime PASS must set protected_closed_form_withheld_runtime_attached=true")
        if "protected_closed_form_withheld_runtime_not_attached" in blockers:
            fail("withheld_runtime PASS must remove protected_closed_form_withheld_runtime_not_attached blocker")
        if probe.get("withheld_runtime_runtime") != "docker" or probe.get("network_mode") != "none":
            fail("withheld_runtime PASS must be docker/no-egress")
        if probe.get("covered_fixture_count") != 48 or probe.get("total_fixture_count") != 48:
            fail("withheld_runtime PASS must cover all 48 linear fixtures")
        if abs(float(probe.get("coverage_fraction", 0)) - 1.0) > 1e-12:
            fail("withheld_runtime PASS coverage_fraction must be 1.0")
        if probe.get("case_count") != 48 * 2:
            fail("withheld_runtime PASS must include 96 cases: 48 fixtures x 2 solvers")
        expected_family_coverage = {
            "A1_control_fixture": 4,
            "A2_rotation_shear": 8,
            "A3_random_stable": 12,
            "A4_stiff_stable": 8,
            "A5_positivity_preserving": 8,
            "A6_boundary_fixture": 8,
        }
        observed_family_coverage = probe.get("family_fixture_coverage") or {}
        for family, total in expected_family_coverage.items():
            row = observed_family_coverage.get(family) or {}
            if row.get("covered_fixtures") != total or row.get("total_fixtures") != total:
                fail(f"withheld_runtime family coverage mismatch for {family}: {row}")
        if "4096 * eps64" not in json.dumps(probe.get("delta_tolerance_policy", {})):
            fail("withheld_runtime tolerance policy is missing or not predeclared")
        delta = probe.get("max_abs_delta_vs_public_reference")
        ratio = probe.get("max_delta_to_tolerance_ratio")
        if not isinstance(delta, (int, float)) or not isinstance(ratio, (int, float)) or float(ratio) > 1.0:
            fail("withheld_runtime PASS delta missing or above predeclared tolerance")
        delta_row = probe.get("max_abs_delta_row") or {}
        ratio_row = probe.get("max_delta_to_tolerance_ratio_row") or {}
        if not isinstance(delta_row, dict) or not isinstance(ratio_row, dict):
            fail("withheld_runtime PASS must disclose max delta and max delta/tolerance rows")
        for label, row in {"max_abs_delta_row": delta_row, "max_delta_to_tolerance_ratio_row": ratio_row}.items():
            if not row.get("case_id") or not row.get("solver"):
                fail(f"withheld_runtime {label} missing case_id/solver")
            if as_float(row.get("delta")) is None or as_float(row.get("delta_tolerance")) is None or as_float(row.get("delta_to_tolerance_ratio")) is None:
                fail(f"withheld_runtime {label} missing delta/tolerance/ratio")
        if abs(float(delta) - float(delta_row["delta"])) > 1e-18:
            fail("withheld_runtime max_abs_delta must equal max_abs_delta_row.delta")
        row_ratio = float(ratio_row["delta"]) / max(float(ratio_row["delta_tolerance"]), 1e-300)
        if abs(row_ratio - float(ratio_row["delta_to_tolerance_ratio"])) > 1e-15:
            fail("withheld_runtime ratio row must satisfy delta_to_tolerance_ratio = delta / delta_tolerance")
        if abs(float(ratio) - float(ratio_row["delta_to_tolerance_ratio"])) > 1e-18:
            fail("withheld_runtime max_delta_to_tolerance_ratio must equal the ratio row value")
        same_row = delta_row.get("case_id") == ratio_row.get("case_id") and delta_row.get("solver") == ratio_row.get("solver")
        expected_relation = "same_row" if same_row else "different_rows"
        if probe.get("max_delta_ratio_case_relation") != expected_relation:
            fail(f"withheld_runtime delta/ratio case relation must be {expected_relation}, got {probe.get('max_delta_ratio_case_relation')}")
        if probe.get("max_delta_and_ratio_same_row") is not same_row:
            fail("withheld_runtime max_delta_and_ratio_same_row must match row identity")
        if "row-wise max(delta / row_delta_tolerance)" not in str(probe.get("max_delta_to_tolerance_ratio_interpretation")):
            fail("withheld_runtime ratio interpretation must state row-wise formula")
        if probe_output.get("case_count") != len(probe_input.get("cases") or []):
            fail("withheld_runtime PASS output case count mismatch")
    else:
        if boundary.get("protected_closed_form_withheld_runtime_attached") is not False:
            fail("non-PASS probe must set protected_closed_form_withheld_runtime_attached=false")
        if "protected_closed_form_withheld_runtime_not_attached" not in blockers:
            fail("non-PASS probe must keep protected_closed_form_withheld_runtime_not_attached blocker")
        if not probe.get("blockers"):
            fail("non-PASS probe must list blockers")

    if len(bounded_control_fixture_rows) != 6:
        fail(f"control_bounded_control_fixture_contract rows must be 6, got {len(bounded_control_fixture_rows)}")
    if len(bounded_control_result_rows) != 6 * len(CONTROL_STEP_COUNTS):
        fail(f"control_bounded_control_convergence_results rows must be {6 * len(CONTROL_STEP_COUNTS)}, got {len(bounded_control_result_rows)}")
    if len(bounded_control_contact_rows) != 6:
        fail(f"control_bounded_control_contact_stability_summary rows must be 6, got {len(bounded_control_contact_rows)}")
    if len(bounded_control_summary_rows) != 1:
        fail("control_bounded_control_convergence_summary must contain exactly one row")
    if {int(r["step_count_n"]) for r in bounded_control_result_rows} != set(CONTROL_STEP_COUNTS):
        fail("control-bounded control step counts mismatch")
    if {r["bounded_control_function_G"] for r in bounded_control_fixture_rows} != {"PUBLIC_SAFE_BOUND_STEP"}:
        fail("control-bounded control fixture contract must bind PUBLIC_SAFE_BOUND_FUNCTION")
    if {r["public_system_reference"] for r in bounded_control_fixture_rows} != {"PUBLIC_SAFE_CLOSED_FORM_REFERENCE"}:
        fail("control-bounded control fixture contract must bind PUBLIC_SAFE_CLOSED_FORM_REFERENCE")
    if any(r["contract_surface_L"] != "bounded_matrix_generator" for r in bounded_control_fixture_rows):
        fail("control-bounded control control contract must be bounded_matrix_generator for this lane")
    for row in bounded_control_result_rows:
        if row["lane_id"] != "DRCET4B_BOUNDED_CONTROL_CONVERGENCE_LANE":
            fail("control-bounded control lane_id mismatch")
        if row["status"] != "PASS":
            fail(f"control-bounded control result row did not PASS: {row['case_id']} n={row['step_count_n']} status={row['status']}")
        if not as_bool(row["contact_check_pass"]):
            fail(f"control-bounded control contact check failed for {row['case_id']} n={row['step_count_n']}")
        if not as_bool(row["stability_check_pass"]):
            fail(f"control-bounded control stability check failed for {row['case_id']} n={row['step_count_n']}")
        if not as_bool(row["certificate_E_n_le_B_n"]):
            fail(f"control-bounded control E_n <= B_n failed for {row['case_id']} n={row['step_count_n']}")
        if as_float(row["S0_identity_error"]) is None or as_float(row["S0_identity_error"]) > 1e-14:
            fail(f"control-bounded control S(0)=I check failed for {row['case_id']}")
        if as_float(row["bound_utilization_E_over_B"]) is None or as_float(row["bound_utilization_E_over_B"]) > 1.0:
            fail(f"control-bounded control bound utilization above 1 for {row['case_id']} n={row['step_count_n']}")
    for row in bounded_control_contact_rows:
        if row["status"] != "PASS":
            fail(f"control-bounded control contract/stability row did not PASS: {row['case_id']}")
        observed = as_float(row["observed_convergence_rate"])
        if observed is None or not (0.75 <= observed <= 1.25):
            fail(f"control-bounded control observed convergence rate outside first-order band for {row['case_id']}: {observed}")
        if int(row["certificate_failures"]) != 0:
            fail(f"control-bounded control certificate failures present for {row['case_id']}")

    bounded_control_summary = status.get("drcet4b_control_bounded_control_convergence_lane") or {}
    if bounded_control_summary.get("lane_id") != "DRCET4B_BOUNDED_CONTROL_CONVERGENCE_LANE":
        fail("status missing DRCET4B lane summary")
    if bounded_control_summary.get("fixture_count") != 6 or bounded_control_summary.get("result_rows") != 6 * len(CONTROL_STEP_COUNTS):
        fail("DRCET4B lane summary fixture/result counts mismatch")
    if bounded_control_summary.get("step_counts") != CONTROL_STEP_COUNTS:
        fail("DRCET4B lane summary step counts mismatch")
    csv_lane_status = bounded_control_summary_rows[0].get("status")
    if csv_lane_status != bounded_control_summary.get("status"):
        fail("DRCET4B CSV summary status must match JSON status")
    bounded_control_probe = read_json(pack_dir / "bounded_control_sealed_replay_probe.json")
    bounded_control_probe_input = read_json(pack_dir / "bounded_control_sealed_replay_input.json")
    bounded_control_probe_output = read_json(pack_dir / "bounded_control_sealed_replay_output.json")
    if bounded_control_probe_input.get("schema_id") != "saa.benchmark.drcet4.control_bounded_control_withheld_runtime_input.v1":
        fail("control-bounded control withheld_runtime input schema mismatch")
    if bounded_control_probe_output.get("schema_id") != "saa.benchmark.drcet4.control_bounded_control_withheld_runtime_output.v1":
        fail("control-bounded control withheld_runtime output schema mismatch")
    if bounded_control_probe.get("input_sha256") != sha256_file(pack_dir / "bounded_control_sealed_replay_input.json"):
        fail("control-bounded control withheld_runtime input sha mismatch")
    if bounded_control_probe.get("output_sha256") != sha256_file(pack_dir / "bounded_control_sealed_replay_output.json"):
        fail("control-bounded control withheld_runtime output sha mismatch")
    bounded_control_probe_status = bounded_control_probe.get("status")
    if bounded_control_summary.get("status") == "VALIDATED_PASS_REVIEW_ONLY_BOUNDED_CONTROL_CONVERGENCE_LANE":
        if bounded_control_probe_status != "PASS_REVIEW_ONLY_NO_EGRESS_WITHHELD_RUNTIME_BOUNDED_CONTROL_LANE":
            fail("DRCET4B VALIDATED/PASS requires protected no-egress withheld_runtime PASS")
        if bounded_control_probe.get("withheld_runtime_runtime") != "docker" or bounded_control_probe.get("network_mode") != "none":
            fail("DRCET4B withheld_runtime PASS must be docker/no-egress")
        if bounded_control_probe.get("case_count") != 6 * len(CONTROL_STEP_COUNTS):
            fail("DRCET4B withheld_runtime case count mismatch")
        if bounded_control_probe.get("covered_fixture_count") != 6 or bounded_control_probe.get("total_fixture_count") != 6:
            fail("DRCET4B withheld_runtime fixture coverage mismatch")
        ratio = bounded_control_probe.get("max_delta_to_tolerance_ratio")
        if not isinstance(ratio, (int, float)) or float(ratio) > 1.0:
            fail("DRCET4B withheld_runtime delta ratio missing or above tolerance")
        if status.get("status") != EXPECTED_STATUS_WITH_CONTROL:
            fail("overall DRCET-4 status must include control-bounded control validation when DRCET4B passes")
    else:
        if bounded_control_summary.get("status") != "CONTRACT_DECLARED_WATCH":
            fail(f"unexpected DRCET4B non-pass status: {bounded_control_summary.get('status')}")
        if bounded_control_probe_status == "PASS_REVIEW_ONLY_NO_EGRESS_WITHHELD_RUNTIME_BOUNDED_CONTROL_LANE":
            fail("DRCET4B withheld_runtime PASS cannot leave lane in CONTRACT_DECLARED_WATCH")
        if "drcet4b_control_bounded_control_convergence_lane_not_validated" not in blockers:
            fail("DRCET4B watch status must keep not_validated blocker")

    production_probe = read_json(pack_dir / "withheld_runtime_bounded_control_probe.json")
    production_input = read_json(pack_dir / "withheld_runtime_bounded_control_probe_input.json")
    production_output = read_json(pack_dir / "withheld_runtime_bounded_control_probe_output.json")
    production_summary = status.get("withheld_runtime_control_bounded_control_withheld_runtime_probe") or {}
    nested_production_summary = bounded_control_summary.get("withheld_runtime_replay_probe") or {}
    if production_probe.get("status") != "WITHHELD_RUNTIME_WITHHELD_RUNTIME_NOT_ATTACHED":
        fail(f"withheld_runtime 4B probe should remain pending in public pack, got {production_probe.get('status')}")
    if production_summary.get("status") != production_probe.get("status"):
        fail("withheld_runtime 4B summary/probe status mismatch")
    if nested_production_summary.get("status") != production_probe.get("status"):
        fail("withheld_runtime 4B nested summary/probe status mismatch")
    if production_input.get("schema_id") != "saa.benchmark.drcet4b.withheld_runtime runtime_input.v1":
        fail("withheld_runtime 4B input schema mismatch")
    if production_output.get("input_sha256") != sha256_file(pack_dir / "withheld_runtime_bounded_control_probe_input.json"):
        fail("withheld_runtime 4B output input_sha mismatch")
    if boundary.get("withheld_runtime runtime_probe_attached") is not False:
        fail("withheld_runtime probe attached flag must remain false without real sealed replay runtime execution")

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
        "release_gate_proxy_rows": len(release_gate_proxy_rows),
        "release_gate_status_counts": status.get("release_gate_status_counts"),
        "convergence_order_status_counts": status.get("convergence_order_status_counts"),
        "bound_utilization_distribution": status.get("bound_utilization_distribution"),
        "a6_release_gate_metric_gate_summary": status.get("a6_release_gate_metric_gate_summary"),
        "a6_metric_step_slope_summary": status.get("a6_metric_step_slope_summary"),
        "release_gate_overhead_summary": status.get("release_gate_overhead_summary"),
        "pressure_lane_summary": status.get("pressure_lane_summary"),
        "metric_equivalence_verification": status.get("metric_equivalence_verification"),
        "article_readiness_findings": status.get("article_readiness_findings"),
        "sealed_replay_closed_form_probe": status.get("sealed_replay_closed_form_probe"),
        "drcet4b_control_bounded_control_convergence_lane": status.get("drcet4b_control_bounded_control_convergence_lane"),
        "smooth_canonical_observed_order_median": medians,
        "claim_boundary": status.get("claim_boundary"),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
