# The Economics of Zero-CAPEX Software Ventures: A Multi-Layered Cost Topology

**September 2026**

## Abstract

The economics of launching software ventures have shifted structurally with the rise of AI-assisted development, serverless compute, Backend-as-a-Service (BaaS), and multi-tenant managed clouds. Popular framing of this shift as "free" or uniformly "cheap" is imprecise. This paper builds a three-layer cost model — **Founder/Build OPEX**, **Infrastructure COGS**, and **AI Inference Economics** — using first-party, currently published pricing from Vercel, Cursor, Supabase, Upstash, Resend, Stripe, Anthropic, OpenAI, and Google as of September 2026. Four findings follow. First, a commercially viable web application on standard professional tooling has a cost floor near **$41–$43/month**, not zero. Second, managed-infrastructure spend follows a **piecewise-linear** path — free-tier steps followed by proportional slopes — rather than an exponential one. Third, several vendors (Upstash, Resend) apply structural rules at tier upgrades that materially change naive projections. Fourth, under an unbounded conversational architecture, AI cost grows **quadratically**, $O(N^2)$, in the number of turns — and the moment a provider's per-turn context crosses a long-context pricing threshold, that quadratic curve gets a second, steeper slope grafted onto it. Context governance, not infrastructure scaling, is the dominant lever on long-run software margins.

---

## 1. The Economic Shift: From CAPEX to Fragmented OPEX

Traditional software engineering required Capital Expenditure (CAPEX) — servers, storage arrays, database clusters — before a product could be validated. Modern stacks replace this with granular Operational Expenditure (OPEX) and usage-based Cost of Goods Sold (COGS): a founder can ship a production application against metered infrastructure and pay only for what is consumed.

That substitution trades one problem for another. Instead of one large upfront bill, a modern stack accumulates a **fragmented web of subscriptions and metered utilities**:

- **AI coding assistants** (Cursor Pro at $20/month, or comparable tools) reduce human labor while adding a fixed recurring toolchain cost.
- **Serverless/managed PaaS** (Vercel, Supabase, Upstash) decouple infrastructure from server management, but price dynamically on compute time, data egress, and command volume.
- **AI inference** (Anthropic, OpenAI, Google) prices by the token, with cost structure that depends on architecture, not just traffic.

Modern software is not "free." It is **low-fixed-cost and usage-sensitive**, which is a different — and for founders who don't model it, more surprising — thing.

---

## 2. Day-One Economic Baseline

The "$20–$50/month MVP" framing collapses several distinct cost tiers into one number. Decomposed:

$$C_{day1} = C_{\text{build tooling}} + C_{\text{commercial hosting}} + C_{\text{domain}} + C_{\text{runtime}}$$

| Component | Baseline Cost | Role |
|---|---|---|
| Cursor Pro | $20/mo | Build tooling |
| Vercel Pro | $20/mo (includes $20 usage credit) | Commercial hosting |
| Domain name | ~$1–3/mo amortized | Brand/DNS |
| Supabase | $0 (free tier, ≤50,000 MAU) | Database/Auth runtime |
| Upstash Redis | $0 (free tier, ≤500,000 commands/mo) | Cache runtime |
| Resend | $0 (free tier, ≤3,000 emails/mo) | Transactional email |
| Stripe | 2.9% + $0.30/transaction | Payments (variable, not fixed) |

Two structural notes matter here. Vercel's free "Hobby" tier is explicitly non-commercial; any product generating revenue requires Pro. Stripe has no monthly platform fee — its cost only appears once a transaction clears, which is why it's excluded from the fixed floor.

$$\boxed{C_{floor} \approx \$41\text{–}\$43/\text{month}}$$

---

## 3. Infrastructure Economics at Scale (MAU Modeling)

### 3.1 Workload Assumptions

To project infrastructure spend against Monthly Active Users (MAU), this model holds three ratios constant:

- 3 transactional emails per MAU/month
- 150 Redis commands per MAU/month
- Supabase billing driven by its Auth/MAU meter, isolated from compute, storage, and egress (see §6.3 for why this matters)

### 3.2 Piecewise-Linear Infrastructure Cost Matrix

