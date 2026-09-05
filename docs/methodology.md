# Methodology

## Layer model

`Vendor Evidence -> Canonical Pricing Snapshot -> Billing Semantics -> Workload -> Cost Model -> Regime Detection -> Unit Economics -> Decision`

- **Vendor evidence**: first-party pricing/model documentation with date and source URL.
- **Canonical pricing**: `configs/vendors/*.json`; model aliases are not accepted as identity.
- **Billing semantics**: free-tier rules, overage buckets, threshold pricing, cache writes/reads, and plan constraints.
- **Workload**: explicit assumptions converting MAU into resource consumption.
- **Cost model**: deterministic calculations from versioned pricing + workload + billing rules.
- **Regime detection**: active regime, next boundary, and distance to boundary.
- **Unit economics**: direct COGS/user, AI COGS/AI-user, contribution margin, gross margin, and cost-driver attribution.
- **Decision**: cheapest feasible plan/architecture, not simply cheapest listed plan.

## Evidence states

`verified`, `verified_partial`, `verified_with_semantics_caveat`, `verified_baseline`, `derived`, and `unknown` are defined in `docs/ground-truth-contract.md`.

## AI context economics

With fixed context growth C and full-history replay:

\[
I(N)=BN+C\frac{N(N-1)}2=O(N^2)
\]

With bounded retention K:

\[
I(N)=\sum_{i=1}^{N}[B+\min(i-1,K)C]=O(N)
\]

This is a conditional architectural result, not a universal property of LLM APIs.

## Thresholds

Explicit usage thresholds must be tested immediately below, at, and immediately above the boundary. Bucketed billing must also test the bucket transition.

## Plan optimization

\[
p^*=\arg\min_{p\in P_{feasible}}Cost(p)
\]

Feasibility includes storage, bandwidth, region, throughput, domains, SLA, and other product/workload constraints.

## Reproducibility

A report records the pricing snapshot/date, canonical model/plan ID, workload, context policy, cache policy, scenario, and calculation version. Historical snapshots are immutable; live research creates a new snapshot.

## Known limitations

- Supabase compute/storage/egress are outside the baseline MAU model.
- Vercel variable cost requires a resource/workload trace; MAU alone is insufficient.
- OpenAI compound cache-write + long-context behavior remains explicitly marked as a semantic caveat until independently confirmed.
- Production traffic needs distributions of turns, context sizes, output lengths, cache hits, and tool calls; mean scenarios are not production forecasts.
