#!/usr/bin/env python3
"""Check or regenerate backend agent docs from the umbrella templates.

Backend AGENTS.md, CLAUDE.md, and .claude/settings.json files are rendered
from docs/templates/ using per-backend values in
docs/templates/agents-params.json. In a rendered AGENTS.md, sections between
`<!-- qx:shared:begin <name> v1 -->` and `<!-- qx:shared:end <name> -->` are
umbrella-owned and must match the template byte-for-byte; sections between
`<!-- qx:backend:begin <name> -->` and `<!-- qx:backend:end <name> -->` are
backend-owned free text whose content is preserved verbatim. CLAUDE.md and
settings.json carry no markers and are compared as whole files.

Usage:
  python3 tools/sync_agent_docs.py [--check] [--diff] [--backend NAME]
  python3 tools/sync_agent_docs.py --write [--backend NAME]

--check (the default) exits 1 and lists every drifted or missing file.
--write regenerates shared blocks in place, preserving backend blocks; when a
target file does not exist or has no markers yet, the full file is generated
with slot content seeded from agents-params.json.
"""

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = ROOT / "docs" / "templates"
AGENTS_TEMPLATE = TEMPLATE_DIR / "backend-AGENTS.md"
CLAUDE_TEMPLATE = TEMPLATE_DIR / "backend-CLAUDE.md"
SETTINGS_TEMPLATE = TEMPLATE_DIR / "backend-claude-settings.json"
PARAMS_FILE = TEMPLATE_DIR / "agents-params.json"

SECTION_RE = re.compile(r"^<!-- qx:section (\S+) -->$")
SLOT_RE = re.compile(r"^<!-- qx:slot (\S+) -->$")
SHARED_BEGIN_RE = re.compile(r"^<!-- qx:shared:begin (\S+) v1 -->$")
SHARED_END_RE = re.compile(r"^<!-- qx:shared:end (\S+) -->$")
BACKEND_BEGIN_RE = re.compile(r"^<!-- qx:backend:begin (\S+) -->$")
BACKEND_END_RE = re.compile(r"^<!-- qx:backend:end (\S+) -->$")
PARAM_RE = re.compile(r"\{\{([a-z_]+)\}\}")


def fail(msg):
    print(f"sync_agent_docs: {msg}", file=sys.stderr)
    sys.exit(2)


def parse_template(path):
    """Return an ordered list of ('shared', name, text) / ('slot', name, None)."""
    segments = []
    current = None
    for lineno, line in enumerate(path.read_text().splitlines(), 1):
        m = SECTION_RE.match(line.strip())
        s = SLOT_RE.match(line.strip())
        if m:
            current = ["shared", m.group(1), []]
            segments.append(current)
        elif s:
            segments.append(["slot", s.group(1), None])
            current = None
        else:
            if current is None:
                if line.strip():
                    fail(f"{path.name}:{lineno}: content outside a qx:section")
                continue
            current[2].append(line)
    out = []
    for kind, name, body in segments:
        if kind == "shared":
            text = "\n".join(body).strip("\n")
            out.append((kind, name, text))
        else:
            out.append((kind, name, None))
    return out


def substitute(text, params, context):
    def repl(m):
        key = m.group(1)
        if key not in params:
            fail(f"{context}: no value for parameter {{{{{key}}}}}")
        return str(params[key])

    return PARAM_RE.sub(repl, text)


def render_agents(segments, backend_params, slot_content):
    """Render a full AGENTS.md from template segments and slot contents."""
    blocks = []
    for kind, name, text in segments:
        if kind == "shared":
            body = substitute(text, backend_params, f"section {name}")
            blocks.append(
                f"<!-- qx:shared:begin {name} v1 -->\n{body}\n<!-- qx:shared:end {name} -->"
            )
        else:
            body = slot_content.get(name, "").strip("\n")
            inner = f"\n{body}\n" if body else "\n"
            blocks.append(
                f"<!-- qx:backend:begin {name} -->{inner}<!-- qx:backend:end {name} -->"
            )
    return "\n\n".join(blocks) + "\n"


def parse_rendered(path):
    """Parse a rendered AGENTS.md into ordered (kind, name, body-text) blocks.

    Returns None if the file has no qx markers at all (pre-template file).
    Fails on unbalanced or interleaved markers or content outside blocks.
    """
    lines = path.read_text().splitlines()
    if not any(SHARED_BEGIN_RE.match(l) or BACKEND_BEGIN_RE.match(l) for l in lines):
        return None
    blocks = []
    current = None  # [kind, name, [lines]]
    for lineno, line in enumerate(lines, 1):
        sb, se = SHARED_BEGIN_RE.match(line), SHARED_END_RE.match(line)
        bb, be = BACKEND_BEGIN_RE.match(line), BACKEND_END_RE.match(line)
        if sb or bb:
            if current is not None:
                fail(f"{path}:{lineno}: nested qx block")
            current = ["shared" if sb else "backend", (sb or bb).group(1), []]
        elif se or be:
            if current is None:
                fail(f"{path}:{lineno}: qx end without begin")
            kind = "shared" if se else "backend"
            name = (se or be).group(1)
            if current[0] != kind or current[1] != name:
                fail(f"{path}:{lineno}: mismatched qx end {kind}/{name}")
            blocks.append((current[0], current[1], "\n".join(current[2]).strip("\n")))
            current = None
        else:
            if current is None:
                if line.strip():
                    fail(f"{path}:{lineno}: content outside qx blocks")
            else:
                current[2].append(line)
    if current is not None:
        fail(f"{path}: unterminated qx block {current[0]}/{current[1]}")
    return blocks


