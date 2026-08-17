# DRCET-4 GitHub Disclosure Boundary

This repository may publish the DRCET-4 evidence contract, synthetic fixture
results, protocol text, hashes, counters, plots, checker logic and review-only
container replay receipts.

This repository must not publish:

- production ARIN22 kernel source;
- protected production container images or build context;
- credentials, environment files, service keys or private endpoints;
- customer/client data, portfolio payloads or commercial production datasets;
- hidden adversarial corpora or private truth anchors;
- internal deployment secrets, S3 credentials or RabbitMQ credentials.

The DRCET-4B Remizov-Chernoff lane is a review-only bounded-linear convergence
lane. It validates `G(0)=I`, tangency, stability, declared first-order bound,
observed rate, `E_n <= B_n`, and docker/no-egress replay on synthetic fixtures.

The DRCET-4C Chernoff-Remizov resolvent lane is a review-only bounded contract
surrogate. It validates the theorem-supported half-plane release gate, reports
the conservative a-priori certificate as a safety envelope rather than a tight
error estimate, and keeps production ARIN22 pending.

The DRCET-4D continuum spatial-refinement lane is a public-safe surrogate for
unbounded/continuum behavior. It uses analytic eigenmode fixtures and grid
refinement readback without publishing protected production operator factors.

These lanes do not certify the production ARIN22 kernel. Public wording must
keep this boundary:

> Foundation and governed routing validated; production ARIN22 kernel pending.
