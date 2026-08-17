#!/usr/bin/env python3
"""Validate H100 long-window energy pack for Accuracy-Cost-Energy Pareto V2."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


EXPECTED_STATUS = {
    "GPU_H100_LONG_WINDOW_ENERGY_MEASURED_RELEASE_QUALITY_REVIEW_ONLY",
    "GPU_H100_LONG_WINDOW_ENERGY_PARTIAL_WITHHELD_INSUFFICIENT_TELEMETRY",
}


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def load_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def int_field(obj: dict, key: str) -> int:
    if key not in obj or obj[key] is None:
        return -1
    return int(obj[key])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pack_dir")
    args = ap.parse_args()
    root = Path(args.pack_dir)
    required = [
        "ACCURACY_COST_ENERGY_PARETO_V2_GPU_H100_ENERGY_LONG_WINDOW_STATUS.json",
        "artifact_manifest.json",
        "gpu_h100_long_window_energy_results.csv",
        "gpu_h100_long_window_energy_by_dimension.csv",
        "gpu_h100_long_window_energy_by_method.csv",
        "gpu_h100_long_window_energy_by_dimension.svg",
        "hardware_probe.json",
        "telemetry_gap_report.json",
        "README.md",
    ]
    for name in required:
        if not (root / name).is_file():
            fail(f"missing {name}")

    status = json.loads((root / required[0]).read_text(encoding="utf-8"))
    manifest = json.loads((root / "artifact_manifest.json").read_text(encoding="utf-8"))
    rows = load_csv(root / "gpu_h100_long_window_energy_results.csv")
    dims = load_csv(root / "gpu_h100_long_window_energy_by_dimension.csv")
    methods = load_csv(root / "gpu_h100_long_window_energy_by_method.csv")

    if status.get("status") not in EXPECTED_STATUS:
        fail(f"unexpected status {status.get('status')}")
    if int_field(status, "workload_count") != len(rows):
        fail("workload_count mismatch")
    expected_workloads = (
        len({r["regime"] for r in rows})
        * len({int(float(r["dimension"])) for r in rows})
        * len({r["method_id"] for r in rows})
        * len({int(float(r["path_budget"])) for r in rows})
        * len({int(float(r["repeat_id"])) for r in rows})
    )
    if int_field(status, "workload_count") != expected_workloads:
        fail(f"expected {expected_workloads} workload rows")
    represented = sum(int(float(r["fixed_iter_metric_rows_represented"])) for r in rows)
    if int_field(status, "metric_rows_represented") != represented:
        fail("metric_rows_represented mismatch")
    if represented != len(rows) * 10:
        fail("expected metric rows represented to equal workload_rows x 10")
    if len(dims) != 4:
        fail("expected 4 dimension rows")
    if len(methods) != 4:
        fail("expected 4 method rows")

    min_required = int(status.get("energy_window_protocol", {}).get("minimum_nvml_sample_count_required") or -1)
    accepted = [r for r in rows if r["energy_status"] == "PASS_NVML_LONG_WINDOW_SAMPLE_COUNT_RELEASE_QUALITY"]
    withheld = [r for r in rows if r["energy_status"] != "PASS_NVML_LONG_WINDOW_SAMPLE_COUNT_RELEASE_QUALITY"]
    all_accepted = len(accepted) == len(rows)
    gate = status.get("nvml_energy_quality_gate", {})
    if int_field(gate, "accepted_energy_workload_rows") != len(accepted):
        fail("accepted_energy_workload_rows mismatch")
    if int_field(gate, "withheld_energy_workload_rows") != len(withheld):
        fail("withheld_energy_workload_rows mismatch")
    comp = status.get("energy_comparability_gate", {})
    cell_methods = {}
    for row in accepted:
        key = (row["regime"], int(float(row["dimension"])), int(float(row["path_budget"])), int(float(row["repeat_id"])))
        cell_methods.setdefault(key, set()).add(row["method_id"])
    min_methods_required = int(comp.get("minimum_release_quality_methods_per_cell_required") or -1)
    comparable_cells = sum(1 for methods_for_cell in cell_methods.values() if len(methods_for_cell) >= min_methods_required)
    if int_field(comp, "expected_cells") != expected_workloads // max(1, len({r["method_id"] for r in rows})):
        fail("energy_comparability_gate expected_cells mismatch")
    if int_field(comp, "comparable_cells") != comparable_cells:
        fail("energy_comparability_gate comparable_cells mismatch")
    if int_field(comp, "non_comparable_cells") != int_field(comp, "expected_cells") - comparable_cells:
        fail("energy_comparability_gate non_comparable_cells mismatch")
    if all_accepted and comp.get("status") != "PASS_MULTI_METHOD_CELL_COVERAGE":
        fail("all-accepted energy pack must pass multi-method cell comparability")
    if int_field(comp, "device_compute_comparable_cells") != int_field(comp, "expected_cells"):
        fail("device-compute energy comparability must cover every workload cell")
    if int_field(comp, "min_device_compute_methods_per_cell") < min_methods_required:
        fail("device-compute energy comparability below minimum method count")
    excluded = set(comp.get("host_transfer_heavy_methods_excluded_from_cross_method_aggregates") or [])
    if "gpu_randomized_qmc_cpu_sobol" not in excluded:
        fail("QMC host/transfer-heavy method must be excluded from cross-method energy aggregates")
    for row in accepted:
        if int(float(row["nvml_sample_count"])) < min_required:
            fail("accepted row below sample threshold")
        if row.get("gpu_energy_joules_per_iter") in (None, ""):
            fail("accepted row missing joules per iter")
    for row in withheld:
        if row.get("gpu_energy_joules_per_iter") not in (None, ""):
            fail("withheld row must not carry joules per iter")

    telemetry = status.get("telemetry_status", {})
    frontier = status.get("frontier_acceptance_gate", {})
    if all_accepted:
        if telemetry.get("gpu_joules") != "MEASURED_NVML_LONG_WINDOW_POWER_INTEGRATED_PER_ITER":
            fail("telemetry must publish long-window GPU joules when all rows pass")
        if frontier.get("gpu_energy_measured") is not True:
            fail("frontier gate must mark gpu_energy_measured=true when all rows pass")
        if frontier.get("gpu_energy_comparable_across_methods") is not True:
            fail("frontier gate must mark GPU energy comparable when all cells pass comparability")
    else:
        if telemetry.get("gpu_joules") != "WITHHELD_INSUFFICIENT_NVML_SAMPLE_COUNT_LONG_WINDOW":
            fail("partial pack must withhold GPU joules")
        if frontier.get("gpu_energy_measured") is not False:
            fail("partial pack must not claim GPU energy")
    if frontier.get("speedup_claim_allowed") is not False:
        fail("speedup claim must remain locked")
    if frontier.get("crossover_claim_allowed") is not False:
        fail("crossover claim must remain locked")
    cross_lane = status.get("cross_lane_join_contract", {})
    if cross_lane.get("status") != "CROSS_LANE_POWER_DERIVATION_FORBIDDEN":
        fail("cross-lane power derivation must be forbidden")
    if cross_lane.get("cross_lane_join_prohibited") is not True:
        fail("cross_lane_join_prohibited must be true")
    aggregate_policy = status.get("cross_method_energy_aggregate_policy", {})
    if aggregate_policy.get("status") != "QMC_HOST_TRANSFER_HEAVY_DISCLOSED_EXCLUDED_FROM_DEVICE_COMPUTE_AGGREGATES":
        fail("QMC aggregate exclusion policy missing")
    qmc = status.get("by_method", {}).get("gpu_randomized_qmc_cpu_sobol", {})
    if qmc.get("energy_measures_host_and_transfer") is not True:
        fail("QMC method must be marked host/transfer-heavy")
    if qmc.get("excluded_from_cross_method_energy_aggregates") is not True:
        fail("QMC method must be excluded from cross-method energy aggregates")
    saturation = status.get("h100_power_saturation_evidence", {})
    if saturation.get("status") != "GPU_POWER_UNDERSATURATED_REVIEW_ONLY":
        fail("H100 power saturation evidence must be present")
    if saturation.get("device_saturated") is not False:
        fail("H100 must remain marked unsaturated")
    if float(saturation.get("power_limit_watts") or 0.0) <= 0.0:
        fail("H100 power limit missing")
    if float(saturation.get("all_methods_max_dimension_median_power_fraction_of_tdp") or 1.0) >= 0.5:
        fail("H100 all-method power fraction unexpectedly saturated")
    if float(saturation.get("device_compute_max_dimension_median_power_fraction_of_tdp") or 1.0) >= 0.5:
        fail("H100 device-compute power fraction unexpectedly saturated")

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
        "status_sha256": sha256_file(root / "ACCURACY_COST_ENERGY_PARETO_V2_GPU_H100_ENERGY_LONG_WINDOW_STATUS.json"),
        "manifest_sha256": sha256_file(root / "artifact_manifest.json"),
        "workload_rows": len(rows),
        "metric_rows_represented": represented,
        "energy_comparability_gate": comp.get("status"),
        "comparable_cells": comp.get("comparable_cells"),
        "expected_cells": comp.get("expected_cells"),
        "accepted_energy_workload_rows": len(accepted),
        "withheld_energy_workload_rows": len(withheld),
        "sample_count_min": gate.get("sample_count_min"),
        "sample_count_median": gate.get("sample_count_median"),
        "all_methods_max_dimension_power_pct_of_tdp": saturation.get("all_methods_max_dimension_median_power_pct_of_tdp"),
        "device_compute_max_dimension_power_pct_of_tdp": saturation.get("device_compute_max_dimension_median_power_pct_of_tdp"),
        "speedup_claim_allowed": frontier["speedup_claim_allowed"],
        "crossover_claim_allowed": frontier["crossover_claim_allowed"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
