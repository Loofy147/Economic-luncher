# Ground Truth Contract

This repository distinguishes **vendor evidence** from **derived economics**.

## Evidence states

- `verified`: directly supported by current first-party documentation.
- `verified_partial`: some fields are supported, while other model features or billing semantics remain outside scope.
- `verified_with_semantics_caveat`: rates are verified but a compound billing interaction still needs explicit provider clarification.
- `verified_baseline`: a narrow baseline (for example, one geography/payment method) is verified, not a universal price.
- `derived`: computed from verified facts; never presented as vendor wording.
- `unknown`: insufficient evidence; excluded from ground-truth calculations.

## Required fields for vendor/model entries

Every price-bearing entry should carry:

```json
{
  "canonical_model_id": "...",
  "status": "verified|verified_partial|verified_with_semantics_caveat|verified_baseline|derived|unknown",
  "source": "https://...",
  "effective_date": "YYYY-MM-DD"
}
```

For plan-based services, the entry must also describe constraints that can make a cheaper plan infeasible. Examples include storage, bandwidth, regions, domain limits, support/SLA, or request-rate ceilings.

## Canonical identity rule

A display name, analyst alias, or historical identifier is not sufficient to establish model identity. A model enters `ground truth` only when its canonical provider ID and current first-party pricing evidence are known.

Unknown aliases must remain explicitly rejected rather than silently mapped to the nearest model.

## Pricing rule

The engine must calculate price from the versioned snapshot, not scrape or mutate prices during a scenario run.

Live web research creates a **new snapshot**. It does not mutate an old snapshot.

## Optimization rule

The engine selects:

\[
argmin_{p \in P_{feasible}} Cost(p)
\]

not merely:

\[
argmin_{p \in P} Cost(p)
\]

A plan that is cheaper but violates workload or product requirements is not an admissible optimum.

## Boundary rule

Threshold behavior must be tested at:

- threshold - 1 unit
- threshold
- threshold + 1 unit

For bucketed billing, test the bucket transition as well.

## Reproducibility rule

A report is reproducible only if it records:

- pricing snapshot ID/date
- model identity
- workload configuration
- context policy
- cache policy
- scenario
- calculation version

The purpose is to make every economic claim replayable after vendor pricing changes.
