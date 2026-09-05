from economics.infrastructure.cost import supabase_cost, upstash_cost, resend_cost


def test_supabase_free_tier():
    assert supabase_cost(50000) == 0.0
    assert supabase_cost(50001) == 25.0


def test_supabase_monotonic_non_decreasing():
    values = [supabase_cost(m) for m in [1000, 50000, 75000, 100000, 250000, 1000000]]
    assert all(values[i] <= values[i + 1] for i in range(len(values) - 1))


def test_supabase_1m_mau_matches_verified_reference():
    assert abs(supabase_cost(1000000) - 2950.0) < 0.01


def test_upstash_prefers_fixed_when_cheaper():
    # 50k MAU * 150 commands/MAU = 7.5M commands/month -> PAYG $15, Fixed 250MB $10
    result = upstash_cost(50000 * 150, storage_mb_estimate=250)
    assert result["plan"] == "fixed_250mb"
    assert result["cost"] == 10


def test_upstash_prefers_payg_for_bursty_low_volume():
    result = upstash_cost(600000, storage_mb_estimate=250)  # just over free tier
    assert result["cost"] == result["payg_cost"]


def test_resend_pro_beats_scale_at_100k():
    # Both sell 100k; Pro should win ($35 vs $90)
    result = resend_cost(100000)
    assert result["plan"] == "pro_100k"
    assert result["cost"] == 35.0


def test_resend_scale_wins_past_true_crossover():
    # Verified crossover is ~455-460k, not the commonly-assumed 200k
    below = resend_cost(400000)
    above = resend_cost(500000)
    assert "pro" in below["plan"]
    assert "scale" in above["plan"]


def test_resend_monotonic_non_decreasing():
    values = [resend_cost(e)["cost"] for e in [3000, 50000, 100000, 300000, 1000000, 2500000]]
    assert all(values[i] <= values[i + 1] for i in range(len(values) - 1))
