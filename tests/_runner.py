"""Minimal dependency-free test runner (network is unavailable in this environment for `pip install pytest`).
Real pytest will pick up these same test_*.py files unmodified once run in an environment with pytest installed."""
import sys, os, importlib, traceback

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src")))
sys.path.insert(0, os.path.dirname(__file__))

test_files = [f[:-3] for f in os.listdir(os.path.dirname(__file__)) if f.startswith("test_") and f.endswith(".py")]

passed, failed = 0, 0
for modname in sorted(test_files):
    mod = importlib.import_module(modname)
    for name in sorted(dir(mod)):
        if name.startswith("test_"):
            fn = getattr(mod, name)
            try:
                fn()
                print(f"PASS  {modname}.{name}")
                passed += 1
            except Exception as e:
                print(f"FAIL  {modname}.{name}  ->  {e}")
                traceback.print_exc()
                failed += 1

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
