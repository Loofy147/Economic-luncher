# Methodology

## Layer model

`Source Data -> Normalized Pricing -> Workload -> Cost Model -> Regime Detection -> Unit Economics -> Report`

- **Source data**: vendor pricing pages, captured with a date and URL in `research/pricing_snapshots/`.
- **Normalized pricing**: `configs/vendors/*.json` -- one file per vendor, machine-readable, no number embedded in code.
- **Workload**: `configs/workloads/*.json` -- the ratios that turn a raw MAU count into emails, Redis commands, AI-active users, and turns/user. Swapping the workload file changes every downstream number without touching the pricing model.
- **Cost model**: `src/economics/infrastructure`, `src/economics/inference`, `src/economics/payments` -- pure functions from (usage, pricing config) to dollars. No global state, no hidden constants.
- **Regime detection**: `src/economics/topology` -- answers "what tier are we in, and how far to the next one" for every metered dimension (Supabase MAU tier, Resend email tier, a model's long-context threshold).
- **Unit economics**: `src/economics/unit_economics` -- rolls the three COGS categories into COGS/MAU, AI COGS/AI-user, gross margin, and identifies the dominant cost driver.
- **Report**: `src/economics/reporting` -- assembles the full field set for a named scenario.

## What "Price," "Cost," "COGS," and "Economic Risk" mean here

- **Price**: the published per-unit rate (`configs/vendors/*.json`).
- **Cost**: price applied to an actual workload (`infrastructure_cogs()`, `conversation_cost()`).
- **COGS**: the subset of cost directly attributable to serving a user or request -- excludes fixed build tooling like Cursor, which is a workflow cost, not a per-user cost.
- **Economic risk**: not separately quantified in this version. The `next_thresholds` field in every report is the raw material for it -- distance to the next priced regime is a proxy for how exposed a scenario is to a sudden step-change in COGS. A dedicated `risk` module (Monte Carlo over vendor-price-change and cache-hit-rate assumptions) is a natural next extension, not yet built.

## Known simplifications

- Supabase COGS covers only the Auth/MAU meter. Compute-tier upgrades, storage overage, and egress overage are real costs at scale and are **not** included -- see `docs/pricing-regimes.md`.
- The AI cost model assumes a single conversation shape (constant per-turn output, linear per-turn context growth) per workload. Real traffic has a distribution of conversation lengths; this engine models the mean case, not the distribution.
- GPT-5.6 Sol's long-context multiplier is a derived estimate (see `research/pricing_snapshots/2026-09-05.json` -> `known_unknowns`), not a vendor-published number at the current promotional rate.
- "Economic Risk" (vendor price-change exposure, cache-hit-rate variance) is described conceptually above but not yet implemented as a scored output.
