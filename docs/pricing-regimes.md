# Pricing Regimes Reference

A **regime** is a pricing state defined by a vendor's published plan, threshold, or effective date. Crossing a regime boundary may change the rate, base fee, included quota, or feasible capabilities.

| Provider / model | Metric | Boundary | Effect |
|---|---|---:|---|
| Supabase | MAU | 50,000 | Free allowance ends |
| Supabase | MAU | 100,000 | Pro included MAU ends; $0.00325/MAU overage begins |
| Upstash | commands/storage/bandwidth | plan limits | Free, PAYG and Fixed are alternative regimes with different constraints |
| Resend | emails/mo | 3,000 / 50,000 / 100,000 and higher published tiers | Base fee, overage rate, or plan capabilities change |
| GPT-5.6 Sol | input context tokens | 272,000 | Full request uses documented long-context multiplier: input 2x, output 1.5x |
| Gemini 3.1 Pro Preview | input context tokens | 200,000 | Input/output pricing changes from $2/$12 to $4/$18 per M tokens |
| Gemini 3.7 Flash | calendar date | 2027-01-01 | Introductory $0.75/$3.75 -> standard $1.50/$7.50 |
| GPT-5.6 Sol | calendar date | 2026-11-21 | Promotional $4/$20 pricing is documented through this date; re-verify afterward |

## Boundary policy

Threshold tests must evaluate the values immediately below, at, and immediately above the threshold. For bucketed billing, bucket transitions must also be tested.

A plan crossover is not a ground-truth fact merely because it appears in analyst prose. It must be recomputed from the versioned plan definitions and relevant constraints.

The engine should expose:

- current regime
- next regime
- distance to boundary
- assumptions driving the boundary
- whether the boundary is price-driven, capability-driven, or date-driven
