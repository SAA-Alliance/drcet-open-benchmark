# Claim Boundary

Every DRCET packet must state what it proves and what it does not prove.

Minimum non-claims:

- not production approval;
- not execution authorization;
- not investment advice;
- not external certification unless an external certificate is attached;
- not model-risk signoff;
- not decision-grade approval by default.

Suppression rule:

If a metric status is `WITHHELD`, the metric must not serialize a numeric `value`. It may serialize `failed_pillar`, `unlock_path`, and non-sensitive context.
