from economics.inference.cost import conversation_cost, bounded_window_cost, first_crossover_turn


def test_claude_sonnet_5_no_long_context_tier():
    assert first_crossover_turn("claude-sonnet-5", 200, 900) is None


def test_gpt_5_6_sol_crossover_boundary():
    assert first_crossover_turn("gpt-5.6-sol", 200, 900) == 304


def test_gemini_3_1_pro_preview_crossover_boundary():
    assert first_crossover_turn("gemini-3.1-pro-preview", 200, 900) == 224


def test_quadratic_growth_claude_sonnet_5():
    c100 = conversation_cost("claude-sonnet-5", 100, 200, 900, 700, cached=False)["total"]
    c1000 = conversation_cost("claude-sonnet-5", 1000, 200, 900, 700, cached=False)["total"]
    assert c1000 / c100 > 10


def test_reference_values_claude_sonnet_5_no_cache():
    r = conversation_cost("claude-sonnet-5", 1000, 200, 900, 700, cached=False)
    assert abs(r["total"] - 906.50) < 0.01


def test_reference_values_gpt_5_6_sol_no_cache():
    r = conversation_cost("gpt-5.6-sol", 1000, 200, 900, 700, cached=False)
    assert abs(r["total"] - 3451.93) < 0.01


def test_caching_reduces_cost_but_not_below_zero():
    no_cache = conversation_cost("claude-sonnet-5", 1000, 200, 900, 700, cached=False)["total"]
    cached = conversation_cost("claude-sonnet-5", 1000, 200, 900, 700, cached=True)["total"]
    assert 0 < cached < no_cache


def test_bounded_window_beats_unbounded_at_high_n():
    unbounded = conversation_cost("claude-sonnet-5", 1000, 200, 900, 700, cached=False)["total"]
    bounded = bounded_window_cost("claude-sonnet-5", 1000, 200, 900, 700, 20)["total"]
    assert bounded < unbounded


def test_bounded_window_is_linear_not_quadratic():
    b100 = bounded_window_cost("claude-sonnet-5", 100, 200, 900, 700, 20)["total"]
    b1000 = bounded_window_cost("claude-sonnet-5", 1000, 200, 900, 700, 20)["total"]
    assert b1000 / b100 < 15
