# FP4 E2M1 Contract

QuixiCore FP4 uses the OCP E2M1 finite encoding. Accelerator-private nibble
swizzles are prepared layouts, not portable serialization.

## Encoding

Bit 3 is the sign. The low three-bit magnitude codes decode as:

| Code | Value |
|---:|---:|
| 0 | 0 |
| 1 | 0.5 |
| 2 | 1 |
| 3 | 1.5 |
| 4 | 2 |
| 5 | 3 |
| 6 | 4 |
| 7 | 6 |

The sign is applied after magnitude decode, so `0x8` is negative zero. There
are no NaN or infinity encodings.

Finite conversion uses round-to-nearest, ties-to-even, with the low magnitude
code bit as the tie parity bit. Overflow and infinity saturate to magnitude 6.
NaN converts to positive zero. Exact reproducibility requires callers to reject
NaN before quantization when NaN-to-zero is not acceptable.

## Packing and scaling

Two adjacent logical K elements share one byte. The lower-K element occupies
the low nibble and the next element occupies the high nibble. K must be even;
MXFP4 and NVFP4 impose stronger block constraints in `mx-formats.md`.

A scaled FP4 value is `scale * e2m1(code)`. A zero block has scale zero and
zero codes. Standalone block FP4 carries an explicit FP16 or FP32 scale selected
by the enclosing format descriptor. Products and reductions accumulate in
FP32.
