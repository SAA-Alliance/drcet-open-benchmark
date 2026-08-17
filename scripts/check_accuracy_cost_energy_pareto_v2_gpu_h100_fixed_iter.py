#!/usr/bin/env python3
"""Validate the H100 GPU fixed-iteration Pareto V2 pack."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

EXPECTED_STATUS = "GPU_H100_FIXED_ITERATION_MEASURED_CPU_REFERENCE_ATTACHED_CROSSOVER_REVIEW_ONLY"
EXPECTED_TARGETS = 320
MIN_NVML_ENERGY_SAMPLE_COUNT = 20


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
        "ACCURACY_COST_ENERGY_PARETO_V2_GPU_H100_FIXED_ITER_STATUS.json",
        "artifact_manifest.json",
        "hardware_probe.json",
        "measured_results_gpu_h100_fixed_iter.csv",
        "gpu_fixed_iter_internal_frontier.csv",
        "telemetry_gap_report.json",
        "README.md",
    ]
    for name in required:
        if not (root / name).is_file():
            fail(f"missing {name}")
    status = json.loads((root / "ACCURACY_COST_ENERGY_PARETO_V2_GPU_H100_FIXED_ITER_STATUS.json").read_text())
    manifest = json.loads((root / "artifact_manifest.json").read_text())
    rows = load_csv(root / "measured_results_gpu_h100_fixed_iter.csv")
    frontier = load_csv(root / "gpu_fixed_iter_internal_frontier.csv")
    if status.get("status") != EXPECTED_STATUS:
        fail(f"unexpected status {status.get('status')}")
    if int(status.get("target_count", 0)) != EXPECTED_TARGETS:
        fail("target_count must be 320")
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
    energy_gate = status.get("nvml_energy_quality_gate", {})
    if int(energy_gate.get("minimum_sample_count_required") or 0) != MIN_NVML_ENERGY_SAMPLE_COUNT:
        fail("missing or wrong NVML energy sample-count gate")
    if int(energy_gate.get("sample_count_median") or 0) < MIN_NVML_ENERGY_SAMPLE_COUNT:
        if status.get("telemetry_status", {}).get("gpu_joules") != "WITHHELD_INSUFFICIENT_NVML_SAMPLE_COUNT_FIXED_ITERATION":
            fail("GPU joules must be withheld when median NVML sample count is below gate")
        if status.get("telemetry_status", {}).get("gpu_energy_release_quality_sufficient") is not False:
            fail("GPU energy release quality must be false when sample-count gate fails")
    accepted_energy_rows = 0
    withheld_energy_rows = 0
    for row in rows:
        if row.get("device_class") != "NVIDIA_GPU_H100_PCIE_FIXED_ITERATION":
            fail("non-H100 fixed-iteration row found")
        if int(float(row["iterations_per_window"])) != fixed_iterations:
            fail("iterations_per_window must equal fixed_iterations")
        if row.get("cloud_cost_status") != "WITHHELD_CLOUD_RATE_NOT_BOUND":
            fail("cloud dollars must be withheld")
        sample_count = int(float(row.get("nvml_sample_count") or 0))
        has_energy = row.get("gpu_energy_joules_per_iter") not in (None, "")
        if sample_count < MIN_NVML_ENERGY_SAMPLE_COUNT:
            withheld_energy_rows += 1
            if has_energy:
                fail("row below NVML sample-count gate must not publish joules")
            if row.get("nvml_energy_status") != "ENERGY_WITHHELD_INSUFFICIENT_NVML_SAMPLES_FIXED_ITERATION":
                fail("row below NVML sample-count gate must carry withheld energy status")
        else:
            accepted_energy_rows += 1 if has_energy else 0
        for key in ["wall_ms_total_window", "wall_ms_per_iter", "gpu_peak_memory_mib", "abs_error", "error_envelope"]:
            value = float(row[key])
            if value < 0:
                fail(f"negative {key}")
    if int(energy_gate.get("accepted_energy_rows") or -1) != accepted_energy_rows:
        fail("energy gate accepted row count mismatch")
    if int(energy_gate.get("withheld_energy_rows") or -1) != withheld_energy_rows:
        fail("energy gate withheld row count mismatch")
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
        "status_sha256": sha256_file(root / "ACCURACY_COST_ENERGY_PARETO_V2_GPU_H100_FIXED_ITER_STATUS.json"),
        "manifest_sha256": sha256_file(root / "artifact_manifest.json"),
        "measured_rows": len(rows),
        "frontier_rows": len(frontier),
        "fixed_iterations": fixed_iterations,
        "within_internal_envelope_rows": status.get("within_internal_envelope_rows"),
        "gpu_energy_accepted_rows": status.get("telemetry_status", {}).get("gpu_energy_accepted_rows"),
        "gpu_energy_withheld_rows": status.get("telemetry_status", {}).get("gpu_energy_withheld_rows"),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