| MAU | Supabase | Upstash | Resend | Total COGS |
|---:|---:|---:|---:|---:|
| 1,000 | $0 | $0 | $0 | **$0** |
| 5,000 | $0 | $1.50 | $20.00 | **$21.50** |
| 10,000 | $0 | $3.00 | $20.00 | **$23.00** |
| 25,000 | $0 | $7.50 | $42.50 | **$50.00** |
| 50,000 | $0 | $15.00 | $110.00 | **$125.00** |
| 75,000 | $25.00 | $22.50 | $177.50 | **$225.00** |
| 100,000 | $25.00 | $30.00 | $245.00 | **$300.00** |
| 150,000 | $187.50 | $45.00 | $380.00 | **$612.50** |
| 250,000 | $512.50 | $75.00 | $650.00 | **$1,237.50** |
| 500,000 | $1,325.00 | $150.00 | $1,325.00 | **$2,800.00** |
| 1,000,000 | $2,950.00 | $300.00 | $2,675.00 | **$5,925.00** |

**Mechanics behind the steps:**

- **Supabase**: free through 50,000 MAU; the $25/month Pro plan includes 100,000 MAU; beyond that, overage runs $0.00325/MAU.
- **Upstash**: pay-as-you-go runs $0.20 per 100,000 commands. Critically, once an account moves to a paid tier, the free 500,000-command allowance is **not** carried forward as a credit — the full command volume is billed at the PAYG rate. This is a documented platform rule, not an edge case, and it is why the 5,000-MAU row already shows a nonzero Upstash charge even though 750,000 commands/month is barely above the raw free-tier ceiling.
- **Resend**: free to 3,000 emails/month; Pro ($20/month) includes 50,000; overage is a flat $0.90 per 1,000 emails and does not decrease until monthly volume passes roughly 200,000 emails — at which point a rational operator would switch plans entirely (see §6.4).

From 100,000 to 1,000,000 MAU, total infrastructure COGS scales from $300 to $5,925 — a marginal rate of **$0.00625/MAU**. This confirms the piecewise-linear character of managed-cloud cost: step discontinuities at free-tier boundaries, proportional slopes in between, no exponential blow-up.

---

## 4. The AI Token Economy & Cross-Provider Topology

Infrastructure cost is predictable. AI inference cost is not — its growth rate is a property of the *conversation architecture*, not the traffic volume.

### 4.1 The Quadratic Growth Law

In a naive chat architecture that re-transmits full conversation history on every turn, with initial prompt size $B$ and per-turn context increment $C$, cumulative input tokens through turn $N$ follow an arithmetic series:

$$I(N) = \sum_{i=1}^{N} \big[B + (i-1)C\big] = BN + C\frac{N(N-1)}{2} = O(N^2)$$

Total cost additionally includes a per-turn output component. This model uses $B = 200$ tokens (initial prompt), $C = 900$ tokens (context added per turn), and $O = 700$ tokens (output generated per turn) as illustrative constants — a compact but realistic stand-in for a coding-agent or support-chat session.

### 4.2 Comparative Model Pricing Topology (September 2026)

| Provider / Model | Input ($/M) | Cached Read ($/M) | Output ($/M) | Context Window | Notes |
|---|---:|---:|---:|---:|---|
| Anthropic Claude Sonnet 5 | $2.00 | $0.20 | $10.00 | 1,000,000 | Flat rate, no long-context surcharge |
| Anthropic Claude Opus 5 | $5.00 | $0.50 | $25.00 | 1,000,000 | Flat rate |
| Anthropic Claude Haiku 4.5 | $1.00 | $0.10 | $5.00 | 200,000 | Cheapest Anthropic tier |
| OpenAI GPT-5.6 Sol | $4.00 (≤272K) / $8.00 (>272K)* | $0.40 / $0.80 | $20.00 / $30.00 | 1,050,000 | *Promotional rate through Nov 21, 2026; long-context multiplier applied to the promotional base |
| OpenAI GPT-5.6 Terra | $2.00 | $0.20 | $12.00 | 1,050,000 | Mid-tier GPT-5.6 |
| Google Gemini 3.1 Pro | $2.00 (≤200K) / $4.00 (>200K) | $0.20 / $0.40 | $12.00 / $18.00 | 1,000,000 | Tiered by context length |
| Google Gemini 3.8 Flash | $0.75 | $0.075 | $3.75 | 1,000,000 | Introductory through Dec 31, 2026; rises to $1.50/$0.15/$7.50 on Jan 1, 2027 |
| Google Gemini 3.1 Flash-Lite | $0.25 | $0.025 | $1.50 | 1,000,000 | Cheapest Gemini 3.x tier |

Google's ecosystem also grants **5,000 free Google Search grounding requests/month**, shared across the whole Gemini 3.x family (then $14/1,000 requests), plus a matching allowance for Google Maps grounding — a meaningful discovery/agentic-retrieval subsidy with no equivalent line item at Anthropic or OpenAI.

