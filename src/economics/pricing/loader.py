"""Loads normalized vendor/workload/scenario configs from configs/."""
import json
import os

_CONFIG_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "configs"))


def _load(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def load_vendor(name: str) -> dict:
    return _load(os.path.join(_CONFIG_ROOT, "vendors", f"{name}.json"))


def load_workload(name: str) -> dict:
    return _load(os.path.join(_CONFIG_ROOT, "workloads", f"{name}.json"))


def load_scenario(name: str) -> dict:
    return _load(os.path.join(_CONFIG_ROOT, "scenarios", f"{name}.json"))


def load_model_pricing(model_key: str) -> dict:
    """Finds a model's pricing block across all AI provider vendor configs."""
    for vendor_name in ("anthropic", "openai", "google"):
        vendor = load_vendor(vendor_name)
        models = vendor.get("models", {})
        if model_key in models:
            entry = dict(models[model_key])
            entry["_vendor"] = vendor_name
            return entry
    raise KeyError(f"model '{model_key}' not found in any AI provider config")


def all_model_keys() -> list:
    keys = []
    for vendor_name in ("anthropic", "openai", "google"):
        keys.extend(load_vendor(vendor_name).get("models", {}).keys())
    return keys
