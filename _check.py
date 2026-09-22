"""Small self-check helper supplied with the course starter files."""
import importlib.util
import pathlib
import sys
import traceback


class Checker:
    def __init__(self, title, target_default):
        self.title = title
        self.target = sys.argv[1] if len(sys.argv) > 1 else target_default
        self.results = []

    def load(self, caller_file):
        path = pathlib.Path(caller_file).parent / self.target
        spec = importlib.util.spec_from_file_location("submission", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def check(self, name, fn, expected, tol=0.01, note=""):
        try:
            got = fn()
            ok = bool(abs(float(got) - float(expected)) <= tol)
            detail = f"got {float(got):.6g}, expected {float(expected):.6g}"
        except Exception:
            ok = False
            detail = traceback.format_exc().strip().split("\n")[-1]
        self.results.append((name, ok, detail, note))

    def report(self):
        for name, ok, detail, note in self.results:
            print(f"  {'pass' if ok else 'FAIL'}  {name}")
            if not ok:
                print(f"        {detail}\n        {note}")
        passed = sum(ok for _, ok, _, _ in self.results)
        print(f"\n{passed} of {len(self.results)} checks pass")
        return 0 if passed == len(self.results) else 1
