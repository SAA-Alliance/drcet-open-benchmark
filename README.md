# DRCET Open Benchmark Protocol

DRCET is an open protocol for **Deterministic Risk Calculation Equivalence Tests**: a way to publish, validate, and compare deterministic risk engines against reference or challenger evidence without hiding the claim boundary.

This repository contains the public protocol surface only:

- protocol documents for DRCET-1, DRCET-2, and DRCET-3;
- machine-readable JSON schemas;
- a dependency-light validator;
- synthetic fixtures for PASS and WITHHELD paths;
- CI checks that prove the fixtures and validator run cleanly.

## What DRCET Covers

| Track | Scope | Publication state in this repo |
|---|---|---|
| DRCET-1 | Tail metrics equivalence: VaR / ES / CVaR across horizons and confidence levels | Protocol surface |
| DRCET-2 | Path-functional equivalence: terminal loss, max drawdown, time underwater, recovery horizon, jump count | Draft protocol surface |
| DRCET-3 | Attribution/stress equivalence: factor/stress attribution, contribution concentration, replay/stochastic attribution consistency | Draft protocol surface |

## What This Repo Is Not

This repository is **not** external certification, not investment advice, not a production model approval, not a claim that any submitted engine is decision-grade, and not a replacement for independent model-risk review.

The included examples are synthetic fixtures. They are designed to validate the protocol and tooling, not to prove performance of any private engine.

## Quick Start

```bash
python3 -m drcet_validator.validate examples/synthetic_pass/drcet_submission.json
python3 -m drcet_validator.validate examples/synthetic_withheld/drcet_submission.json
python3 -m unittest discover -s tests -v
```

Expected result: both fixture submissions validate. The WITHHELD fixture proves that suppressed metrics do not serialize numeric values.

## Claim Boundary

A DRCET packet must make its boundary explicit:

- `claim_boundary` tells readers what the packet may and may not be used for.
- `non_claims` prevents marketing language from silently becoming a model-risk claim.
- `evidence_tier` separates synthetic fixtures, internal evidence, independent reproduction, and external certification.
- `metric.status = WITHHELD` forbids `value` serialization.

See [docs/CLAIM_BOUNDARY.md](docs/CLAIM_BOUNDARY.md).

## Repository Layout

```text
docs/                       Human-readable protocol docs
schemas/                    JSON schemas for submissions and results
drcet_validator/            Python validator, stdlib only
examples/                   Synthetic protocol fixtures
tests/                      Unit tests for validator behavior
.github/workflows/ci.yml    GitHub Actions validation
```

## License

Apache-2.0. See [LICENSE](LICENSE).
