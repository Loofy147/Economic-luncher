"""Stripe fee: the one COGS line driven by revenue/AOV, not MAU or tokens."""
from economics.pricing.loader import load_vendor


def stripe_fee(monthly_revenue_usd: float, avg_transaction_usd: float) -> dict:
    cfg = load_vendor("stripe")["standard_us_online"]
    txns = monthly_revenue_usd / avg_transaction_usd if avg_transaction_usd > 0 else 0
    fee = monthly_revenue_usd * cfg["percent"] / 100 + txns * cfg["fixed_usd"]
    return {"transactions": txns, "fee": fee, "effective_rate_pct": (fee / monthly_revenue_usd * 100) if monthly_revenue_usd else 0}
