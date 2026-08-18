#!/usr/bin/env python3
"""Validate the CPU-only Contabo measured Pareto V2 evidence pack."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

EXPECTED_STATUS = "CPU_ONLY_MEASURED_GPU_PENDING"
EXPECTED_TARGETS = 320


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def check_pack(root: Path) -> Dict[str, Any]:
    required = [
        "ACCURACY_COST_ENERGY_PARETO_V2_CPU_CONTABO_STATUS.json",
        "artifact_manifest.json",
        "hardware_probe.json",
        "reference_results_cpu.csv",
        "measured_results_cpu.csv",
        "cpu_internal_frontier.csv",
        "telemetry_gap_report.json",
        "README.md",
    ]
    for name in required:
        if not (root / name).is_file():
            fail(f"missing required artifact {name}")
    status = load_json(root / "ACCURACY_COST_ENERGY_PARETO_V2_CPU_CONTABO_STATUS.json")
    manifest = load_json(root / "artifact_manifest.json")
    hardware = load_json(root / "hardware_probe.json")
    measured = load_csv(root / "measured_results_cpu.csv")
    reference = load_csv(root / "reference_results_cpu.csv")
    frontier = load_csv(root / "cpu_internal_frontier.csv")

    if status.get("status") != EXPECTED_STATUS:
        fail(f"unexpected status {status.get('status')}")
    if int(status.get("target_count", 0)) != EXPECTED_TARGETS:
        fail("target_count must be 320")
    if status.get("frontier_acceptance_gate", {}).get("crossover_claim_allowed") is not False:
        fail("crossover_claim_allowed must remain false for CPU-only pack")
    if status.get("frontier_acceptance_gate", {}).get("gpu_rows_present") is not False:
        fail("gpu_rows_present must be false for CPU-only pack")
    if not measured:
        fail("measured_results_cpu.csv is empty")
    if len(reference) != EXPECTED_TARGETS:
        fail(f"reference rows expected 320, got {len(reference)}")
    budgets = status.get("budgets_paths") or []
    repeats = int(status.get("repeats", 0))
    methods = status.get("methods") or []
    expected_measured = EXPECTED_TARGETS * len(budgets) * repeats * len(methods)
    if len(measured) != expected_measured:
        fail(f"measured row count expected {expected_measured}, got {len(measured)}")
    if len(frontier) != EXPECTED_TARGETS:
        fail(f"frontier rows expected 320, got {len(frontier)}")
    for row in measured:
        if row.get("device_class") != "CPU":
            fail("non-CPU row found in CPU-only pack")
        if row.get("gpu_status") != "PENDING_GPU_NODE":
            fail("GPU status must remain pending")
        if row.get("cloud_cost_status") != "WITHHELD_CLOUD_RATE_NOT_BOUND":
            fail("cloud cost must remain withheld without rate profile")
        # Numeric sanity.
        for key in ["wall_ms", "process_cpu_seconds", "cpu_peak_rss_mb", "abs_error", "error_envelope"]:
            try:
                val = float(row[key])
            except Exception as exc:
                fail(f"non-numeric {key}: {exc}")
            if val < 0:
                fail(f"negative {key}")
    if hardware.get("rapl", {}).get("available") is False:
        if status.get("telemetry_status", {}).get("cpu_joules") != "WITHHELD_RAPL_NOT_AVAILABLE":
            fail("RAPL absent but cpu_joules not withheld")
    manifest_files = {f["path"]: f for f in manifest.get("files", [])}
    for name in required:
        if name == "artifact_manifest.json":
            continue
        if name not in manifest_files:
            fail(f"manifest missing {name}")
        actual = sha256_file(root / name)
        if manifest_files[name].get("sha256") != actual:
            fail(f"manifest sha mismatch for {name}")
    return {
        "status": status["status"],
        "measured_rows": len(measured),
        "reference_rows": len(reference),
        "frontier_rows": len(frontier),
        "status_sha256": sha256_file(root / "ACCURACY_COST_ENERGY_PARETO_V2_CPU_CONTABO_STATUS.json"),
        "manifest_sha256": sha256_file(root / "artifact_manifest.json"),
        "cpu_joules": status.get("telemetry_status", {}).get("cpu_joules"),
        "crossover_claim_allowed": status.get("frontier_acceptance_gate", {}).get("crossover_claim_allowed"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check CPU Contabo measured Pareto V2 pack")
    parser.add_argument("pack_dir")
    args = parser.parse_args()
    result = check_pack(Path(args.pack_dir))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