Two of the three providers price by **context tier**, not just by model: crossing a fixed token threshold mid-conversation silently raises the rate on *every* token in that request, input and output alike. This is the detail a flat per-model rate card hides, and it is the single biggest lever in the table below.

### 4.3 Cumulative Cost Scaling ($N$ turns; $B=200$, $C=900$, $O=700$)

| Turns ($N$) | Claude Sonnet 5 | GPT-5.6 Sol | Gemini 3.1 Pro | Gemini 3.8 Flash |
|---:|---:|---:|---:|---:|
| 10 | $0.16 | $0.31 | $0.17 | $0.06 |
| 50 | $2.58 | $5.15 | $2.65 | $0.97 |
| 100 | $9.65 | $19.30 | $9.79 | $3.62 |
| 1,000 | $906.50 | **$3,451.93** | **$1,766.02** | $339.94 |

At $N=10$ through $N=100$, every conversation in this table stays under each provider's long-context threshold, so cost differences simply track the headline per-token rates. By $N=1{,}000$, that stops being true. Given $B=200,\ C=900$, per-turn context exceeds Gemini's 200K threshold at **turn 224** and GPT-5.6 Sol's 272K threshold at **turn 304** — meaning roughly three-quarters of the conversation is billed at the premium tier. That is why GPT-5.6 Sol's $N=1{,}000$ cost is nearly **4×** Claude Sonnet 5's rather than the 2× a flat-rate comparison would suggest, and why Gemini 3.1 Pro — priced identically to Claude at the entry tier — ends up **95% more expensive** at scale. A pricing comparison run only at small $N$ would miss this entirely.

### 4.4 The Real Cost of Prompt Caching

Caching is usually described as "0.1× off input." That's true only for cache *reads*. Writing new content into the cache carries a **premium** over the base input rate (Claude Sonnet 5: $2.50/M to write vs. $2.00/M raw, a 1.25× multiplier), and only content that is subsequently *reused* earns back that premium via the $0.20/M read rate. A conversation that never reuses a turn's cached prefix is not cheaper under caching — it's more expensive.

Modeling a realistic accumulating-cache session (each turn writes only its new increment, then reads the full prior context from cache) on Claude Sonnet 5:

| Turns ($N$) | No Cache | With Cache | Reduction |
|---:|---:|---:|---:|
| 10 | $0.16 | $0.10 | 37% |
| 100 | $9.65 | $1.80 | 81% |
| 1,000 | $906.50 | $99.02 | 89% |

The saving is real and grows with $N$ — but it is a consequence of *reuse frequency*, not a flat discount, and it does not change the underlying exponent. Caching compresses the constant in front of $N^2$; it does not make the curve linear.

---

## 5. Architectural Mitigation: Breaking the Quadratic Ceiling

Three architectural changes address the $O(N^2)$ growth directly, in increasing order of engineering effort:

**1. Bounded context windows.** Retaining only the last $K$ turns of history caps the per-turn context at $B + KC$ instead of letting it grow indefinitely, which converts the cumulative cost curve from quadratic to linear: $I(N) \approx N(KC+B) = O(N)$. Concretely, on Claude Sonnet 5 at $N=1{,}000$ turns:

| Strategy | Total Cost |
|---|---:|
| Unbounded history | $906.50 |
| $K=50$ window | $95.10 |
| $K=20$ window | $43.02 |
| $K=10$ window | $25.30 |

A 20-turn window alone cuts cost by **95%** at this scale, at the price of the model losing visibility into anything older than 20 exchanges — a trade-off that has to be made deliberately, not by default.

**2. Retrieval-augmented memory.** Archive full history into a vector store (Supabase pgvector, Pinecone, or similar) and inject only the semantically relevant snippets per turn. This keeps effective context small like a bounded window, but without discarding older information outright — at the cost of retrieval latency and embedding spend.

**3. Model-tier routing.** Route mechanical sub-tasks (extraction, classification, formatting) to a low-cost model (Gemini 3.1 Flash-Lite, Claude Haiku 4.5) and reserve the flagship model for turns that need deep reasoning. Because cost scales with the *product* of tokens and per-token rate, halving the rate on routine turns compounds with any of the two strategies above.

---

## 6. Service Interdependencies and Operational Guidance

Each vendor in this stack has its own billing logic, and several of them interact in ways that aren't obvious from any single pricing page. This section is a practical map of those relationships.

### 6.1 Vercel ↔ everything downstream

