# Pricing Regimes Reference

A quick-reference for every threshold this engine tracks. "Regime" = a priced tier; crossing a threshold changes the *rate*, not just the *quantity billed*.

| Vendor | Metric | Threshold | What changes |
|---|---|---|---|
| Supabase | MAU | 50,000 | free -> $25/mo base |
| Supabase | MAU | 100,000 | flat $25 -> $25 + $0.00325/MAU overage |
| Upstash | commands/mo | 500,000 | free -> PAYG or Fixed (no free carry-over) |
| Resend | emails/mo | 3,000 / 50,000 / 100,000 / 200,000 / 500,000 / 1M / 1.5M / 2.5M | each step changes base fee and overage rate; **true Pro-vs-Scale price crossover is ~455-460K emails/mo**, not the 100-200K figure often assumed |
| GPT-5.6 Sol | context tokens (single request) | 272,000 | input/cache ~2x, output ~1.5x on the *entire* request |
| Gemini 3.1 Pro | context tokens (single request) | 200,000 | input/output/cache roughly double |
| Gemini 3.8 Flash | calendar date | 2027-01-01 | intro rate ($0.75/$3.75) -> standard rate ($1.50/$7.50) |
| GPT-5.6 Sol | calendar date | 2026-11-21 | promotional rate ($4/$20) -> standard rate ($5/$30), unless extended |

The two calendar-based thresholds matter as much as the usage-based ones: a report generated today can go stale on a fixed date even if traffic never changes.
