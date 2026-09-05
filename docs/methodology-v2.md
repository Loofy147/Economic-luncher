# Methodology v2

Ground-truth methodology has been tightened so vendor evidence, billing semantics, assumptions, derived results, and economic decisions are separate layers.

See `docs/ground-truth-contract.md` for the contract and `research/pricing_snapshots/2026-09-05.json` for the current verified-partial snapshot.

The mathematical core is:

- MAU-driven infrastructure: piecewise / workload-dependent pricing.
- Full-history AI: cumulative input processing is O(N^2) under fixed per-turn growth.
- Bounded context: cumulative input processing becomes O(N).
- Threshold-aware providers: request rates are a function of context size and effective pricing regime.
- Plan optimization: minimize cost over feasible plans, not all plans.
