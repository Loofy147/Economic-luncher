"""Runs the engine against the specific questions this project is meant to answer.
python examples/answer_questions.py"""
import sys, os

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src")))
from economics.context.strategies import crossover_turn_bounded_vs_cached
from economics.inference.cost import conversation_cost, first_crossover_turn
from economics.infrastructure.cost import upstash_cost, resend_cost
from economics.unit_economics.model import compute

B, C, O = 200, 900, 700

print("Q: At what conversation depth does a bounded (K=20) window beat full-history caching, on Claude Sonnet 5?")
n = crossover_turn_bounded_vs_cached("claude-sonnet-5", B, C, O, 20)
print(f"A: turn {n}\n")

print("Q: Is Upstash PAYG or Fixed cheaper for a steady 50,000-MAU workload at 150 commands/MAU?")
r = upstash_cost(50000 * 150, storage_mb_estimate=250)
print(f"A: {r['plan']} at ${r['cost']}/mo (PAYG would be ${r['payg_cost']}/mo)\n")

print("Q: At what monthly email volume does the Resend optimizer first prefer a Scale tier over Pro on pure price?")
for emails in [449000, 450000, 451000, 500000]:
    r = resend_cost(emails)
    print(f"   emails={emails:>8,}  plan={r['plan']:<12} cost=${r['cost']:,.2f}")
print()

print("Q: For an unbounded full-history conversation, at what turn does GPT-5.6 Sol cross its long-context pricing tier?")
turn = first_crossover_turn("gpt-5.6-sol", B, C)
c_sonnet = conversation_cost("claude-sonnet-5", 1000, B, C, O, cached=False)["total"]
c_sol = conversation_cost("gpt-5.6-sol", 1000, B, C, O, cached=False)["total"]
print(f"A: turn {turn}. By turn 1000, Sol costs ${c_sol:,.2f} vs Sonnet 5's ${c_sonnet:,.2f} ({c_sol/c_sonnet:.2f}x).\n")

print("Q: At what MAU does AI inference COGS overtake infrastructure COGS, for the 'saas' workload on Claude Sonnet 5?")
for mau in [10000, 50000, 100000, 250000, 500000, 1000000]:
    r = compute(mau, "saas", "claude-sonnet-5", mau * 0.4, 25)
    print(f"   MAU={mau:>8,}  infra=${r.infra_cogs:>9,.2f}  ai=${r.ai_cogs:>10,.2f}  driver={r.dominant_cost_driver}")