Vercel is the traffic gateway: every request to Supabase, Upstash, or an AI provider from a serverless function is metered *twice* — once by Vercel and once by the downstream service. Under Fluid Compute, Vercel's Active CPU meter specifically **excludes** time spent waiting on I/O — a database query or an AI model call pauses CPU billing entirely, by design. What does *not* pause is Provisioned Memory, which bills for the full in-flight duration of a request, wait included. **Practical rule:** a slow AI call doesn't cost extra CPU-time on Vercel, but it does hold memory allocated for longer — stream responses and keep concurrency in mind if memory-hours, not CPU-hours, are the line item to watch.

### 6.2 Cursor ↔ the AI providers

Cursor's $20/month Pro plan bundles a $20 "Other Models" allowance that draws from the same underlying provider APIs priced in §4.2 — a heavy agentic session against a flagship model can exhaust that allowance well before the billing period ends, at which point cost shifts to metered on-demand pricing. **Practical rule:** route routine refactors and boilerplate generation to a cheaper model inside Cursor and reserve flagship-model calls for architecture-level decisions, mirroring the model-tier-routing strategy in §5.

### 6.3 Supabase's compute, storage, and egress meters are separate from the MAU meter used in §3

The infrastructure table in §3.2 isolates Supabase's Auth/MAU billing line to keep the model tractable — it does **not** include compute-tier upgrades, database storage overage, or egress overage, all of which scale with real usage independently of MAU count. In practice, an application at 500,000–1,000,000 MAU will almost certainly need a compute tier above the Pro plan's included Micro instance, plus meaningful egress overage; budget an additional **$100–$300/month** on top of the §3.2 figures once real traffic (not just account count) is considered.

### 6.4 Resend: Scale isn't a discount, it's a different purchase

It's tempting to read Resend's tiered Scale overage ($0.90 down to $0.46 per 1,000 at the top tier) as "switch to Scale once volume justifies it." Comparing every published tier directly shows the opposite holds for longer than expected: **Pro plus flat $0.90 overage remains the cheaper *price* until roughly 455,000–460,000 emails/month**, because Scale's much higher base fee ($90 vs. Pro's $20–$35) has to be earned back by its lower marginal rate first, and that takes a while. Below that volume, moving to Scale for a "cheaper rate" is a false economy — what Scale actually buys at that point is more domains, longer retention, and dedicated-IP eligibility, not a lower bill. Treat the plan choice as a genuine minimization over every published tier at each growth step, not a single volume-based rule of thumb in either direction.

### 6.5 Upstash: PAYG vs. Fixed is a traffic-shape decision, not a size decision

Because PAYG billing forfeits the free-tier allowance entirely on upgrade (§3.2), a workload with steady, predictable command volume above ~500,000/month is usually cheaper on a **Fixed** plan (from $10/month) than on PAYG, even though PAYG looks like the "pay for what you use" default. PAYG is the right choice for bursty or idle-heavy workloads; Fixed is the right choice for anything with a stable floor.

### 6.6 Stripe's fee is the one line item that scales with revenue, not usage

Every other service in this model scales with MAU or token count. Stripe scales with **transaction volume and average order value** instead — a business with few, high-value transactions pays a much lower effective rate (the $0.30 flat fee amortizes away) than one with many small transactions, where the flat fee dominates. This is worth modeling separately from the rest of the COGS stack precisely because its growth driver is unrelated to every other line in this paper.

### 6.7 The one dependency that changes everything: conversation architecture drives AI spend more than model choice

Section 4.3 showed GPT-5.6 Sol costing nearly 4× Claude Sonnet 5 at $N=1{,}000$ turns — not because its headline rate is 4× higher (it's roughly 2×), but because its longer per-token context threshold interacts with an unbounded-history architecture to spend more turns in the premium tier. **The architectural decision (bounded context, RAG, or full history) determines which model's pricing curve actually applies to a given product far more than the provider's headline per-token rate does.** Choosing a model before choosing a context strategy is choosing the wrong variable first.

---

## 7. Conclusion

The zero-CAPEX movement has genuinely eliminated the infrastructural barrier to entry: a production-grade application can launch for roughly $41–$43/month, and managed infrastructure scales in a predictable, piecewise-linear way through at least seven figures of MAU. What it has not eliminated is the need to model cost deliberately. Infrastructure vendors reward (or punish) specific plan and tier decisions at specific volume thresholds; AI providers reward (or punish) specific conversation architectures at specific turn counts. The venture that wins on unit economics is not the one that picked the cheapest model — it's the one that engineered its context so the cheapest model's pricing curve is the one that actually applies.
