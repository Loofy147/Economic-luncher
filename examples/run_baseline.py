"""Run: python examples/run_baseline.py [scenario_name]
Prints the full structured report for a scenario in configs/scenarios/."""
import sys, os, json

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src")))
from economics.reporting.report import build_report

if __name__ == "__main__":
    scenario = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    print(json.dumps(build_report(scenario), indent=2))
