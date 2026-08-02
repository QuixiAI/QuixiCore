#!/usr/bin/env python3
"""Generate the canonical quant-format test vectors.

These are the contract between the six backend repos. A format is specified in
prose in `specs/formats/`, but prose is not checkable: this repo already carried
an E8M0 spec saying code 0 decodes to 2^-127, and seven ROCm kernel families
decoded it to +0.0 anyway, for years, because nothing compared them.

Every vector here is derived from the spec text, not from any implementation, so
a backend that disagrees is wrong by construction rather than by argument. The
edge codes are the point -- 0, 254 and 255 are where implementations diverge and
where ordinary data never goes.

Values are emitted as both a float and its exact IEEE-754 bit pattern; backends
should compare bits, since 2^-127 is subnormal and a permissive comparison will
happily call it zero.

    python3 scripts/gen_quant_vectors.py          # write test-vectors/quant/
    python3 scripts/gen_quant_vectors.py --check  # verify committed files match
"""

from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "test-vectors" / "quant"


def bits(x: float) -> str:
    return f"0x{struct.unpack('<I', struct.pack('<f', x))[0]:08x}"


# --------------------------------------------------------------------- E8M0
def e8m0() -> dict:
    """specs/formats/mx-formats.md: codes 0..254 -> 2^(code-127), 255 is NaN."""
    cases = []
    for code in (0, 1, 2, 126, 127, 128, 253, 254):
        v = math.ldexp(1.0, code - 127)
        cases.append({"code": code, "value": repr(v), "bits": bits(v)})
    cases.append({"code": 255, "value": "nan", "bits": None,
                  "note": "NaN; the format has no infinity"})
    return {
        "format": "e8m0",
        "spec": "specs/formats/mx-formats.md",
        "note": (
            "Code 0 is the divergence that matters: it is 2^-127, a SUBNORMAL "
            "float, not zero and not the smallest normal. A decoder using "
            "__uint_as_float(code << 23) returns +0.0 here and +Inf at 255. "
            "That shortcut is sound only under the producer contract (an "
            "all-zero block carries code 0 with all-zero elements), so a "
            "backend may ship it -- but it must not claim conformance."
        ),
        "cases": cases,
    }


def e8m0_gguf() -> dict:
    """ggml's E8M0, which is NOT OCP MX and must not be checked against it.

    ggml decodes by bit-punning the code into the fp32 exponent field with no
    special cases, so codes 0..254 agree with MX exactly and code 255 comes out
    +Inf rather than NaN. Matching this is a requirement, not a defect: the
    point is to read the GGUF files that exist. ggml's quantizer does not emit
    255, so the divergence is unreachable from conformant data -- but a decoder
    shared with the MX path would be wrong for one of them.
    """
    cases = []
    for code in (0, 1, 126, 127, 254):
        v = math.ldexp(1.0, code - 127)
        cases.append({"code": code, "value": repr(v), "bits": bits(v)})
    cases.append({"code": 255, "value": "inf", "bits": "0x7f800000",
                  "note": "ggml bit-puns with no special case; MX says NaN"})
    return {
        "format": "e8m0_gguf",
        "spec": "specs/formats/gguf.md",
        "note": (
            "Differs from e8m0 only at code 255. Kept as a separate contract "
            "so a backend cannot satisfy one by breaking the other."
        ),
        "cases": cases,
    }


# --------------------------------------------------------------------- E2M1
E2M1 = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0]


def e2m1() -> dict:
    """specs/formats/fp4.md: sign bit plus a 3-bit magnitude codebook."""
    cases = []
    for code in range(16):
        v = E2M1[code & 7] * (-1.0 if code & 8 else 1.0)
        cases.append({"code": code, "value": repr(v), "bits": bits(v)})
    return {
        "format": "e2m1",
        "spec": "specs/formats/fp4.md",
        "note": "Code 8 is negative zero; compare bits, not values.",
        "cases": cases,
    }


# -------------------------------------------------------------------- MXFP4
def mxfp4() -> dict:
    """One E8M0 scale byte then 16 packed nibble bytes, 32 elements."""
    blocks = []
    for name, scale, nibbles in (
        ("unit_scale_ramp", 127, [(i % 8) | (((i + 1) % 8) << 4) for i in range(16)]),
        ("all_zero_block", 0, [0] * 16),
        ("negative_half", 126, [0x8 | (0x9 << 4)] * 16),
    ):
        s = math.ldexp(1.0, scale - 127)
        vals = []
        for b in nibbles:
            vals.append(s * E2M1[b & 7] * (-1.0 if b & 8 else 1.0))
        for b in nibbles:
            hi = b >> 4
            vals.append(s * E2M1[hi & 7] * (-1.0 if hi & 8 else 1.0))
        blocks.append({
            "name": name,
            "scale_code": scale,
            "element_bytes": nibbles,
            "values": [repr(v) for v in vals],
            "bits": [bits(v) for v in vals],
        })
    return {
        "format": "mxfp4",
        "spec": "specs/formats/mx-formats.md",
        "note": (
            "Element order: the low nibble of byte i is element i, the high "
            "nibble is element i+16. Swapping the halves leaves the value "
            "multiset and the block norm almost unchanged, so a norm-only "
            "check passes a wrong decoder -- these vectors pin positions. "
            "`all_zero_block` is the producer contract from mx-formats.md and "
            "is the case where the fast and conformant E8M0 decoders agree."
        ),
        "blocks": blocks,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="verify committed vectors match this generator")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    rc = 0
    for doc in (e8m0(), e8m0_gguf(), e2m1(), mxfp4()):
        path = OUT / f"{doc['format']}.json"
        text = json.dumps(doc, indent=2) + "\n"
        if args.check:
            have = path.read_text() if path.exists() else ""
            if have != text:
                print(f"stale or missing: {path.relative_to(ROOT)}")
                rc = 1
        else:
            path.write_text(text)
            print(f"wrote {path.relative_to(ROOT)}")
    if args.check and rc == 0:
        print("quant vectors: up to date")
    return rc


if __name__ == "__main__":
    sys.exit(main())
