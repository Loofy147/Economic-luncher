"""Rolls infra COGS + AI COGS + payment COGS into per-MAU unit economics."""
from dataclasses import dataclass, field
from economics.infrastructure.cost import infrastructure_cogs
from economics.inference.cost import conversation_cost
from economics.payments.stripe import stripe_fee
from economics.pricing.loader import load_workload


@dataclass
class UnitEconomicsReport:
    mau: int
    ai_active_users: int
    turns_per_ai_user: int
    model: str
    workload: str
    infra_cogs: float
    ai_cogs: float
    payment_cogs: float
    monthly_cogs: float
    cogs_per_mau: float
    ai_cogs_per_ai_user: float
    revenue: float
    gross_margin_pct: float
    dominant_cost_driver: str
    infra_breakdown: dict = field(default_factory=dict)


def compute(mau: int, workload_name: str, model_key: str, monthly_revenue_usd: float,
            avg_transaction_usd: float, cached: bool = None) -> UnitEconomicsReport:
    workload = load_workload(workload_name)
    cache_flag = workload.get("cache_enabled", False) if cached is None else cached

    infra = infrastructure_cogs(mau, workload)

    ai_active_users = int(mau * workload["ai_active_fraction_of_mau"])
    turns_per_user = workload["turns_per_ai_user_per_month"]
    ai_cost_per_user = conversation_cost(
        model_key, turns_per_user,
        workload["prompt_base_tokens"], workload["context_growth_tokens_per_turn"],
        workload["output_tokens_per_turn"], cached=cache_flag,
    )["total"]
    ai_cogs = ai_cost_per_user * ai_active_users

    pay = stripe_fee(monthly_revenue_usd, avg_transaction_usd)

    monthly_cogs = infra["total"] + ai_cogs + pay["fee"]
    gross_margin = ((monthly_revenue_usd - monthly_cogs) / monthly_revenue_usd * 100) if monthly_revenue_usd else 0.0

    drivers = {"infrastructure": infra["total"], "ai_inference": ai_cogs, "payments": pay["fee"]}
    dominant = max(drivers, key=drivers.get)

    return UnitEconomicsReport(
        mau=mau, ai_active_users=ai_active_users, turns_per_ai_user=turns_per_user,
        model=model_key, workload=workload_name,
        infra_cogs=infra["total"], ai_cogs=ai_cogs, payment_cogs=pay["fee"],
        monthly_cogs=monthly_cogs, cogs_per_mau=(monthly_cogs / mau if mau else 0),
        ai_cogs_per_ai_user=(ai_cogs / ai_active_users if ai_active_users else 0),
        revenue=monthly_revenue_usd, gross_margin_pct=gross_margin,
        dominant_cost_driver=dominant, infra_breakdown=infra,
    )
