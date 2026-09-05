# zero-capex-economics

An economic cost topology engine for AI-assisted software ventures: not a rate card, but a model of *how cost moves between pricing regimes* as MAU, conversation depth, context size, cache-hit rate, workload shape, and feasible plan choice change.

## Ground-truth status

The `2026-09-05` pricing snapshot is intentionally marked `verified_partial`. Vendor facts are separated from derived results, and canonical model IDs are required before a model can enter the calculation layer. See `docs/ground-truth-contract.md`.

## Why this exists

A flat "$X/month" estimate hides the mechanisms that actually change cost. Some services are piecewise-linear in a metric; others depend on workload shape; AI inference can change regime when context crosses a provider threshold. This engine makes those transitions explicit and reproducible.

## Install & run

```bash
python3 examples/run_baseline.py baseline
python3 examples/answer_questions.py
python3 tests/_runner.py
python3 -m pytest tests/ -q
```

## Layout

```
configs/vendors/             versioned vendor pricing and canonical model identities
configs/workloads/           explicit workload assumptions
configs/scenarios/           named scenarios
src/economics/
  pricing/                   config loading and normalization
  infrastructure/            Supabase / Upstash / Resend / Vercel
  inference/                 threshold-aware AI token economics
  context/                   context-strategy comparison
  payments/                  transaction economics
tests/                       invariant, boundary, and regression tests
research/pricing_snapshots/  immutable dated evidence snapshots
docs/
  ground-truth-contract.md   evidence and reproducibility rules
  methodology.md             mathematical and modeling assumptions
  pricing-regimes.md         threshold reference
examples/                    runnable analyses
```

## Verified boundaries and known limitations

- **Resend:** plan selection is optimized from versioned tiers; a fixed crossover is not hardcoded because price and capabilities are separate decision variables.
- **Upstash:** PAYG and Fixed are compared as separate regimes; storage, bandwidth, read-region, and throughput constraints can affect feasibility.
- **Vercel:** Active CPU and Provisioned Memory are modeled as separate resource dimensions; MAU alone is insufficient to forecast Vercel variable cost.
- **AI:** full-history context is quadratic in cumulative input processing under fixed per-turn growth; bounded context changes the asymptotic regime to linear.
- **Google model identity:** current canonical IDs are used (`gemini-3.1-flash-lite`, `gemini-3-flash-preview`, `gemini-3.1-pro-preview`, `gemini-3.7-flash`). Prior aliases are deliberately rejected.

Still outside the baseline model: Supabase compute/storage/egress, detailed Vercel traces, provider-specific tool charges, production traffic distributions, and probabilistic economic-risk scoring.

## Extension principle

New vendor facts belong in `configs/vendors/` and a dated snapshot. New assumptions belong in `configs/workloads/`. New formulas belong in pure calculation modules. Reports must be generated from these layers rather than hand-editing results.
