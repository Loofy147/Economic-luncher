"""Generic threshold / regime-crossing primitives, shared by infra and inference cost models."""
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class Regime:
    """A priced regime: applies while `metric <= upper_bound`."""
    upper_bound: float
    label: str


def active_regime(regimes: list, metric_value: float) -> Regime:
    for r in sorted(regimes, key=lambda x: x.upper_bound):
        if metric_value <= r.upper_bound:
            return r
    return regimes[-1]


def distance_to_next_regime(regimes: list, metric_value: float) -> Optional[float]:
    """How much further `metric_value` can grow before the priced regime changes."""
    current = active_regime(regimes, metric_value)
    if current.upper_bound == float("inf"):
        return None
    return current.upper_bound - metric_value
