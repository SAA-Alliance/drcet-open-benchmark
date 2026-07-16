"""DRCET protocol validator.

Stdlib-only validator for the public DRCET protocol surface. It intentionally
checks protocol invariants beyond ordinary JSON Schema: claim boundary,
WITHHELD value suppression, artifact hashes, and status/verdict consistency.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

VALIDATOR_VERSION = "drcet-validator-0.1.0"
SHA_RE = re.compile(r"^sha256:[a-f0-9]{64}$")
ALLOWED_SCHEMA = "drcet.submission.v1"
ALLOWED_DRCET = {"DRCET-1", "DRCET-2", "DRCET-3"}
ALLOWED_TIERS = {"SYNTHETIC_FIXTURE", "INTERNAL_REPRODUCTION", "INDEPENDENT_REPRODUCTION", "EXTERNAL_CERTIFICATION"}
ALLOWED_STATUS = {"PUBLISHED", "WITHHELD", "DATA_SUSPECT", "NO_DATA", "FAILED"}
ALLOWED_VERDICTS = {"PASS", "WATCH", "FAIL", "WITHHELD"}
REQUIRED_NON_CLAIMS = {
    "not production approval",
    "not execution authorization",
    "not investment advice",
}


def _err(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_submission(payload: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, message: str = "") -> None:
        checks.append({"name": name, "status": "PASS" if ok else "FAIL", "message": message})
        if not ok:
            _err(errors, f"{name}: {message}")

    check("schema_version", payload.get("schema_version") == ALLOWED_SCHEMA, "expected drcet.submission.v1")
    check("drcet_version", payload.get("drcet_version") in ALLOWED_DRCET, "expected DRCET-1/2/3")
    check("evidence_tier", payload.get("evidence_tier") in ALLOWED_TIERS, "unknown evidence_tier")
    check("claim_boundary", isinstance(payload.get("claim_boundary"), str) and bool(payload.get("claim_boundary", "").strip()), "claim_boundary required")

    non_claims = payload.get("non_claims")
    check("non_claims_present", isinstance(non_claims, list) and len(non_claims) > 0, "non_claims must be non-empty array")
    non_claim_text = " | ".join(str(x).lower() for x in (non_claims or []))
    for claim in REQUIRED_NON_CLAIMS:
        check(f"non_claim:{claim}", claim in non_claim_text, f"missing {claim}")

    metrics = payload.get("metrics")
    check("metrics_present", isinstance(metrics, list) and len(metrics) > 0, "metrics must be non-empty array")
    if isinstance(metrics, list):
        for idx, metric in enumerate(metrics):
            prefix = f"metric[{idx}]"
            if not isinstance(metric, dict):
                check(prefix, False, "metric must be object")
                continue
            status = metric.get("status")
            verdict = metric.get("verdict")
            check(f"{prefix}.status", status in ALLOWED_STATUS, "invalid metric status")
            check(f"{prefix}.verdict", verdict in ALLOWED_VERDICTS, "invalid metric verdict")
            if status == "WITHHELD":
                check(f"{prefix}.withheld_value_absent", "value" not in metric, "WITHHELD metric must not serialize value")
                check(f"{prefix}.withheld_unlock_path", bool(metric.get("unlock_path")), "WITHHELD metric should include unlock_path")
            if status == "PUBLISHED":
                check(f"{prefix}.published_value_present", isinstance(metric.get("value"), (int, float)), "PUBLISHED metric requires numeric value")
            if verdict == "PASS":
                check(f"{prefix}.pass_not_withheld", status == "PUBLISHED", "PASS verdict requires PUBLISHED status")

    artifacts = payload.get("artifacts")
    check("artifacts_present", isinstance(artifacts, list) and len(artifacts) > 0, "artifacts must be non-empty array")
    if isinstance(artifacts, list):
        for idx, artifact in enumerate(artifacts):
            prefix = f"artifact[{idx}]"
            if not isinstance(artifact, dict):
                check(prefix, False, "artifact must be object")
                continue
            check(f"{prefix}.name", isinstance(artifact.get("name"), str) and bool(artifact.get("name", "").strip()), "artifact name required")
            check(f"{prefix}.sha256", isinstance(artifact.get("sha256"), str) and bool(SHA_RE.match(artifact.get("sha256", ""))), "artifact sha256 must be sha256:<64 hex>")

    status = "PASS" if not errors else "FAIL"
    return {
        "schema_version": "drcet.result.v1",
        "submission_id": str(payload.get("submission_id", "")),
        "validator_version": VALIDATOR_VERSION,
        "status": status,
        "checks": checks,
        "errors": errors,
    }


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("top-level JSON must be object")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a DRCET submission JSON file")
    parser.add_argument("submission", type=Path)
    parser.add_argument("--json", action="store_true", help="print machine-readable result")
    args = parser.parse_args(argv)

    result = validate_submission(load_json(args.submission))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"DRCET validation: {result['status']} ({args.submission})")
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