def render_claude(backend_params):
    return substitute(CLAUDE_TEMPLATE.read_text(), backend_params, "CLAUDE template")


def render_settings(backend_params):
    data = json.loads(SETTINGS_TEMPLATE.read_text())
    allow = data["permissions"]["allow"]
    try:
        idx = allow.index("{{settings_allow_extra}}")
    except ValueError:
        fail("settings template lacks the {{settings_allow_extra}} placeholder")
    extras = backend_params.get("settings_allow_extra", [])
    data["permissions"]["allow"] = allow[:idx] + extras + allow[idx + 1 :]
    return json.dumps(data, indent=2) + "\n"


def show_diff(expected, actual, label):
    diff = difflib.unified_diff(
        actual.splitlines(keepends=True),
        expected.splitlines(keepends=True),
        fromfile=f"{label} (current)",
        tofile=f"{label} (expected)",
    )
    sys.stdout.writelines(diff)


def process_backend(name, cfg, segments, write, diff):
    """Returns a list of problem strings (empty = clean)."""
    problems = []
    repo = ROOT / cfg["path"]
    if not repo.is_dir():
        return [f"{name}: sibling checkout {cfg['path']} not found"]

    # AGENTS.md
    agents_path = repo / "AGENTS.md"
    slot_names = [n for kind, n, _ in segments if kind == "slot"]
    existing_slots = {}
    parsed = parse_rendered(agents_path) if agents_path.exists() else None
    if parsed is not None:
        expected_seq = [(k, n) for k, n, _ in segments]
        actual_seq = [
            ("shared" if k == "shared" else "slot", n) for k, n, _ in parsed
        ]
        if actual_seq != expected_seq:
            problems.append(f"{name}/AGENTS.md: block sequence differs from template")
        for kind, bname, body in parsed:
            if kind == "backend":
                existing_slots[bname] = body
    seed_slots = dict(cfg.get("slots", {}))
    seed_slots.update(existing_slots)
    expected_agents = render_agents(segments, cfg, {n: seed_slots.get(n, "") for n in slot_names})
    actual_agents = agents_path.read_text() if agents_path.exists() else ""
    if actual_agents != expected_agents:
        problems.append(
            f"{name}/AGENTS.md: "
            + ("missing" if not agents_path.exists() else "shared sections drifted or markers absent")
        )
        if diff:
            show_diff(expected_agents, actual_agents, f"{cfg['path']}/AGENTS.md")
        if write:
            agents_path.write_text(expected_agents)

    # CLAUDE.md
    claude_path = repo / "CLAUDE.md"
    expected_claude = render_claude(cfg)
    actual_claude = claude_path.read_text() if claude_path.exists() else ""
    if actual_claude != expected_claude:
        problems.append(f"{name}/CLAUDE.md: " + ("missing" if not claude_path.exists() else "drifted"))
        if diff:
            show_diff(expected_claude, actual_claude, f"{cfg['path']}/CLAUDE.md")
        if write:
            claude_path.write_text(expected_claude)

    # .claude/settings.json
    settings_path = repo / ".claude" / "settings.json"
    expected_settings = render_settings(cfg)
    actual_settings = settings_path.read_text() if settings_path.exists() else ""
    if actual_settings != expected_settings:
        problems.append(
            f"{name}/.claude/settings.json: "
            + ("missing" if not settings_path.exists() else "drifted")
        )
        if diff:
            show_diff(expected_settings, actual_settings, f"{cfg['path']}/.claude/settings.json")
        if write:
            settings_path.parent.mkdir(exist_ok=True)
            settings_path.write_text(expected_settings)

    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="verify (default)")
    ap.add_argument("--write", action="store_true", help="regenerate in place")
    ap.add_argument("--diff", action="store_true", help="show unified diffs")
    ap.add_argument("--backend", help="restrict to one backend name")
    args = ap.parse_args()
    if args.check and args.write:
        fail("--check and --write are mutually exclusive")

    params = json.loads(PARAMS_FILE.read_text())["backends"]
    if args.backend:
        if args.backend not in params:
            fail(f"unknown backend {args.backend!r} (have: {', '.join(sorted(params))})")
        params = {args.backend: params[args.backend]}

    segments = parse_template(AGENTS_TEMPLATE)
    all_problems = []
    for name, cfg in params.items():
        all_problems.extend(process_backend(name, cfg, segments, args.write, args.diff))

    if all_problems:
        verb = "rewrote" if args.write else "drift in"
        for p in all_problems:
            print(f"{verb}: {p}")
        if args.write:
            print(f"sync_agent_docs: rewrote {len(all_problems)} file(s); re-run --check to confirm")
            return 0
        return 1
    print(f"sync_agent_docs: {len(params)} backend(s) synchronized")
    return 0


if __name__ == "__main__":
    sys.exit(main())
