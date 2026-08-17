#!/usr/bin/env python3
"""Validate the CPU Contabo fixed-window Pareto V2 evidence pack."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

EXPECTED_STATUS = "CPU_CONTABO_WINDOWED_MEASURED_GPU_COMPARABLE_UNITS"
EXPECTED_TARGETS = 320


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> int:
    ap = argparse.ArgumentParser(description="Check CPU Contabo fixed-window Pareto V2 pack")
    ap.add_argument("pack_dir")
    args = ap.parse_args()
    root = Path(args.pack_dir)
    required = [
        "ACCURACY_COST_ENERGY_PARETO_V2_CPU_CONTABO_WINDOWED_STATUS.json",
        "artifact_manifest.json",
        "hardware_probe.json",
        "reference_results_cpu.csv",
        "measured_results_cpu_windowed.csv",
        "cpu_windowed_internal_frontier.csv",
        "telemetry_gap_report.json",
        "README.md",
    ]
    for name in required:
        if not (root / name).is_file():
            fail(f"missing required artifact {name}")
    status = load_json(root / "ACCURACY_COST_ENERGY_PARETO_V2_CPU_CONTABO_WINDOWED_STATUS.json")
    manifest = load_json(root / "artifact_manifest.json")
    rows = load_csv(root / "measured_results_cpu_windowed.csv")
    refs = load_csv(root / "reference_results_cpu.csv")
    frontier = load_csv(root / "cpu_windowed_internal_frontier.csv")
    if status.get("status") != EXPECTED_STATUS:
        fail(f"unexpected status {status.get('status')}")
    if int(status.get("target_count", 0)) != EXPECTED_TARGETS:
        fail("target_count must be 320")
    if len(refs) != EXPECTED_TARGETS:
        fail(f"reference rows expected 320, got {len(refs)}")
    methods = status.get("methods") or []
    budgets = status.get("budgets_paths") or []
    repeats = int(status.get("repeats", 0))
    expected_rows = EXPECTED_TARGETS * len(methods) * len(budgets) * repeats
    if len(rows) != expected_rows:
        fail(f"measured row count expected {expected_rows}, got {len(rows)}")
    if len(frontier) != EXPECTED_TARGETS:
        fail(f"frontier rows expected 320, got {len(frontier)}")
    gate = status.get("frontier_acceptance_gate", {})
    if gate.get("cpu_windowed_units_present") is not True:
        fail("cpu_windowed_units_present must be true")
    if gate.get("crossover_claim_allowed") is not False:
        fail("crossover claim must remain false in CPU-only windowed pack")
    for row in rows:
        if row.get("device_class") != "CPU_CONTABO_WINDOWED":
            fail("non-windowed CPU row found")
        for key in ["wall_ms_total_window", "wall_ms_per_iter", "process_cpu_seconds_total_window", "process_cpu_seconds_per_iter", "iterations_per_window", "abs_error", "error_envelope"]:
            try:
                value = float(row[key])
            except Exception as exc:
                fail(f"non-numeric {key}: {exc}")
            if value <= 0 and key not in {"abs_error"}:
                fail(f"non-positive {key}")
        if float(row["wall_ms_total_window"]) < float(row["wall_ms_per_iter"]):
            fail("window total must be >= per-iteration wall time")
    mf = {f["path"]: f for f in manifest.get("files", [])}
    for name in required:
        if name == "artifact_manifest.json":
            continue
        if name not in mf:
            fail(f"manifest missing {name}")
        if mf[name].get("sha256") != sha256_file(root / name):
            fail(f"manifest sha mismatch for {name}")
    print(json.dumps({
        "status": status["status"],
        "status_sha256": sha256_file(root / "ACCURACY_COST_ENERGY_PARETO_V2_CPU_CONTABO_WINDOWED_STATUS.json"),
        "manifest_sha256": sha256_file(root / "artifact_manifest.json"),
        "measured_rows": len(rows),
        "frontier_rows": len(frontier),
        "cpu_joules": status.get("telemetry_status", {}).get("cpu_joules"),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
