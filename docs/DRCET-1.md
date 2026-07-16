# DRCET-1: Tail Metrics Equivalence

DRCET-1 covers tail risk metrics such as VaR, ES, and CVaR.

Required dimensions:

- metric family: `VAR`, `ES`, `CVAR`;
- horizon, for example `1D`, `10D`, `30D`, `90D`;
- confidence level, for example `0.95`, `0.99`, `0.999`;
- tolerance contract;
- reference or challenger artifact hash;
- verdict and claim boundary.

DRCET-1 is about equivalence of reported tail metrics under a declared contract. It is not by itself a production model approval.
