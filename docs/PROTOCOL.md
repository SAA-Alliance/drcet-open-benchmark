# DRCET Protocol Overview

DRCET packets are evidence envelopes for deterministic risk calculation equivalence.

A packet has four layers:

1. **Submission metadata**: participant, engine, run id, evidence tier, claim boundary.
2. **Metric declarations**: metric family, horizon, confidence, tolerance, and status.
3. **Equivalence cases**: expected and observed values, deltas, confidence intervals, verdicts.
4. **Artifacts**: hashes, logs, reproducibility notes, and non-claims.

The protocol intentionally separates:

- calculation correctness from model approval;
- internal evidence from external certification;
- synthetic fixtures from real benchmark submissions;
- published values from withheld values.

## Verdicts

- `PASS`: within declared tolerance and no guardrail breach.
- `WATCH`: near boundary or low-power / incomplete evidence.
- `FAIL`: outside tolerance or contract breach.
- `WITHHELD`: result exists but must not serialize a value because a gate failed.

## Evidence Tiers

- `SYNTHETIC_FIXTURE`: protocol/validator fixture only.
- `INTERNAL_REPRODUCTION`: internal evidence, not external certification.
- `INDEPENDENT_REPRODUCTION`: independently reproduced evidence.
- `EXTERNAL_CERTIFICATION`: formal external certification, only with attached evidence.
