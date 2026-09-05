# Ground Truth Contract

This repository distinguishes **vendor evidence** from **derived economics**.

## Evidence states

- `verified`: directly supported by current first-party documentation.
- `verified_partial`: some fields are supported while other meters/semantics remain outside scope.
- `verified_with_semantics_caveat`: rates are verified but a compound billing interaction remains unresolved.
- `verified_baseline`: a narrow baseline such as one geography/payment method.
- `derived`: computed from verified facts; never presented as vendor wording.
- `unknown`: insufficient evidence; excluded from ground-truth outputs.

## Required identity fields

Every price-bearing model entry must identify:

```json
{
  "canonical_model_id": "...",
  "status": "verified|verified_partial|verified_with_semantics_caveat|verified_baseline|derived|unknown",
  "source": "https://...",
  "effective_date": "YYYY-MM-DD"
}
```

An analyst alias is not a canonical identity. Unknown aliases are rejected rather than silently mapped to another model.

## Pricing and optimization rules

The engine calculates from an immutable versioned snapshot. Live research creates a new snapshot; it does not mutate historical snapshots.

Plan optimization is:

\[
argmin_{p\in P_{feasible}} Cost(p)
\]

A cheaper plan that violates storage, bandwidth, region, domain, throughput, SLA, or other constraints is not a valid optimum.

## Boundary rule

Explicit thresholds must be tested immediately below, at, and immediately above the boundary. Bucketed billing requires bucket-transition tests as well.

## Reproducibility

Reports must record pricing snapshot, canonical model/plan identity, workload, context policy, cache policy, scenario, and calculation version.
