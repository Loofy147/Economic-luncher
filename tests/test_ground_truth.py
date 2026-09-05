import json
from pathlib import Path

from economics.infrastructure.cost import resend_cost, upstash_cost
from economics.pricing.loader import load_model_pricing

ROOT = Path(__file__).resolve().parents[1]


def test_google_uses_canonical_model_ids():
    cfg = json.loads((ROOT / "configs/vendors/google.json").read_text())
    assert "gemini-3.1-pro-preview" in cfg["models"]
    assert "gemini-3-flash-preview" in cfg["models"]
    assert "gemini-3.8-flash" not in cfg["models"]
    assert "gemini-3.1-pro" not in cfg["models"]


def test_google_loader_resolves_canonical_id_only():
    model = load_model_pricing("gemini-3.1-pro-preview")
    assert model["context_window"] == 1_000_000
    assert model["long_context_threshold_tokens"] == 200_000


def test_resend_price_crossover_is_derived_not_hardcoded():
    # Under the versioned tiers, Pro 100K costs $350 at 450K emails including
    # overage; Scale 500K is also $350. At 451K, Scale is strictly cheaper.
    tie = resend_cost(450_000)
    first_scale_advantage = resend_cost(451_000)
    assert tie["cost"] == 350.0
    assert "pro" in tie["plan"]
    assert "scale" in first_scale_advantage["plan"]
    assert first_scale_advantage["cost"] == 350.0


def test_upstash_fixed_vs_payg_is_workload_dependent():
    steady = upstash_cost(7_500_000, storage_mb_estimate=250)
    assert steady["plan"] == "fixed_250mb"
    assert steady["cost"] == 10.0

    variable = upstash_cost(600_000, storage_mb_estimate=250)
    assert variable["plan"] == "payg"
    assert variable["cost"] == 1.2


def test_snapshot_is_explicitly_partial_until_all_semantics_are_verified():
    snapshot = json.loads(
        (ROOT / "research/pricing_snapshots/2026-09-05.json").read_text()
    )
    assert snapshot["status"] == "verified_partial"
    openai = next(x for x in snapshot["entries"] if x["vendor"] == "openai")
    assert openai["status"] == "verified_with_semantics_caveat"
