#!/usr/bin/env python3
"""Validate the H100 GPU measured Pareto V2 pack."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

EXPECTED_STATUS = "GPU_H100_MEASURED_CPU_REFERENCE_ATTACHED_CROSSOVER_REVIEW_ONLY"
EXPECTED_TARGETS = 320


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def load_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pack_dir")
    args = ap.parse_args()
    root = Path(args.pack_dir)
    required = [
        "ACCURACY_COST_ENERGY_PARETO_V2_GPU_H100_STATUS.json",
        "artifact_manifest.json",
        "hardware_probe.json",
        "measured_results_gpu_h100.csv",
        "gpu_internal_frontier.csv",
        "telemetry_gap_report.json",
        "README.md",
    ]
    for name in required:
        if not (root / name).is_file():
            fail(f"missing {name}")
    status = json.loads((root / "ACCURACY_COST_ENERGY_PARETO_V2_GPU_H100_STATUS.json").read_text())
    manifest = json.loads((root / "artifact_manifest.json").read_text())
    rows = load_csv(root / "measured_results_gpu_h100.csv")
    frontier = load_csv(root / "gpu_internal_frontier.csv")
    if status.get("status") != EXPECTED_STATUS:
        fail(f"unexpected status {status.get('status')}")
    if status.get("target_count") != EXPECTED_TARGETS:
        fail("target_count must be 320")
    if status.get("frontier_acceptance_gate", {}).get("crossover_claim_allowed") is not False:
        fail("crossover claim must stay false")
    expected_rows = EXPECTED_TARGETS * len(status.get("budgets_paths") or []) * int(status.get("repeats") or 0) * len(status.get("methods") or [])
    if len(rows) != expected_rows:
        fail(f"measured row count expected {expected_rows}, got {len(rows)}")
    if len(frontier) != EXPECTED_TARGETS:
        fail(f"frontier rows expected 320, got {len(frontier)}")
    for row in rows:
        if row.get("device_class") != "NVIDIA_GPU_H100_PCIE":
            fail("non-H100 row found")
        if row.get("cloud_cost_status") != "WITHHELD_CLOUD_RATE_NOT_BOUND":
            fail("cloud dollars must be withheld")
        if row.get("nvml_energy_status") != "MEASURED_NVML_POWER_INTEGRATED":
            fail("NVML energy must be measured")
        for key in ["wall_ms_per_iter", "gpu_energy_joules_per_iter", "gpu_peak_memory_mib", "abs_error", "error_envelope"]:
            val = float(row[key])
            if val < 0:
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
        "measured_rows": len(rows),
        "frontier_rows": len(frontier),
        "status_sha256": sha256_file(root / "ACCURACY_COST_ENERGY_PARETO_V2_GPU_H100_STATUS.json"),
        "manifest_sha256": sha256_file(root / "artifact_manifest.json"),
        "crossover_claim_allowed": status["frontier_acceptance_gate"]["crossover_claim_allowed"],
        "gpu_joules": status["telemetry_status"]["gpu_joules"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
