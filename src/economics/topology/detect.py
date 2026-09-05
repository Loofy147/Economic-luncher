"""'What regime are we in, and how far to the next one' -- across every metered dimension at once."""
from economics.pricing.loader import load_vendor
from economics.inference.cost import first_crossover_turn


def next_infra_thresholds(mau: int, workload: dict) -> dict:
    sb = load_vendor("supabase")
    rs = load_vendor("resend")
    findings = {}

    if mau <= sb["free"]["included_mau"]:
        findings["supabase"] = {"current": "free", "next_threshold_mau": sb["free"]["included_mau"], "distance": sb["free"]["included_mau"] - mau}
    elif mau <= sb["pro"]["included_mau"]:
        findings["supabase"] = {"current": "pro_flat", "next_threshold_mau": sb["pro"]["included_mau"], "distance": sb["pro"]["included_mau"] - mau}
    else:
        findings["supabase"] = {"current": "pro_overage", "next_threshold_mau": None, "distance": None}

    emails = mau * workload["emails_per_mau_per_month"]
    next_tier = None
    for tier in rs["tiers"]:
        if emails <= tier["included_emails"]:
            next_tier = tier
            break
    if next_tier:
        findings["resend"] = {"next_threshold_emails": next_tier["included_emails"], "distance_emails": next_tier["included_emails"] - emails}
    else:
        findings["resend"] = {"next_threshold_emails": None, "distance_emails": None}

    return findings


def next_ai_threshold(model_key: str, base_tokens: int, growth_tokens_per_turn: int, current_turns: int) -> dict:
    crossover = first_crossover_turn(model_key, base_tokens, growth_tokens_per_turn)
    if crossover is None:
        return {"has_long_context_tier": False, "crossover_turn": None, "turns_remaining": None}
    return {
        "has_long_context_tier": True,
        "crossover_turn": crossover,
        "turns_remaining": max(0, crossover - current_turns),
        "already_crossed": current_turns >= crossover,
    }
