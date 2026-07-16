# DRCET-2: Path-Functional Equivalence

DRCET-2 covers path-dependent risk functionals:

- terminal loss;
- max drawdown;
- time underwater;
- recovery horizon;
- jump count;
- other path functionals when declared.

The draft protocol requires each path-functional metric to declare whether it is terminal, pathwise, or event-count based.

DRCET-2 is intentionally separate from tail-metric equivalence because a method can match VaR/ES and still disagree on drawdown or recovery geometry.
