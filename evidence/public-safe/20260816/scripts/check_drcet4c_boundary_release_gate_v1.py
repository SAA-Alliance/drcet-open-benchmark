#!/usr/bin/env python3
"""Acceptance checker for DRCET-4C boundary release gate pack v1."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_PACK = REPO / "docs/benchmarks/drcet4c_boundary_release_gate_v1_20260816"
EXPECTED_STATUS = "VALIDATED_PASS_WITH_ORDER_FLOOR_GATE_AND_QUADRATURE_WATCH_BOUNDARY_RELEASE_LANE_PRODUCTION_ARIN22_PENDING"
SAFE_FAIL_CLOSED_OUTSIDE_BOUNDARY_TRANSFORM_HALF_PLANE = "SAFE_FAIL_CLOSED_OUTSIDE_CERTIFIED_BOUNDARY_TRANSFORM_HALF_PLANE"
SAFE_FAIL_CLOSED_NON_CONVERGENT = "SAFE_FAIL_CLOSED_NON_CONVERGENT"
LAMBDA_GATE_INSIDE = "INSIDE_CERTIFIED_BOUNDARY_TRANSFORM_HALF_PLANE"
REQUIRED_FILES = {
    "DRCET4C_BOUNDARY_RELEASE_GATE_STATUS.json",
    "README.md",
    "artifact_manifest.json",
    "contract_function_policy.json",
    "boundary_half_plane_policy.json",
    "boundary_transform_fixture_contract.csv",
    "boundary_transform_lambda_sweep_results.csv",
    "boundary_transform_tangency_product_summary.csv",
    "boundary_transform_convergence_summary.csv",
    "boundary_transform_protected_container_input.json",
    "boundary_transform_protected_container_output.json",
    "production_arin22_boundary_transform_container_input.json",
    "production_arin22_boundary_transform_container_output.json",
    "production_arin22_boundary_transform_container_probe.json",
    "external_blind_replay_request.json",
    "external_blind_replay_receipt.json",
    "boundary_transform_loglog_convergence.svg",
    "boundary_transform_lambda_gate_sweep.svg",
}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def fnum(value: Any, field: str) -> float:
    try:
        out = float(value)
    except Exception as exc:
        fail(f"{field} is not numeric: {value!r} ({exc})")
    if not math.isfinite(out):
        fail(f"{field} is non-finite: {value!r}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Check DRCET-4C boundary release gate pack v1")
    parser.add_argument("--pack-dir", default=str(DEFAULT_PACK))
    args = parser.parse_args()
    pack = Path(args.pack_dir)
    if not pack.exists():
        fail(f"pack dir missing: {pack}")
    missing = sorted(name for name in REQUIRED_FILES if not (pack / name).exists())
    if missing:
        fail(f"required files missing: {missing}")

    status = read_json(pack / "DRCET4C_BOUNDARY_RELEASE_GATE_STATUS.json")
    manifest = read_json(pack / "artifact_manifest.json")
    fixture_rows = read_csv(pack / "boundary_transform_fixture_contract.csv")
    lambda_rows = read_csv(pack / "boundary_transform_lambda_sweep_results.csv")
    tangent_rows = read_csv(pack / "boundary_transform_tangency_product_summary.csv")
    convergence_rows = read_csv(pack / "boundary_transform_convergence_summary.csv")
    container_input = read_json(pack / "boundary_transform_protected_container_input.json")
    container_output = read_json(pack / "boundary_transform_protected_container_output.json")
    production_input = read_json(pack / "production_arin22_boundary_transform_container_input.json")
    production_output = read_json(pack / "production_arin22_boundary_transform_container_output.json")
    production_probe = read_json(pack / "production_arin22_boundary_transform_container_probe.json")
    replay_request = read_json(pack / "external_blind_replay_request.json")
    replay_receipt = read_json(pack / "external_blind_replay_receipt.json")

    if status.get("artifact_id") != "DRCET4C_BOUNDARY_RELEASE_BOUNDARY_TRANSFORM_V1":
        fail("artifact_id mismatch")
    if status.get("status") != EXPECTED_STATUS:
        fail(f"unexpected status: {status.get('status')}")
    if status.get("contract_function_policy", {}).get("not_the_object") != "I+tL first-order product proxy from DRCET-4B":
        fail("object mismatch disclosure missing")
    if status.get("contract_function_policy", {}).get("production_kernel_exercised") is not False:
        fail("production kernel boundary must remain false")
    if "production_ARIN22_kernel_validated_through_protected_route" not in status.get("must_not_claim", []):
        fail("must_not_claim production boundary missing")
    if "external_blind_replay_request_published_not_completed" not in status.get("blockers", []):
        fail("external blind replay pending blocker missing")
    if status.get("silent_release_outside_certified_half_plane_count") != 0:
        fail("silent release outside certified half-plane detected")
    if status.get("silent_release_outside_certified_boundary_transform_half_plane_count") != 0:
        fail("silent release outside certified boundary_transform half-plane detected")
    fail_closed_count = int(status.get("fail_closed_outside_certified_boundary_transform_half_plane_rows", -1))
    if fail_closed_count <= 0:
        fail("certified boundary_transform half-plane must have fail-closed rows")
    if status.get("exact_boundary_transform_diagnostic_available_below_boundary_rows") != fail_closed_count:
        fail("below-boundary diagnostic exact boundary_transform readback must match fail-closed rows in this bounded fixture")
    if fnum(status.get("conservative_theorem_domain_block_rate"), "conservative_theorem_domain_block_rate") != 1.0:
        fail("conservative theorem-domain block rate must be 1.0 in this fixture")
    if status.get("error_budget_policy", {}).get("B_total") != "B_product + B_quadrature + B_tail + B_reference + B_floating":
        fail("error budget policy missing full B_total formula")
    lambda_status_counts = status.get("lambda_status_counts", {})
    if not lambda_status_counts or sum(int(v) for v in lambda_status_counts.values()) != int(status.get("lambda_sweep_rows", -1)):
        fail(f"lambda status counts do not sum to lambda_sweep_rows: {lambda_status_counts}")
    if int(lambda_status_counts.get(SAFE_FAIL_CLOSED_OUTSIDE_BOUNDARY_TRANSFORM_HALF_PLANE, 0)) <= 0:
        fail("lambda status counts must include fail-closed outside half-plane rows")
    if int(lambda_status_counts.get("PASS_RECOMPRESSED_NEAR_BOUNDARY", 0)) <= 0:
        fail("lambda status counts must include near-boundary recompressed rows")
    if int(lambda_status_counts.get("PASS_BOUNDARY_TRANSFORM_CONVERGENCE", 0)) <= 0:
        fail("lambda status counts must include converged rows")
    convergence_status_counts = status.get("boundary_transform_convergence_status_counts", {})
    if not convergence_status_counts or sum(int(v) for v in convergence_status_counts.values()) != int(status.get("boundary_transform_convergence_rows", -1)):
        fail("boundary_transform convergence status counts do not sum to convergence rows")
    if int(convergence_status_counts.get("WATCH_BOUNDARY_TRANSFORM_ORDER", 0)) > 0 and status.get("watch_items") != ["near_boundary_quadrature_dominated_boundary_transform_order_row"]:
        fail("quadrature watch item must be explicit when convergence watch rows exist")
    if fnum(status.get("observed_boundary_transform_order_median"), "observed_boundary_transform_order_median") < 1.8:
        fail("median boundary_transform order below second-order evidence band")
    if fnum(status.get("max_released_E_over_B"), "max_released_E_over_B") >= 1.0:
        fail("released E/B exceeds declared bound")
    order_gate = status.get("boundary_transform_order_release_gate", {})
    if order_gate.get("status") != "PASS_NONCONVERGENT_ROWS_FAIL_CLOSED":
        fail(f"order release gate did not pass: {order_gate.get('status')}")
    if fnum(order_gate.get("order_floor"), "order gate floor") < 1.0:
        fail("order gate floor must be explicit and nontrivial")
    nonconvergent_fail_closed = int(status.get("fail_closed_nonconvergent_rows", -1))
    if nonconvergent_fail_closed <= 0:
        fail("nonconvergent rows must fail closed")
    if nonconvergent_fail_closed != int(order_gate.get("transitioned_released_to_fail_closed_rows", -2)):
        fail("nonconvergent fail-closed count must match order gate transitions")
    if int(status.get("silent_release_nonconvergent_count", -1)) != 0:
        fail("nonconvergent rows were silently released")

    if len(fixture_rows) != 4:
        fail(f"fixture rows must be 4, got {len(fixture_rows)}")
    expected_lambda_rows = len(fixture_rows) * len(status.get("lambda_sweep_deltas", [])) * len(status.get("step_counts", []))
    if len(lambda_rows) != expected_lambda_rows:
        fail(f"lambda rows must match fixture*deltas*steps ({expected_lambda_rows}), got {len(lambda_rows)}")
    if len(tangent_rows) != 4:
        fail(f"tangent rows must be 4, got {len(tangent_rows)}")
    inside_deltas = sorted({float(r["delta_scaled"]) for r in lambda_rows if r["lambda_gate_status"] == LAMBDA_GATE_INSIDE})
    if len(convergence_rows) != len(fixture_rows) * len(inside_deltas):
        fail(f"convergence rows must match fixture*inside_deltas, got {len(convergence_rows)}")
    if any(r["foundation_function_G"] == "I+tL" for r in fixture_rows):
        fail("DRCET-4C must not use the DRCET-4B I+tL object")
    if any(r["declared_product_order"] != "2" for r in fixture_rows):
        fail("declared product order must be 2")
    if any(str(r["abc_present"]).lower() != "true" for r in fixture_rows):
        fail("all fixtures must carry a/b/c operator evidence")
    for row in fixture_rows:
        local_order = fnum(row["local_defect_order_estimate"], f"{row['case_id']} local order")
        global_order = fnum(row["global_product_order_estimate"], f"{row['case_id']} global order")
        if not (2.5 <= local_order <= 3.5):
            fail(f"local defect order outside O(h^3) band for {row['case_id']}: {local_order}")
        if not (1.6 <= global_order <= 2.4):
            fail(f"global product order outside O(n^-2) band for {row['case_id']}: {global_order}")
    if any(r["status"] != "PASS_SECOND_ORDER_PRODUCT" for r in tangent_rows):
        fail("all tangency/product rows must pass")

    for row in lambda_rows:
        inside = row["lambda_gate_status"] == LAMBDA_GATE_INSIDE
        released = row["released"].lower() == "true"
        delta_scaled = fnum(row["delta_scaled"], "delta_scaled")
        if inside:
            if row["certificate_E_le_B"].lower() != "true":
                fail(f"inside half-plane E<=B failed: {row['case_id']} n={row['step_count_n']}")
            if fnum(row["bound_utilization_E_over_B"], "E/B") >= 1.0:
                fail(f"inside half-plane E/B >= 1: {row['case_id']} n={row['step_count_n']}")
            ref_norm = fnum(row.get("reference_boundary_transform_norm"), "reference_boundary_transform_norm")
            rel_err = fnum(row.get("E_over_reference_boundary_transform_norm"), "E_over_reference_boundary_transform_norm")
            if ref_norm <= 0 or rel_err < 0:
                fail("relative error readback must be present for inside half-plane rows")
            gate_status = row.get("convergence_release_gate_status")
            if gate_status == SAFE_FAIL_CLOSED_NON_CONVERGENT:
                if released:
                    fail(f"nonconvergent inside half-plane row released: {row['case_id']} n={row['step_count_n']}")
                if row["status"] != SAFE_FAIL_CLOSED_NON_CONVERGENT:
                    fail(f"nonconvergent gate status mismatch: {row['status']}")
            else:
                if not released:
                    fail(f"inside half-plane convergent row not released: {row['case_id']} n={row['step_count_n']}")
                if not row["status"].startswith("PASS"):
                    fail(f"inside half-plane convergent row status not PASS: {row['status']}")
            for field in ["B_product", "B_quadrature", "B_tail", "B_reference", "B_floating"]:
                if fnum(row[field], field) < 0:
                    fail(f"{field} must be non-negative")
            if row.get("B_tail_status") != "NOT_APPLICABLE_FOR_GAUSS_LAGUERRE_INFINITE_INTERVAL":
                fail(f"B_tail_status must explain Gauss-Laguerre no finite tail truncation: {row.get('B_tail_status')}")
        else:
            if released:
                fail(f"outside half-plane row released: {row['case_id']} n={row['step_count_n']}")
            if row["status"] != SAFE_FAIL_CLOSED_OUTSIDE_BOUNDARY_TRANSFORM_HALF_PLANE:
                fail(f"outside half-plane row did not fail closed: {row['status']}")
            if delta_scaled == 0.0 and fnum(row["lambda_minus_omega"], "lambda_minus_omega") > 1e-14:
                fail("zero delta row must not be inside the certified half-plane")
            if row.get("stability_probe_pass") != "NOT_APPLICABLE_OUTSIDE_CERTIFIED_BOUNDARY_TRANSFORM_HALF_PLANE":
                fail("outside half-plane stability probe must be marked NOT_APPLICABLE")

    lambda_grid = status.get("lambda_grid_readback", {})
    if lambda_grid.get("counts_are_grid_coverage_not_frequency") is not True:
        fail("lambda grid counts must be marked as grid coverage, not empirical frequency")
    if fnum(lambda_grid.get("min_positive_lambda_minus_omega"), "min_positive_lambda_minus_omega") <= 0:
        fail("dense lambda grid must include positive inside rows")
    if fnum(lambda_grid.get("max_negative_lambda_minus_omega"), "max_negative_lambda_minus_omega") >= 0:
        fail("dense lambda grid must include negative outside rows")
    if int(lambda_grid.get("zero_delta_released_rows", -1)) != 0:
        fail("zero delta rows must not release")

    certificate = status.get("certificate_envelope_summary", {})
    if certificate.get("status") != "CONSERVATIVE_SAFETY_ENVELOPE_NOT_TIGHT_ERROR_ESTIMATE":
        fail(f"certificate envelope status mismatch: {certificate.get('status')}")
    if certificate.get("all_released_E_le_B") is not True:
        fail("certificate envelope must verify all released E<=B")
    if fnum(certificate.get("max_E_over_B"), "certificate max E/B") >= 1.0:
        fail("certificate max E/B must be below 1")
    if fnum(certificate.get("B_product_dominates_released_share"), "B_product dominance share") <= 0.5:
        fail("certificate summary should expose B_product dominance when present")

    bootstrap = status.get("boundary_transform_order_bootstrap_ci95", {})
    if bootstrap.get("status") != "PASS_REPORTED_WITH_QUADRATURE_WATCH":
        fail(f"bootstrap status mismatch: {bootstrap.get('status')}")
    if int(bootstrap.get("bootstrap_replicates", 0)) < 1000:
        fail("bootstrap replicates must be >= 1000")
    if fnum(bootstrap.get("ci95_low"), "bootstrap ci95_low") > fnum(bootstrap.get("ci95_high"), "bootstrap ci95_high"):
        fail("bootstrap CI is inverted")

    probe = status.get("protected_no_egress_container", {})
    if probe.get("status") != "PASS_REVIEW_ONLY_NO_EGRESS_CONTAINER_FOUNDATION_BOUNDARY_TRANSFORM_LANE":
        fail(f"container status mismatch: {probe.get('status')}")
    if probe.get("network_mode") != "none":
        fail("container network_mode must be none")
    if probe.get("case_count") != len([r for r in lambda_rows if r["lambda_gate_status"] == LAMBDA_GATE_INSIDE]):
        fail("container case count must match inside-half-plane rows")
    if probe.get("expected_case_count") != probe.get("case_count"):
        fail("container expected case count must match actual case count")
    if fnum(probe.get("max_delta_to_tolerance_ratio"), "container max delta/tolerance") >= 1.0:
        fail("container delta/tolerance ratio exceeds bound")
    if container_input.get("schema_id") != "saa.benchmark.drcet4c.boundary_transform_container_input.v1":
        fail("container input schema mismatch")
    if container_output.get("schema_id") != "saa.benchmark.drcet4c.boundary_transform_container_output.v1":
        fail("container output schema mismatch")
    if container_output.get("input_sha256") != sha256_file(pack / "boundary_transform_protected_container_input.json"):
        fail("container output input_sha256 mismatch")
    for field in ["lane_id", "contract_version", "contract_sha256", "actual_G_implementation_sha256", "composition_trace_sha256", "composition_weights_hash"]:
        if not container_input.get(field):
            fail(f"container input runtime identity missing {field}")
        if container_output.get(field) != container_input.get(field):
            fail(f"container output runtime identity mismatch for {field}")
    if probe.get("runtime_identity_mismatches"):
        fail(f"container probe runtime identity mismatches: {probe.get('runtime_identity_mismatches')}")
    prod_summary = status.get("production_arin22_protected_container_probe", {})
    if prod_summary.get("status") != "PRODUCTION_ARIN22_CONTAINER_NOT_ATTACHED":
        fail(f"production ARIN22 probe should remain pending in public pack, got {prod_summary.get('status')}")
    if production_probe.get("status") != prod_summary.get("status"):
        fail("production probe file/status summary mismatch")
    if production_input.get("schema_id") != "saa.benchmark.drcet4c.production_arin22_container_input.v1":
        fail("production ARIN22 input schema mismatch")
    if production_output.get("input_sha256") != sha256_file(pack / "production_arin22_boundary_transform_container_input.json"):
        fail("production ARIN22 output input_sha mismatch")
    if replay_request.get("schema_id") != "saa.benchmark.drcet4c.external_blind_replay_request.v1":
        fail("external blind replay request schema mismatch")
    if replay_receipt.get("status") != "PENDING_EXTERNAL_BLIND_REPLAY":
        fail("external blind replay receipt must be pending")
    if replay_receipt.get("request_sha256") != sha256_file(pack / "external_blind_replay_request.json"):
        fail("external blind replay request sha mismatch")
    cross_rule = status.get("container_cross_quadrature_rule", {})
    if cross_rule.get("python_primary_quadrature_rule") == cross_rule.get("container_quadrature_rule"):
        fail("container cross-rule readback must not claim identical quadrature order")

    listed = {item["path"] for item in manifest.get("files", [])}
    expected_listed = REQUIRED_FILES - {"artifact_manifest.json"}
    missing_manifest = sorted(expected_listed - listed)
    if missing_manifest:
        fail(f"manifest missing files: {missing_manifest}")
    print(json.dumps({
        "status": "PASS",
        "pack_status": status.get("status"),
        "status_sha256": sha256_file(pack / "DRCET4C_BOUNDARY_RELEASE_GATE_STATUS.json"),
        "artifact_manifest_sha256": sha256_file(pack / "artifact_manifest.json"),
        "lambda_status_counts": status.get("lambda_status_counts"),
        "fail_closed_nonconvergent_rows": status.get("fail_closed_nonconvergent_rows"),
        "released_rows": status.get("released_rows"),
        "container_status": probe.get("status"),
        "watch_items": status.get("watch_items"),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
