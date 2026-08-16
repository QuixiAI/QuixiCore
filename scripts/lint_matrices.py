#!/usr/bin/env python3
"""Lint matrices/*.md status symbols against registry/status-schema.yaml.

The matrices are hand-edited; a cell symbol outside the shared vocabulary is
either a typo or a status the schema does not define — both drift. Table rows
(lines starting with '|') are scanned for emoji-range codepoints; anything not
in the schema's `symbol:` set or the documented capability-map extensions
fails with file:line.

Stdlib only (the schema is read with a regex, not a YAML parser, to match the
CI environment).
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Local legend extensions documented in matrices/capability-map.md.
ALLOWED_EXTRA = {"\U0001F512"}  # 🔒 capability-gated

EMOJI_RANGES = (
    (0x1F000, 0x1FAFF),
    (0x2600, 0x27BF),
    (0x2B00, 0x2BFF),
)


def emoji_in(text):
    for ch in text:
        cp = ord(ch)
        if any(lo <= cp <= hi for lo, hi in EMOJI_RANGES):
            yield ch


def main():
    schema = (ROOT / "registry" / "status-schema.yaml").read_text()
    allowed = set(re.findall(r'symbol:\s*"(.+?)"', schema)) | ALLOWED_EXTRA
    bad = []
    for md in sorted((ROOT / "matrices").glob("*.md")):
        for n, line in enumerate(md.read_text().splitlines(), 1):
            if not line.lstrip().startswith("|"):
                continue
            for ch in emoji_in(line):
                if ch not in allowed:
                    bad.append(f"{md.relative_to(ROOT)}:{n}: symbol {ch!r} (U+{ord(ch):04X}) not in status vocabulary")
    for b in bad:
        print(b)
    print(f"{'FAIL' if bad else 'OK'}: matrix status symbols ({', '.join(sorted(allowed))} allowed)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
