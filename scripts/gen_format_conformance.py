#!/usr/bin/env python3
"""Generate the test-emitted section of matrices/format-conformance.md.

Backends' conformance tests print `QC-CONFORMANCE {json}` lines (contract in
docs/correctness.md) that are captured into each backend repo as
`.quixicore/conformance.jsonl`. Those snapshots are mirrored into
`matrices/conformance-data/<backend>.jsonl` here, and this script rewrites
only the marked block in matrices/format-conformance.md from them. The
hand-written per-format sections (which carry edge-code detail) stay manual.

Usage:
  gen_format_conformance.py             # rewrite the generated block in place
  gen_format_conformance.py --check     # regenerate and diff; exit 1 if stale
  gen_format_conformance.py --refresh   # first re-copy sibling snapshots into
                                        # matrices/conformance-data/ (local
                                        # checkouts only), then rewrite; with
                                        # --check, fail if mirrors drifted

Stdlib only.
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "matrices" / "conformance-data"
TARGET = ROOT / "matrices" / "format-conformance.md"
BEGIN = "<!-- BEGIN GENERATED: conformance -->"
END = "<!-- END GENERATED -->"

BACKEND_DIRS = {
    "metal": "QuixiCore-Metal", "cuda": "QuixiCore-CUDA", "rocm": "QuixiCore-ROCm",
    "xpu": "QuixiCore-XPU", "gaudi": "QuixiCore-Gaudi", "cpu": "QuixiCore-CPU",
}


def build_block():
    rows = []
    for f in sorted(DATA.glob("*.jsonl")):
        for n, line in enumerate(f.read_text().splitlines(), 1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                sys.exit(f"{f}:{n}: bad JSON ({e})")
            rows.append(rec)
    lines = [
        BEGIN,
        "",
        "## Test-emitted conformance (generated)",
        "",
        "Assembled from each backend's committed `.quixicore/conformance.jsonl`",
        "snapshot (mirrored under `matrices/conformance-data/`); regenerate with",
        "`python3 scripts/gen_format_conformance.py`. Backends without a row have",
        "no snapshot yet — that means unchecked, not conformant.",
        "",
        "| Backend | Format | Decoder | Cases | Failed | Verdict |",
        "|---|---|---|---:|---:|---|",
    ]
    for rec in sorted(rows, key=lambda r: (r.get("backend", ""), r.get("format", ""), r.get("decoder", ""))):
        note = f" — {rec['note']}" if rec.get("note") else ""
        lines.append(
            f"| {rec.get('backend','?')} | `{rec.get('format','?')}` | "
            f"`{rec.get('decoder','?')}` | {rec.get('cases','?')} | "
            f"{rec.get('failed','?')} | {rec.get('verdict','?')}{note} |"
        )
    if not rows:
        lines.append("| — | — | — | — | — | no snapshots committed yet |")
    lines += ["", END]
    return "\n".join(lines)


def splice(text, block):
    if BEGIN in text:
        pre = text[: text.index(BEGIN)]
        post = text[text.index(END) + len(END):]
        return pre + block + post
    # first insertion: before the "## Making this generated" section
    anchor = "## Making this generated"
    if anchor not in text:
        sys.exit(f"{TARGET}: no {BEGIN} block and no insertion anchor")
    i = text.index(anchor)
    return text[:i] + block + "\n\n" + text[i:]


def refresh():
    drifted = []
    DATA.mkdir(exist_ok=True)
    for backend, dirname in BACKEND_DIRS.items():
        src = ROOT / dirname / ".quixicore" / "conformance.jsonl"
        dst = DATA / f"{backend}.jsonl"
        if not src.exists():
            continue
        content = src.read_text()
        if not dst.exists() or dst.read_text() != content:
            drifted.append(str(dst.relative_to(ROOT)))
            dst.write_text(content)
    return drifted


def main():
    check = "--check" in sys.argv
    do_refresh = "--refresh" in sys.argv
    drifted_mirrors = refresh() if do_refresh else []
    block = build_block()
    current = TARGET.read_text()
    updated = splice(current, block)
    stale = updated != current
    if check:
        problems = drifted_mirrors + (["matrices/format-conformance.md (generated block)"] if stale else [])
        if problems:
            for p in problems:
                print(f"stale: {p}")
            print("FAIL: format conformance (run scripts/gen_format_conformance.py)")
            return 1
        print("OK: format conformance table matches the committed snapshots")
        return 0
    if stale:
        TARGET.write_text(updated)
        print(f"rewrote generated block in {TARGET.relative_to(ROOT)}")
    else:
        print("generated block already up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
