"""AI token cost model: threshold-aware pricing regimes + realistic accumulating prompt cache."""
from economics.pricing.loader import load_model_pricing


def _rates_for_context(model_cfg: dict, context_tokens: int) -> dict:
    threshold = model_cfg.get("long_context_threshold_tokens")
    if threshold and context_tokens > threshold:
        mult = model_cfg.get("long_context_multiplier")
        if mult:
            return {
                "input": model_cfg["input_usd_per_m"] * mult["input"],
                "output": model_cfg["output_usd_per_m"] * mult["output"],
                "cache_read": model_cfg["cache_read_usd_per_m"] * mult.get("cache_read", mult["input"]),
                "cache_write": model_cfg.get("cache_write_usd_per_m", model_cfg["input_usd_per_m"] * 1.25) * mult.get("cache_write", mult["input"]),
            }
        lc = model_cfg.get("long_context_rates", {})
        return {
            "input": lc.get("input_usd_per_m", model_cfg["input_usd_per_m"]),
            "output": lc.get("output_usd_per_m", model_cfg["output_usd_per_m"]),
            "cache_read": lc.get("cache_read_usd_per_m", model_cfg["cache_read_usd_per_m"]),
            "cache_write": lc.get("cache_write_usd_per_m", model_cfg.get("cache_write_usd_per_m", model_cfg["input_usd_per_m"])),
        }
    return {
        "input": model_cfg["input_usd_per_m"],
        "output": model_cfg["output_usd_per_m"],
        "cache_read": model_cfg["cache_read_usd_per_m"],
        "cache_write": model_cfg.get("cache_write_usd_per_m", model_cfg.get("cache_write_5m_usd_per_m", model_cfg["input_usd_per_m"] * 1.25)),
    }


def first_crossover_turn(model_key: str, base_tokens: int, growth_tokens_per_turn: int):
    """First turn number at which per-turn context exceeds this model's long-context threshold, if any."""
    cfg = load_model_pricing(model_key)
    threshold = cfg.get("long_context_threshold_tokens")
    if not threshold:
        return None
    turn = (threshold - base_tokens) // growth_tokens_per_turn + 2
    return max(1, int(turn))


def conversation_cost(model_key: str, turns: int, base_tokens: int, growth_tokens_per_turn: int,
                       output_tokens_per_turn: int, cached: bool = False) -> dict:
    """Cumulative cost of an N-turn conversation with growing (unbounded) context."""
    cfg = load_model_pricing(model_key)
    total = 0.0
    series = []
    for i in range(1, turns + 1):
        ctx = base_tokens + (i - 1) * growth_tokens_per_turn
        rates = _rates_for_context(cfg, ctx)
        if cached:
            new_tok = base_tokens if i == 1 else growth_tokens_per_turn
            read_tok = ctx - new_tok
            total += new_tok / 1e6 * rates["cache_write"] + read_tok / 1e6 * rates["cache_read"] + output_tokens_per_turn / 1e6 * rates["output"]
        else:
            total += ctx / 1e6 * rates["input"] + output_tokens_per_turn / 1e6 * rates["output"]
        series.append(total)
    return {"model": model_key, "turns": turns, "cached": cached, "total": total, "series": series}


def bounded_window_cost(model_key: str, turns: int, base_tokens: int, growth_tokens_per_turn: int,
                         output_tokens_per_turn: int, window_k: int) -> dict:
    """Cumulative cost with context capped at the last `window_k` turns -- converts O(N^2) to O(N)."""
    cfg = load_model_pricing(model_key)
    total = 0.0
    series = []
    for i in range(1, turns + 1):
        window = min(i - 1, window_k)
        ctx = base_tokens + window * growth_tokens_per_turn
        rates = _rates_for_context(cfg, ctx)
        total += ctx / 1e6 * rates["input"] + output_tokens_per_turn / 1e6 * rates["output"]
        series.append(total)
    return {"model": model_key, "turns": turns, "window_k": window_k, "total": total, "series": series}
