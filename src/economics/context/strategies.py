"""Compares context-management strategies against each other -- answers 'which architecture wins, and when'."""
from economics.inference.cost import conversation_cost, bounded_window_cost


def crossover_turn_bounded_vs_cached(model_key: str, base_tokens: int, growth_tokens_per_turn: int,
                                      output_tokens_per_turn: int, window_k: int, max_turns: int = 5000) -> int | None:
    """First turn N at which a bounded-K window becomes cheaper than unbounded caching, for the same model.
    Returns None if bounded already wins at turn 1, or if caching never loses within max_turns."""
    for n in range(1, max_turns + 1):
        cached_total = conversation_cost(model_key, n, base_tokens, growth_tokens_per_turn, output_tokens_per_turn, cached=True)["total"]
        bounded_total = bounded_window_cost(model_key, n, base_tokens, growth_tokens_per_turn, output_tokens_per_turn, window_k)["total"]
        if bounded_total < cached_total:
            return n
    return None


def crossover_turn_between_models(model_a: str, model_b: str, base_tokens: int, growth_tokens_per_turn: int,
                                   output_tokens_per_turn: int, strategy: str = "unbounded",
                                   window_k: int = 20, max_turns: int = 5000) -> int | None:
    """First turn N at which model_b becomes cheaper than model_a under the given context strategy.
    strategy: 'unbounded' (full history) or 'bounded' (uses window_k for both models)."""
    cost_fn = (lambda m, n: bounded_window_cost(m, n, base_tokens, growth_tokens_per_turn, output_tokens_per_turn, window_k)["total"]) \
        if strategy == "bounded" else \
        (lambda m, n: conversation_cost(m, n, base_tokens, growth_tokens_per_turn, output_tokens_per_turn, cached=False)["total"])

    a0, b0 = cost_fn(model_a, 1), cost_fn(model_b, 1)
    if b0 < a0:
        return 1
    for n in range(2, max_turns + 1):
        if cost_fn(model_b, n) < cost_fn(model_a, n):
            return n
    return None
