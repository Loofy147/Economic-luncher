# zero-capex-economics

An economic cost topology engine for AI-assisted software ventures: not a rate card, but a model of *how cost moves between pricing regimes* as MAU, conversation depth, context size, cache-hit rate, workload shape, and plan choice change.

## Why this exists

A flat "$X/month" estimate hides the thing that actually matters: every vendor in this stack prices in **steps**, not a smooth line. Supabase is free, then $25 flat, then $25 + a per-MAU rate. Resend's cheapest plan changes twice as volume grows. Two of the three major AI providers silently double their rate once a single request's context crosses a fixed token count. This engine makes those steps explicit and computable, instead of leaving them buried in a spreadsheet cell or a paragraph of prose.

## Install & run

```bash
cd zero-capex-economics
python3 examples/run_baseline.py baseline
python3 examples/answer_questions.py
python3 tests/_runner.py          # dependency-free test runner (this sandbox has no network for `pip install pytest`)
python3 -m pytest tests/ -q       # once pytest is available -- the test_*.py files are unmodified pytest tests
```

## Layout

```
configs/vendors/      one JSON file per vendor -- every rate, sourced and dated, nothing hardcoded in code
configs/workloads/     usage-ratio profiles (emails/MAU, turns/user, context growth, ...)
configs/scenarios/     named MAU + workload + model combinations
src/economics/
  pricing/             config loader + generic regime/threshold primitives
  infrastructure/       Supabase / Upstash (PAYG-vs-Fixed argmin) / Resend (tier argmin) / Vercel
  inference/             AI token cost, threshold-aware, with a real accumulating cache model
  context/               compares context-management strategies against each other
  payments/              Stripe
  unit_economics/        rolls everything into COGS/MAU, gross margin, dominant cost driver
  topology/               "what regime are we in, how far to the next one"
  reporting/              assembles the full report for a scenario
tests/                   19 tests, all passing -- see "What's verified" below
research/pricing_snapshots/   dated, sourced rate captures so a scenario stays reproducible after vendor prices change
docs/                    methodology and a pricing-regime quick reference
examples/                two runnable scripts
```

## What's verified vs. what's a documented simplification

Every number in `configs/vendors/` was checked against a live vendor pricing page as of 2026-09-05 (see `research/pricing_snapshots/2026-09-05.json` for sources). Two corrections worth flagging explicitly because they contradict commonly-repeated claims:

- **Resend's Pro-vs-Scale crossover is ~455,000-460,000 emails/month**, verified by comparing every published tier directly -- not the ~200,000 figure that shows up in a lot of secondary write-ups, and not "never" either (Scale's overage genuinely does taper to $0.46/1,000 at high volume).
- **Vercel's Active CPU billing excludes I/O wait** (a slow AI call does not burn Active CPU for the wait). What *does* keep billing during that wait is Provisioned Memory. The practical advice to stream long AI responses still holds -- the mechanism is a memory-duration cost, not a CPU cost.

Documented, not yet modeled: Supabase compute/storage/egress beyond the Auth-MAU meter, and a scored "economic risk" dimension (see `docs/methodology.md`). The engine is honest about this boundary rather than papering over it with an invented number.

## Extending it

- New vendor: drop a JSON file in `configs/vendors/`, add a cost function in the matching `src/economics/` module.
- New workload shape: add a JSON file in `configs/workloads/` -- no code changes needed.
- New question: most of "at what point does X beat Y" is a loop over `src/economics/inference/cost.py` or `src/economics/context/strategies.py`'s existing functions, as `examples/answer_questions.py` shows.
