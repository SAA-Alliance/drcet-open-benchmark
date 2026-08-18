#!/usr/bin/env python3
"""Validate Pareto V2 cloud-cost profile."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pack_dir")
    args = ap.parse_args()
    root = Path(args.pack_dir)
    status_path = root / "CLOUD_COST_PROFILE_STATUS.json"
    manifest_path = root / "artifact_manifest.json"
    for path in [status_path, manifest_path, root / "README.md"]:
        if not path.is_file():
            fail(f"missing {path.name}")
    status = json.loads(status_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    gate = status.get("frontier_acceptance_gate", {})
    if gate.get("h100_rate_bound") is not True:
        fail("H100 rate must be bound for current profile")
    if gate.get("contabo_cpu_rate_bound") is not False:
        fail("Contabo CPU rate must remain explicitly withheld unless provided")
    if gate.get("cloud_cost_profile_bound") is not False:
        fail("cloud cost profile must not be fully bound without CPU rate")
    if gate.get("dollar_frontier_claim_allowed") is not False:
        fail("dollar frontier claim must remain locked")
    if status.get("h100_gpu_rate", {}).get("hourly_usd") != 3.96:
        fail("H100 hourly rate mismatch")
    mf = {f["path"]: f for f in manifest.get("files", [])}
    for name in ["CLOUD_COST_PROFILE_STATUS.json", "README.md"]:
        if name not in mf:
            fail(f"manifest missing {name}")
        if mf[name]["sha256"] != sha256_file(root / name):
            fail(f"manifest sha mismatch for {name}")
    print(json.dumps({
        "status": status["status"],
        "status_sha256": sha256_file(status_path),
        "manifest_sha256": sha256_file(manifest_path),
        "h100_hourly_usd": status["h100_gpu_rate"]["hourly_usd"],
        "cloud_cost_profile_bound": gate["cloud_cost_profile_bound"],
        "dollar_frontier_claim_allowed": gate["dollar_frontier_claim_allowed"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
