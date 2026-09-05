"""Builds the full structured report from a named scenario config."""
from economics.pricing.loader import load_scenario, load_workload
from economics.unit_economics.model import compute
from economics.topology.detect import next_infra_thresholds, next_ai_threshold
from economics.inference.cost import conversation_cost


def build_report(scenario_name: str) -> dict:
    sc = load_scenario(scenario_name)
    workload = load_workload(sc["workload"])

    ue = compute(sc["mau"], sc["workload"], sc["model"], sc["monthly_revenue_usd"], sc["avg_transaction_usd"])

    infra_next = next_infra_thresholds(sc["mau"], workload)
    ai_next = next_ai_threshold(sc["model"], workload["prompt_base_tokens"], workload["context_growth_tokens_per_turn"],
                                 workload["turns_per_ai_user_per_month"])

    return {
        "scenario": sc["name"],
        "mau": ue.mau,
        "ai_active_users": ue.ai_active_users,
        "turns_per_ai_user_per_month": ue.turns_per_ai_user,
        "tokens_per_turn_output": workload["output_tokens_per_turn"],
        "context_growth_per_turn": workload["context_growth_tokens_per_turn"],
        "model": ue.model,
        "provider": _provider_of(ue.model),
        "cache_enabled": workload.get("cache_enabled", False),
        "infrastructure_plan": {
            "supabase": ue.infra_breakdown["supabase"],
            "upstash": ue.infra_breakdown["upstash"]["plan"],
            "resend": ue.infra_breakdown["resend"]["plan"],
        },
        "monthly_cogs_usd": round(ue.monthly_cogs, 2),
        "cogs_per_mau_usd": round(ue.cogs_per_mau, 5),
        "ai_cogs_per_ai_user_usd": round(ue.ai_cogs_per_ai_user, 5),
        "infra_cogs_usd": round(ue.infra_cogs, 2),
        "ai_cogs_usd": round(ue.ai_cogs, 2),
        "payment_cogs_usd": round(ue.payment_cogs, 2),
        "revenue_usd": ue.revenue,
        "gross_margin_pct": round(ue.gross_margin_pct, 2),
        "dominant_cost_driver": ue.dominant_cost_driver,
        "next_thresholds": {"infrastructure": infra_next, "ai_long_context": ai_next},
    }


def _provider_of(model_key: str) -> str:
    if model_key.startswith("claude"):
        return "anthropic"
    if model_key.startswith("gpt"):
        return "openai"
    if model_key.startswith("gemini"):
        return "google"
    return "unknown"
