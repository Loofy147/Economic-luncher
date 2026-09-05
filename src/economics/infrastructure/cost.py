"""Infrastructure COGS: Supabase, Upstash (PAYG vs Fixed argmin), Resend (tier argmin), Vercel."""
import math
from economics.pricing.loader import load_vendor


def supabase_cost(mau: int) -> float:
    cfg = load_vendor("supabase")
    if mau <= cfg["free"]["included_mau"]:
        return 0.0
    pro = cfg["pro"]
    if mau <= pro["included_mau"]:
        return float(pro["base_fee_usd"])
    overage = (mau - pro["included_mau"]) * pro["mau_overage_usd_per_mau"]
    return pro["base_fee_usd"] + overage


def upstash_cost(commands_per_month: int, storage_mb_estimate: float = 250) -> dict:
    """Returns the cheaper of PAYG and best-fit Fixed plan, with the losing option shown for comparison."""
    cfg = load_vendor("upstash")
    if commands_per_month <= cfg["free"]["included_commands_per_month"] and storage_mb_estimate <= cfg["free"]["included_storage_mb"]:
        return {"plan": "free", "cost": 0.0, "payg_cost": 0.0, "best_fixed_cost": None}

    payg_cost = commands_per_month / 100000 * cfg["payg"]["usd_per_100k_commands"]

    best_fixed = None
    for plan in cfg["fixed_plans"]:
        if storage_mb_estimate <= plan["storage_mb"]:
            if best_fixed is None or plan["base_fee_usd"] < best_fixed["base_fee_usd"]:
                best_fixed = plan

    fixed_cost = best_fixed["base_fee_usd"] if best_fixed else None

    if fixed_cost is not None and fixed_cost < payg_cost:
        return {"plan": best_fixed["name"], "cost": fixed_cost, "payg_cost": payg_cost, "best_fixed_cost": fixed_cost}
    return {"plan": "payg", "cost": payg_cost, "payg_cost": payg_cost, "best_fixed_cost": fixed_cost}


def resend_cost(emails_per_month: int) -> dict:
    """argmin over every published tier -- not a hardcoded 'switch to Scale at X' rule."""
    cfg = load_vendor("resend")
    if emails_per_month <= cfg["free"]["included_emails"]:
        return {"plan": "free", "cost": 0.0}

    best = None
    for tier in cfg["tiers"]:
        if emails_per_month <= tier["included_emails"]:
            cost = float(tier["base_fee_usd"])
        else:
            overage_units = math.ceil((emails_per_month - tier["included_emails"]) / 1000)
            cost = tier["base_fee_usd"] + overage_units * tier["overage_usd_per_1k"]
        if best is None or cost < best["cost"]:
            best = {"plan": tier["name"], "cost": cost}
    return best


def vercel_cost(active_cpu_hours: float, provisioned_memory_gb_hours: float,
                 invocations: int, data_transfer_gb: float, seats: int = 1) -> dict:
    cfg = load_vendor("vercel")["pro"]
    rates = cfg["rates"]
    base = cfg["base_fee_usd"] * seats
    credit = cfg["usage_credit_usd"] * seats

    usage = (
        active_cpu_hours * rates["active_cpu_usd_per_cpu_hour"]
        + provisioned_memory_gb_hours * rates["provisioned_memory_usd_per_gb_hour"]
        + max(0, invocations) / 1_000_000 * rates["invocations_usd_per_million"]
        + max(0, data_transfer_gb - rates["fast_data_transfer_included_gb"]) * rates["fast_data_transfer_usd_per_gb"]
    )
    net_usage = max(0.0, usage - credit)
    return {"base": base, "usage": usage, "credit_applied": min(usage, credit), "total": base + net_usage}


def infrastructure_cogs(mau: int, workload: dict) -> dict:
    """Full infra COGS bundle for a given MAU under a workload profile."""
    emails = mau * workload["emails_per_mau_per_month"]
    commands = mau * workload["redis_commands_per_mau_per_month"]

    sb = supabase_cost(mau)
    up = upstash_cost(commands, workload.get("upstash_storage_mb_estimate", 250))
    rs = resend_cost(emails)

    total = sb + up["cost"] + rs["cost"]
    return {
        "supabase": sb,
        "upstash": up,
        "resend": rs,
        "total": total,
        "emails_per_month": emails,
        "redis_commands_per_month": commands,
    }
