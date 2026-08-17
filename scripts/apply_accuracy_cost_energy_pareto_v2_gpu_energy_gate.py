#!/usr/bin/env python3
"""Apply the fixed-iteration NVML energy-quality gate to an existing H100 pack.

This is a metadata/row reclassification step, not a benchmark rerun. It preserves
timing and accuracy rows while withholding per-iteration joules when the fixed
timing window did not collect enough NVML power samples for release-quality
energy integration.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

DEFAULT_PACK = Path("docs/benchmarks/accuracy_cost_energy_pareto_v2_gpu_h100_fixed_iter_20260817")
STATUS_FILE = "ACCURACY_COST_ENERGY_PARETO_V2_GPU_H100_FIXED_ITER_STATUS.json"
MEASURED_CSV = "measured_results_gpu_h100_fixed_iter.csv"
FRONTIER_CSV = "gpu_fixed_iter_internal_frontier.csv"
MIN_NVML_ENERGY_SAMPLE_COUNT = 20


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: Iterable[Dict[str, Any]], fields: Sequence[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(fields), extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def numeric(row: Dict[str, str], key: str) -> float | None:
    raw = row.get(key)
    if raw in (None, ""):
        return None
    return float(raw)


def median(values: Sequence[float]) -> float | str:
    return "" if not values else float(statistics.median(values))


def gate_rows(rows: List[Dict[str, str]], min_samples: int) -> Dict[str, Any]:
    accepted = 0
    withheld = 0
    sample_counts: List[int] = []
    for row in rows:
        sample_count = int(float(row.get("nvml_sample_count") or 0))
        sample_counts.append(sample_count)
        has_raw_energy = row.get("gpu_energy_joules_total_window") not in (None, "")
        if has_raw_energy and sample_count >= min_samples:
            accepted += 1
            row["nvml_energy_status"] = f"MEASURED_NVML_POWER_INTEGRATED_SAMPLE_COUNT_GE_{min_samples}_REVIEW_ONLY"
        else:
            withheld += 1
            row["nvml_energy_status"] = "ENERGY_WITHHELD_INSUFFICIENT_NVML_SAMPLES_FIXED_ITERATION"
            row["gpu_energy_joules_total_window"] = ""
            row["gpu_energy_joules_per_iter"] = ""
    return {
        "accepted_energy_rows": accepted,
        "withheld_energy_rows": withheld,
        "sample_count_min": min(sample_counts) if sample_counts else 0,
        "sample_count_median": statistics.median(sample_counts) if sample_counts else 0,
        "sample_count_max": max(sample_counts) if sample_counts else 0,
        "energy_quality_sufficient": bool(rows and accepted == len(rows)),
    }


def update_group_summaries(status: Dict[str, Any], rows: List[Dict[str, str]], min_samples: int) -> None:
    for group_name, key_name in [("by_method", "method_id"), ("by_dimension", "dimension")]:
        groups = status.get(group_name) or {}
        for key, summary in groups.items():
            subset = [r for r in rows if str(r.get(key_name)) == str(key)]
            energies = [float(v) for r in subset if (v := r.get("gpu_energy_joules_per_iter")) not in (None, "")]
            sample_counts = [int(float(r.get("nvml_sample_count") or 0)) for r in subset]
            summary["median_gpu_energy_joules_per_iter"] = median(energies)
            summary["gpu_energy_accepted_rows"] = len(energies)
            summary["gpu_energy_withheld_rows"] = len(subset) - len(energies)
            summary["nvml_sample_count_min"] = min(sample_counts) if sample_counts else 0
            summary["nvml_sample_count_median"] = statistics.median(sample_counts) if sample_counts else 0
            summary["nvml_sample_count_max"] = max(sample_counts) if sample_counts else 0
            summary["gpu_energy_status"] = (
                "MEASURED_NVML_POWER_INTEGRATED_RELEASE_QUALITY"
                if subset and len(energies) == len(subset)
                else f"WITHHELD_INSUFFICIENT_NVML_SAMPLE_COUNT_MIN_{min_samples}"
            )


def update_frontier(frontier: List[Dict[str, str]], rows: List[Dict[str, str]]) -> None:
    grouped: Dict[Tuple[str, str, str], List[Dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault((row["target_id"], row["method_id"], str(row["path_budget"])), []).append(row)
    for item in frontier:
        subset = grouped.get((item["target_id"], item["method_id"], str(item["path_budget"])), [])
        energies = [float(v) for r in subset if (v := r.get("gpu_energy_joules_per_iter")) not in (None, "")]
        item["median_gpu_energy_joules_per_iter"] = median(energies)
        item["energy_release_quality_status"] = (
            "PASS_GROUP_HAS_RELEASE_QUALITY_ENERGY_ROWS"
            if energies
            else "WITHHELD_GROUP_INSUFFICIENT_NVML_SAMPLES"
        )


def update_manifest(pack: Path) -> None:
    manifest = {
        "schema_id": "saa.drcet.accuracy_cost_energy_pareto_gpu_h100_fixed_iter.v2.artifact_manifest",
        "artifact_id": pack.name,
        "generated_at_utc": now_utc(),
        "files": [],
    }
    for path in sorted(pack.iterdir()):
        if path.is_file() and path.name != "artifact_manifest.json":
            manifest["files"].append({"path": path.name, "sha256": sha256_file(path), "byte_length": path.stat().st_size})
    write_json(pack / "artifact_manifest.json", manifest)


def build(args: argparse.Namespace) -> Dict[str, Any]:
    pack = Path(args.pack_dir)
    status_path = pack / STATUS_FILE
    rows_path = pack / MEASURED_CSV
    frontier_path = pack / FRONTIER_CSV
    telemetry_path = pack / "telemetry_gap_report.json"
    readme_path = pack / "README.md"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    rows = load_csv(rows_path)
    frontier = load_csv(frontier_path)
    gate = gate_rows(rows, int(args.min_samples))
    update_group_summaries(status, rows, int(args.min_samples))
    update_frontier(frontier, rows)

    status["generated_at_utc"] = now_utc()
    status["claim_state"] = "GPU_FIXED_ITERATION_TIMING_MEASURED_ENERGY_AXIS_WITHHELD_INSUFFICIENT_NVML_SAMPLES"
    status["nvml_energy_quality_gate"] = {
        "status": "WITHHELD_INSUFFICIENT_NVML_SAMPLE_COUNT_FIXED_ITERATION" if not gate["energy_quality_sufficient"] else "PASS_NVML_SAMPLE_COUNT_RELEASE_QUALITY",
        "minimum_sample_count_required": int(args.min_samples),
        "sample_count_min": gate["sample_count_min"],
        "sample_count_median": gate["sample_count_median"],
        "sample_count_max": gate["sample_count_max"],
        "accepted_energy_rows": gate["accepted_energy_rows"],
        "withheld_energy_rows": gate["withheld_energy_rows"],
        "rule": "Fixed-iteration timing windows are not automatically valid energy windows; GPU joules require enough NVML samples or a separate long-window energy lane.",
    }
    telemetry = status.setdefault("telemetry_status", {})
    telemetry["gpu_joules"] = (
        "MEASURED_NVML_POWER_INTEGRATED_RELEASE_QUALITY"
        if gate["energy_quality_sufficient"]
        else "WITHHELD_INSUFFICIENT_NVML_SAMPLE_COUNT_FIXED_ITERATION"
    )
    telemetry["gpu_energy_release_quality_sufficient"] = gate["energy_quality_sufficient"]
    telemetry["gpu_energy_accepted_rows"] = gate["accepted_energy_rows"]
    telemetry["gpu_energy_withheld_rows"] = gate["withheld_energy_rows"]
    telemetry["gpu_energy_sample_count_minimum"] = int(args.min_samples)
    telemetry.pop("gpu_energy_measured_rows", None)

    frontier_gate = status.setdefault("frontier_acceptance_gate", {})
    frontier_gate["gpu_energy_release_quality_sufficient"] = gate["energy_quality_sufficient"]
    frontier_gate["gpu_energy_accepted_rows"] = gate["accepted_energy_rows"]
    frontier_gate["gpu_energy_withheld_rows"] = gate["withheld_energy_rows"]
    frontier_gate["reason"] = (
        "GPU H100 fixed-iteration timing rows are measured, but fixed timing windows do not provide release-quality NVML energy integration. "
        "CPU RAPL joules, dated cloud cost profile, external/multi-engine reference, and long-window GPU energy lane remain missing."
    )
    frontier_gate.pop("gpu_energy_measured_rows", None)

    write_csv(rows_path, rows, list(rows[0].keys()))
    write_csv(frontier_path, frontier, list(frontier[0].keys()))
    write_json(status_path, status)
    write_json(telemetry_path, {
        "schema_id": "saa.drcet.accuracy_cost_energy_pareto_gpu_h100_fixed_iter.v2.telemetry_gap_report",
        "artifact_id": pack.name,
        "generated_at_utc": now_utc(),
        "measured": ["gpu_wall_time_fixed_iteration", "gpu_peak_memory_mib"],
        "partial": [],
        "withheld": [
            {"field": "gpu_energy_joules", "reason": f"WITHHELD_UNLESS_NVML_SAMPLE_COUNT_GE_{int(args.min_samples)}_FIXED_ITERATION_OR_SEPARATE_LONG_WINDOW_ENERGY_LANE"},
            {"field": "cloud_dollars", "reason": "WITHHELD_CLOUD_RATE_NOT_BOUND"},
            {"field": "cpu_energy_joules", "reason": "CPU_PACK_WITHHELD_RAPL_NOT_AVAILABLE"},
            {"field": "public_crossover_claim", "reason": "INTERNAL_REFERENCE_ONLY_AND_CPU_ENERGY_MISSING"},
        ],
        "nvml_energy_quality_gate": status["nvml_energy_quality_gate"],
    })
    readme = readme_path.read_text(encoding="utf-8")
    marker = "\n## Energy telemetry quality gate\n"
    readme = readme.split(marker)[0].rstrip() + marker + (
        f"\nGPU wall time remains measured under the fixed-iteration protocol, but joules are withheld unless "
        f"`nvml_sample_count >= {int(args.min_samples)}`. Current accepted energy rows: "
        f"`{gate['accepted_energy_rows']}`; withheld energy rows: `{gate['withheld_energy_rows']}`; "
        f"sample count median: `{gate['sample_count_median']}`. A separate long-window energy lane is required "
        "before publishing energy or perf-per-watt claims.\n"
    )
    readme_path.write_text(readme, encoding="utf-8")
    update_manifest(pack)
    return {
        "status_sha256": sha256_file(status_path),
        "manifest_sha256": sha256_file(pack / "artifact_manifest.json"),
        **gate,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack-dir", default=str(DEFAULT_PACK))
    ap.add_argument("--min-samples", type=int, default=MIN_NVML_ENERGY_SAMPLE_COUNT)
    args = ap.parse_args()
    print(json.dumps(build(args), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
