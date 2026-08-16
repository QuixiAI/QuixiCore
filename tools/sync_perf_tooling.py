#!/usr/bin/env python3
"""Distribute the shared perf tooling to the sibling backend checkouts, or
verify (--check) that the committed copies still match the canonicals.

Canonical files (edit these, never the copies):
  tools/templates/run_bench_core.sh  -> <backend>/perf/harness/run_bench_core.sh
  scripts/perf_diff.py               -> <backend>/perf/harness/perf_diff.py

The copies are committed in each backend repo so a standalone clone works;
six hand-maintained variants of the guard logic is exactly the drift this
repo's sync pattern (tools/sync_kernel_contract.py) exists to prevent.

Usage:
  python3 tools/sync_perf_tooling.py           # write copies into all six
  python3 tools/sync_perf_tooling.py --check   # verify, exit 1 on drift
"""

import os
import stat
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BACKENDS = {
    "metal": "QuixiCore-Metal",
    "cuda": "QuixiCore-CUDA",
    "rocm": "QuixiCore-ROCm",
    "xpu": "QuixiCore-XPU",
    "gaudi": "QuixiCore-Gaudi",
    "cpu": "QuixiCore-CPU",
}

FILES = {
    os.path.join(ROOT, "tools", "templates", "run_bench_core.sh"): "run_bench_core.sh",
    os.path.join(ROOT, "scripts", "perf_diff.py"): "perf_diff.py",
}


def main():
    check = "--check" in sys.argv[1:]
    problems = []
    written = 0

    for name, dirname in BACKENDS.items():
        repo = os.path.join(ROOT, dirname)
        if not os.path.isdir(repo):
            problems.append(f"{name}: sibling checkout {dirname} not found")
            continue
        harness = os.path.join(repo, "perf", "harness")
        for src, base in FILES.items():
            dst = os.path.join(harness, base)
            with open(src) as f:
                expected = f.read()
            actual = None
            if os.path.exists(dst):
                with open(dst) as f:
                    actual = f.read()
            if actual == expected:
                continue
            if check:
                problems.append(
                    f"{name}: perf/harness/{base} "
                    + ("missing" if actual is None else "drifted")
                )
            else:
                os.makedirs(harness, exist_ok=True)
                with open(dst, "w") as f:
                    f.write(expected)
                os.chmod(dst, os.stat(dst).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                written += 1
                print(f"wrote {dirname}/perf/harness/{base}")

    if problems:
        for p in problems:
            print(f"drift: {p}")
        return 1
    print(
        f"perf tooling is synchronized ({len(BACKENDS)} backends)" if check
        else f"perf tooling synced ({written} file(s) written)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
