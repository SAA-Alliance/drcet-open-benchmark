#!/usr/bin/env python3
"""Validate the CPU Contabo fixed-iteration Pareto V2 evidence pack."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

EXPECTED_STATUS = "CPU_CONTABO_FIXED_ITERATION_MEASURED_GPU_COMPARABLE_UNITS"
EXPECTED_TARGETS = 320


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def load_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pack_dir")
    args = ap.parse_args()
    root = Path(args.pack_dir)
    required = [
        "ACCURACY_COST_ENERGY_PARETO_V2_CPU_CONTABO_FIXED_ITER_STATUS.json",
        "artifact_manifest.json",
        "hardware_probe.json",
        "reference_results_cpu.csv",
        "measured_results_cpu_fixed_iter.csv",
        "cpu_fixed_iter_internal_frontier.csv",
        "telemetry_gap_report.json",
        "README.md",
    ]
    for name in required:
        if not (root / name).is_file():
            fail(f"missing {name}")
    status = json.loads((root / "ACCURACY_COST_ENERGY_PARETO_V2_CPU_CONTABO_FIXED_ITER_STATUS.json").read_text())
    manifest = json.loads((root / "artifact_manifest.json").read_text())
    rows = load_csv(root / "measured_results_cpu_fixed_iter.csv")
    refs = load_csv(root / "reference_results_cpu.csv")
    frontier = load_csv(root / "cpu_fixed_iter_internal_frontier.csv")
    if status.get("status") != EXPECTED_STATUS:
        fail(f"unexpected status {status.get('status')}")
    if int(status.get("target_count", 0)) != EXPECTED_TARGETS:
        fail("target_count must be 320")
    if len(refs) != EXPECTED_TARGETS:
        fail(f"reference rows expected 320, got {len(refs)}")
    expected_rows = EXPECTED_TARGETS * len(status.get("methods") or []) * len(status.get("budgets_paths") or []) * int(status.get("repeats") or 0)
    if len(rows) != expected_rows:
        fail(f"measured rows expected {expected_rows}, got {len(rows)}")
    if len(frontier) != EXPECTED_TARGETS:
        fail(f"frontier rows expected 320, got {len(frontier)}")
    fixed_iterations = int(status.get("fixed_iterations", 0))
    if fixed_iterations <= 0:
        fail("fixed_iterations must be positive")
    if status.get("frontier_acceptance_gate", {}).get("crossover_claim_allowed") is not False:
        fail("crossover claim must stay false")
    for row in rows:
        if row.get("device_class") != "CPU_CONTABO_FIXED_ITERATION":
            fail("non-fixed CPU row found")
        if int(float(row["iterations_per_window"])) != fixed_iterations:
            fail("iterations_per_window must equal fixed_iterations")
        for key in ["wall_ms_total_window", "wall_ms_per_iter", "process_cpu_seconds_total_window", "process_cpu_seconds_per_iter", "abs_error", "error_envelope"]:
            value = float(row[key])
            if value < 0:
                fail(f"negative {key}")
    mf = {f["path"]: f for f in manifest.get("files", [])}
    for name in required:
        if name == "artifact_manifest.json":
            continue
        if name not in mf:
            fail(f"manifest missing {name}")
        if mf[name]["sha256"] != sha256_file(root / name):
            fail(f"manifest sha mismatch for {name}")
    print(json.dumps({
        "status": status["status"],
        "status_sha256": sha256_file(root / "ACCURACY_COST_ENERGY_PARETO_V2_CPU_CONTABO_FIXED_ITER_STATUS.json"),
        "manifest_sha256": sha256_file(root / "artifact_manifest.json"),
        "measured_rows": len(rows),
        "frontier_rows": len(frontier),
        "fixed_iterations": fixed_iterations,
        "within_internal_envelope_rows": status.get("within_internal_envelope_rows"),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
