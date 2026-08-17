#!/usr/bin/env python3
"""Acceptance checker for DRCET-4D continuum spatial-refinement pack v1."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_PACK = REPO / "docs/benchmarks/drcet4d_continuum_spatial_refinement_v1_20260816"
EXPECTED_STATUS = "VALIDATED_PASS_PUBLIC_SAFE_CONTINUUM_SPATIAL_REFINEMENT_LANE_PRODUCTION_ARIN22_PENDING"
REQUIRED_FILES = {
    "DRCET4D_CONTINUUM_SPATIAL_REFINEMENT_STATUS.json",
    "README.md",
    "artifact_manifest.json",
    "continuum_spatial_fixture_contract.csv",
    "continuum_spatial_refinement_results.csv",
    "continuum_spatial_order_summary.csv",
    "spatial_refinement_loglog_error.svg",
    "production_arin22_spatial_refinement_container_input.json",
    "production_arin22_spatial_refinement_container_output.json",
    "external_blind_replay_request.json",
    "external_blind_replay_receipt.json",
}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def fnum(value: Any, field: str) -> float:
    try:
        out = float(value)
    except Exception as exc:
        fail(f"{field} is not numeric: {value!r} ({exc})")
    if not math.isfinite(out):
        fail(f"{field} is non-finite: {value!r}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Check DRCET-4D continuum spatial-refinement pack v1")
    parser.add_argument("--pack-dir", default=str(DEFAULT_PACK))
    args = parser.parse_args()
    pack = Path(args.pack_dir)
    if not pack.exists():
        fail(f"pack dir missing: {pack}")
    missing = sorted(name for name in REQUIRED_FILES if not (pack / name).exists())
    if missing:
        fail(f"required files missing: {missing}")

    status = read_json(pack / "DRCET4D_CONTINUUM_SPATIAL_REFINEMENT_STATUS.json")
    manifest = read_json(pack / "artifact_manifest.json")
    fixtures = read_csv(pack / "continuum_spatial_fixture_contract.csv")
    rows = read_csv(pack / "continuum_spatial_refinement_results.csv")
    order_rows = read_csv(pack / "continuum_spatial_order_summary.csv")
    prod_input = read_json(pack / "production_arin22_spatial_refinement_container_input.json")
    prod_output = read_json(pack / "production_arin22_spatial_refinement_container_output.json")
    replay_request = read_json(pack / "external_blind_replay_request.json")
    replay_receipt = read_json(pack / "external_blind_replay_receipt.json")

    if status.get("artifact_id") != "DRCET4D_CONTINUUM_SPATIAL_REFINEMENT_V1":
        fail("artifact_id mismatch")
    if status.get("status") != EXPECTED_STATUS:
        fail(f"unexpected status: {status.get('status')}")
    if status.get("fixture_count") != 4:
        fail("fixture_count must be 4")
    if status.get("grid_counts") != [32, 64, 128, 256]:
        fail("grid_counts mismatch")
    if len(fixtures) != 4:
        fail(f"fixture rows must be 4, got {len(fixtures)}")
    if len(rows) != 16:
        fail(f"refinement rows must be 16, got {len(rows)}")
    if len(order_rows) != 4:
        fail(f"order rows must be 4, got {len(order_rows)}")
    if status.get("silent_bound_breach_released_count") != 0:
        fail("silent bound breach released count must be 0")
    if fnum(status.get("max_bound_utilization_E_over_B"), "max E/B") >= 1.0:
        fail("max E/B must be below 1")
    if not (1.75 <= fnum(status.get("observed_spatial_order_median"), "observed order median") <= 2.25):
        fail("observed spatial order median outside second-order band")
    if "production_arin22_container_not_attached" not in status.get("blockers", []):
        fail("production container pending blocker missing")
    if "external_blind_replay_response_not_attached" not in status.get("blockers", []):
        fail("external blind replay pending blocker missing")
    for row in rows:
        if row["truth_tier"] != "R0_ANALYTIC_CONTINUUM_EIGENMODE":
            fail(f"unexpected truth tier: {row['truth_tier']}")
        if row["status"] != "PASS_SPATIAL_REFINEMENT_CERTIFICATE":
            fail(f"row status not PASS: {row['status']}")
        if row["certificate_E_h_le_B_h"].lower() != "true":
            fail("row certificate must be true")
        if row["released"].lower() != "true":
            fail("all public-safe refinement rows should release under the certificate")
        if fnum(row["bound_utilization_E_over_B"], "row E/B") >= 1.0:
            fail(f"row E/B >= 1: {row['case_id']} grid={row['interior_grid_points']}")
    for row in order_rows:
        if row["status"] != "PASS_SECOND_ORDER_SPATIAL_REFINEMENT":
            fail(f"order row status not PASS: {row['status']}")
        if not (1.75 <= fnum(row["observed_spatial_order"], "observed order") <= 2.25):
            fail(f"order outside band: {row['case_id']}")
    prod_probe = status.get("production_arin22_protected_container_probe", {})
    if prod_probe.get("status") != "PRODUCTION_ARIN22_CONTAINER_NOT_ATTACHED":
        fail(f"production probe should remain pending in public pack, got {prod_probe.get('status')}")
    if prod_input.get("schema_id") != "saa.benchmark.drcet4d.production_arin22_container_input.v1":
        fail("production input schema mismatch")
    if prod_output.get("input_sha256") != sha256_file(pack / "production_arin22_spatial_refinement_container_input.json"):
        fail("production output input_sha mismatch")
    if replay_request.get("schema_id") != "saa.benchmark.drcet4d.external_blind_replay_request.v1":
        fail("external replay request schema mismatch")
    if replay_receipt.get("status") != "PENDING_EXTERNAL_BLIND_REPLAY":
        fail("external replay receipt must be pending")
    if replay_receipt.get("request_sha256") != sha256_file(pack / "external_blind_replay_request.json"):
        fail("external replay request sha mismatch")

    listed = {item["path"]: item for item in manifest.get("files", [])}
    expected_listed = REQUIRED_FILES - {"artifact_manifest.json"}
    if set(listed) != expected_listed:
        fail(f"manifest file set mismatch missing={sorted(expected_listed-set(listed))} extra={sorted(set(listed)-expected_listed)}")
    for name, item in listed.items():
        path = pack / name
        if item.get("sha256") != sha256_file(path):
            fail(f"manifest sha mismatch: {name}")
        if int(item.get("byte_length", -1)) != path.stat().st_size:
            fail(f"manifest byte_length mismatch: {name}")
    print(json.dumps({
        "status": "PASS",
        "pack_status": status.get("status"),
        "status_sha256": sha256_file(pack / "DRCET4D_CONTINUUM_SPATIAL_REFINEMENT_STATUS.json"),
        "manifest_sha256": sha256_file(pack / "artifact_manifest.json"),
        "rows": len(rows),
        "observed_spatial_order_median": status.get("observed_spatial_order_median"),
        "production_probe": prod_probe.get("status"),
        "external_blind_replay": replay_receipt.get("status"),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
