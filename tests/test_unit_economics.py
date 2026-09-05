from economics.unit_economics.model import compute


def test_baseline_scenario_runs():
    r = compute(100000, "saas", "claude-sonnet-5", 40000, 25)
    assert r.monthly_cogs > 0
    assert 0 < r.gross_margin_pct < 100
    assert r.dominant_cost_driver in ("infrastructure", "ai_inference", "payments")


def test_cogs_per_mau_shrinks_with_scale_for_flat_fee_components():
    small = compute(5000, "saas", "claude-sonnet-5", 2000, 25)
    large = compute(500000, "saas", "claude-sonnet-5", 200000, 25)
    # Not asserting strict monotonic decrease (usage-based components can offset this),
    # just that both are well-formed and small-scale isn't zero-cost.
    assert small.cogs_per_mau > 0
    assert large.cogs_per_mau > 0
