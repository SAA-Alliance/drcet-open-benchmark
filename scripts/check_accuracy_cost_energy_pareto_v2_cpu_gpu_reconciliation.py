#!/usr/bin/env python3
"""Validate CPU/H100 reconciliation pack for Accuracy-Cost-Energy Pareto V2."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

VALID_STATUSES = {
    "INVALID_UNIT_MISMATCH_RECONCILIATION_WITHHELD",
    "CPU_H100_UNIT_MATCHED_ISO_ACCURACY_REVIEW_ONLY_DEVICE_UNSATURATED",
    "CPU_H100_FIXED_ITERATION_ISO_ACCURACY_REVIEW_ONLY_DEVICE_UNSATURATED",
    "CPU_H100_FIXED_ITERATION_GPU_LONG_WINDOW_ENERGY_REVIEW_ONLY_DEVICE_UNSATURATED",
    "CPU_H100_FIXED_ITERATION_5_BUDGET_GPU_LONG_WINDOW_ENERGY_REVIEW_ONLY_DEVICE_UNSATURATED",
}


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
        "ACCURACY_COST_ENERGY_PARETO_V2_CPU_GPU_RECONCILIATION_STATUS.json",
        "artifact_manifest.json",
        "invalidated_prior_speedups_by_method.csv",
        "invalidated_prior_speedups_by_dimension.csv",
        "cpu_gpu_unit_matched_common_rows.csv",
        "cpu_gpu_unit_matched_iso_accuracy_by_method.csv",
        "cpu_gpu_unit_matched_iso_accuracy_by_dimension.csv",
        "cpu_h100_unit_matched_iso_speedup_by_dimension.svg",
        "README.md",
    ]
    for name in required:
        if not (root / name).is_file():
            fail(f"missing {name}")
    status = json.loads((root / "ACCURACY_COST_ENERGY_PARETO_V2_CPU_GPU_RECONCILIATION_STATUS.json").read_text())
    manifest = json.loads((root / "artifact_manifest.json").read_text())
    if status.get("status") not in VALID_STATUSES:
        fail(f"unexpected status {status.get('status')}")
    gate = status.get("frontier_acceptance_gate", {})
    if gate.get("speedup_claim_allowed") is not False:
        fail("speedup claim must remain locked")
    if gate.get("crossover_claim_allowed") is not False:
        fail("crossover claim must remain locked")
    timing = status.get("timing_unit_contract", {})
    if status.get("status") == "INVALID_UNIT_MISMATCH_RECONCILIATION_WITHHELD":
        if timing.get("unit_matched") is not False:
            fail("invalid status must declare unit_matched=false")
        if status.get("review_only_findings", {}).get("median_unit_matched_iso_speedup_by_dimension"):
            fail("invalid status must not publish unit-matched speedups")
    else:
        if timing.get("unit_matched") is not True:
            fail("unit-matched status must declare unit_matched=true")
        if status.get("status") in {
            "CPU_H100_FIXED_ITERATION_ISO_ACCURACY_REVIEW_ONLY_DEVICE_UNSATURATED",
            "CPU_H100_FIXED_ITERATION_GPU_LONG_WINDOW_ENERGY_REVIEW_ONLY_DEVICE_UNSATURATED",
            "CPU_H100_FIXED_ITERATION_5_BUDGET_GPU_LONG_WINDOW_ENERGY_REVIEW_ONLY_DEVICE_UNSATURATED",
        }:
            amort = status.get("amortization_contract", {})
            if timing.get("amortization_matched") is not True or amort.get("amortization_matched") is not True:
                fail("fixed-iteration status must declare amortization_matched=true")
            if int(amort.get("fixed_iterations_cpu") or -1) != int(amort.get("fixed_iterations_h100") or -2):
                fail("fixed iterations must match")
            if int(amort.get("warmup_iterations_cpu") or -1) != int(amort.get("warmup_iterations_h100") or -2):
                fail("warmup iterations must match")
        if gate.get("iso_accuracy_filter_applied") is not True:
            fail("iso-accuracy filter must be applied")
        cloud = status.get("cloud_cost_profile", {})
        if cloud:
            if cloud.get("h100_rate_bound") is not True:
                fail("attached cloud-cost profile must bind H100 rate")
            if cloud.get("contabo_cpu_rate_bound") is not False:
                fail("current cloud-cost profile must keep Contabo CPU rate withheld")
            if cloud.get("cloud_cost_profile_bound") is not False:
                fail("cloud-cost profile must remain partial without CPU rate")
            if gate.get("cloud_cost_profile_bound") is not False:
                fail("frontier gate must not mark cloud cost fully bound")
        energy_gate = status.get("gpu_energy_quality_gate", {})
        if energy_gate.get("status") == "WITHHELD_INSUFFICIENT_NVML_SAMPLE_COUNT_FIXED_ITERATION":
            if gate.get("gpu_energy_measured") is not False:
                fail("GPU energy must not be claim-measured when NVML sample-count gate fails")
            if status.get("telemetry_matrix", {}).get("gpu_joules") != "WITHHELD_INSUFFICIENT_NVML_SAMPLE_COUNT_FIXED_ITERATION":
                fail("telemetry matrix must withhold GPU joules when NVML sample-count gate fails")
        if status.get("status") == "CPU_H100_FIXED_ITERATION_GPU_LONG_WINDOW_ENERGY_REVIEW_ONLY_DEVICE_UNSATURATED":
            long_window_status = True
        elif status.get("status") == "CPU_H100_FIXED_ITERATION_5_BUDGET_GPU_LONG_WINDOW_ENERGY_REVIEW_ONLY_DEVICE_UNSATURATED":
            long_window_status = True
        else:
            long_window_status = False
        if long_window_status:
            if status.get("gpu_energy_long_window_attached") is not True:
                fail("long-window status must declare gpu_energy_long_window_attached=true")
            if energy_gate.get("status") != "PASS_NVML_LONG_WINDOW_SAMPLE_COUNT_RELEASE_QUALITY":
                fail("long-window status requires release-quality NVML gate")
            comp_gate = status.get("gpu_energy_comparability_gate", {})
            if comp_gate.get("status") != "PASS_MULTI_METHOD_CELL_COVERAGE":
                fail("long-window status requires multi-method energy comparability")
            if gate.get("gpu_energy_measured") is not True:
                fail("long-window status must mark GPU energy measured")
            if gate.get("gpu_energy_comparable_across_methods") is not True:
                fail("frontier gate must mark GPU energy comparable across methods")
            if status.get("telemetry_matrix", {}).get("gpu_joules") != "MEASURED_NVML_LONG_WINDOW_POWER_INTEGRATED_PER_ITER":
                fail("telemetry matrix must cite long-window GPU joules")
            if status.get("telemetry_matrix", {}).get("gpu_joules_source") != "H100_LONG_WINDOW_ENERGY_PACK":
                fail("telemetry matrix must identify long-window GPU energy source")
            join = status.get("gpu_energy_join_contract", {})
            if join.get("status") != "ATTACHED_WORKLOAD_LEVEL_LONG_WINDOW_ENERGY":
                fail("long-window energy join contract missing")
            if int(join.get("energy_workload_rows") or -1) <= 0:
                fail("expected positive energy workload rows")
            if int(join.get("metric_rows_represented") or -1) != int(join.get("energy_workload_rows") or 0) * 10:
                fail("expected metric rows represented by long-window energy to equal workload rows x 10")
            if gate.get("speedup_claim_allowed") is not False or gate.get("crossover_claim_allowed") is not False:
                fail("long-window energy must not unlock speedup/crossover")
        sweep = status.get("path_budget_sweep_contract", {})
        if status.get("status") == "CPU_H100_FIXED_ITERATION_5_BUDGET_GPU_LONG_WINDOW_ENERGY_REVIEW_ONLY_DEVICE_UNSATURATED":
            if sweep.get("status") != "PASS_MINIMUM_5_BUDGET_SWEEP":
                fail("5-budget status requires PASS_MINIMUM_5_BUDGET_SWEEP")
            if int(sweep.get("path_budget_count") or -1) < int(sweep.get("minimum_path_budget_levels_required") or 999):
                fail("5-budget status has insufficient path-budget count")
            if gate.get("path_budget_sweep_complete") is not True:
                fail("frontier gate must mark path_budget_sweep_complete=true")
        dims = load_csv(root / "cpu_gpu_unit_matched_iso_accuracy_by_dimension.csv")
        methods = load_csv(root / "cpu_gpu_unit_matched_iso_accuracy_by_method.csv")
        common = load_csv(root / "cpu_gpu_unit_matched_common_rows.csv")
        join = status.get("join_key_contract", {})
        reproduced_iso = sum(1 for row in common if str(row.get("both_within_error_envelope", "")).lower() == "true")
        if int(join.get("common_rows") or -1) != len(common):
            fail("join_key_contract common_rows does not match row-level CSV")
        if int(join.get("reproduced_iso_accuracy_common_rows") or -1) != reproduced_iso:
            fail("join_key_contract reproduced_iso_accuracy_common_rows mismatch")
        if int(status.get("iso_accuracy_contract", {}).get("iso_accuracy_common_rows") or -1) != reproduced_iso:
            fail("iso_accuracy_contract count does not reproduce from common rows")
        if len({row.get("join_key") for row in common}) != len(common):
            fail("join_key must be unique")
        for row in common:
            if not row.get("join_key") or not row.get("method_pair_key"):
                fail("common row missing join_key/method_pair_key")
            if status.get("status") in {
                "CPU_H100_FIXED_ITERATION_ISO_ACCURACY_REVIEW_ONLY_DEVICE_UNSATURATED",
                "CPU_H100_FIXED_ITERATION_GPU_LONG_WINDOW_ENERGY_REVIEW_ONLY_DEVICE_UNSATURATED",
                "CPU_H100_FIXED_ITERATION_5_BUDGET_GPU_LONG_WINDOW_ENERGY_REVIEW_ONLY_DEVICE_UNSATURATED",
            }:
                if int(float(row["cpu_iterations_per_window"])) != int(float(row["h100_iterations_per_window"])):
                    fail("fixed-iteration common row has unmatched iterations")
                if int(float(row["cpu_warmup_iterations_excluded"])) != int(float(row["h100_warmup_iterations_excluded"])):
                    fail("fixed-iteration common row has unmatched warmup policy")
            if row.get("h100_nvml_energy_status") == "ENERGY_WITHHELD_INSUFFICIENT_NVML_SAMPLES_FIXED_ITERATION" and row.get("h100_gpu_energy_joules_per_iter") not in (None, ""):
                fail("withheld H100 energy row must not carry joules per iter")
        if len(dims) != 4:
            fail("expected 4 dimension rows")
        if len(methods) != 4:
            fail("expected 4 method rows")
        for row in dims + methods:
            if int(float(row["common_rows"])) <= 0:
                fail("common_rows must be positive")
            if int(float(row["iso_accuracy_common_rows"])) <= 0:
                fail("iso_accuracy_common_rows must be positive")
            speed = float(row["review_only_wall_time_speedup_cpu_over_h100_iso"])
            if speed <= 0:
                fail("unit-matched speedup diagnostic must be positive")
        sat = status.get("device_saturation_analysis", {})
        if sat.get("device_saturated") is not False:
            fail("current H100 diagnostic should remain unsaturated/claim-locked")
        if sat.get("extrapolation_allowed") is not False:
            fail("extrapolation must be prohibited while unsaturated")
        acc = status.get("accuracy_invariant", {})
        if acc.get("fixed_iteration_within_envelope_rows") is None:
            fail("accuracy invariant must publish fixed_iteration_within_envelope_rows")
        if acc.get("single_shot_within_envelope_rows") is None:
            fail("accuracy invariant must publish single_shot_within_envelope_rows")
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
        "status_sha256": sha256_file(root / "ACCURACY_COST_ENERGY_PARETO_V2_CPU_GPU_RECONCILIATION_STATUS.json"),
        "manifest_sha256": sha256_file(root / "artifact_manifest.json"),
        "speedup_claim_allowed": gate["speedup_claim_allowed"],
        "crossover_claim_allowed": gate["crossover_claim_allowed"],
        "unit_matched": timing.get("unit_matched"),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
