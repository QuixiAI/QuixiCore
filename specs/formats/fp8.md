# FP8 Contract

This document defines the portable QuixiCore FP8 representation. Backend-
private swizzles and matrix-instruction fragments are derived layouts and are
not serializable formats.

## Scalar encodings

Both encodings use bit 7 as the sign and preserve signed zero on decode.

### E4M3FN

- Bits 6:3 are a four-bit exponent with bias 7; bits 2:0 are the fraction.
- Exponent zero decodes as `(-1)^s * mantissa * 2^-9`.
- Exponents 1 through 14 decode as
  `(-1)^s * (1 + mantissa/8) * 2^(exponent-7)`.
- Exponent 15 and mantissas 0 through 6 are finite. The maximum finite code is
  `0x7e`, which decodes to 448.
- Magnitude code `0x7f` is NaN. E4M3FN has no infinity encoding.

### E5M2

- Bits 6:2 are a five-bit exponent with bias 15; bits 1:0 are the fraction.
- Exponent zero decodes as `(-1)^s * mantissa * 2^-16`.
- Exponents 1 through 30 decode as
  `(-1)^s * (1 + mantissa/4) * 2^(exponent-15)`.
- Exponent 31 with a zero mantissa is infinity; a non-zero mantissa is NaN.
- The maximum finite magnitude code is `0x7b`, which decodes to 57344.

## Conversion

Finite conversion uses round-to-nearest, ties-to-even over the representable
finite values. Positive and negative zero encode as `0x00` and `0x80`.
Finite overflow and input infinity saturate to the same-sign maximum finite
code. A NaN encodes to the canonical positive code `0x7f` for E4M3FN and
`0x7d` for E5M2; decoders must accept every NaN payload.

## Scaled tensors

The canonical logical value is `scale * decode(code)`. Scale tables are
row-major over the unquantized tensor and may use one of these modes:

- tensor: one finite FP32 scale for the tensor;
- row or channel: one finite FP32 scale for each logical row/channel;
- group: one finite FP32 scale per contiguous K group; or
- block: one finite FP32 scale per declared N-by-K tile.

Group and block sizes are required metadata. A zero-valued group uses scale
zero and all-zero codes. Dynamic scales are selected from the maximum finite
magnitude divided by 448 (E4M3FN) or 57344 (E5M2), unless the operation
explicitly requests a power-of-two scale. Static scales are supplied by the
caller and must be finite and non-negative.

Codes are stored in logical row-major order. Scale tables precede neither the
codes nor each other implicitly: serialized containers must carry explicit
offsets and scale mode metadata.

## Arithmetic

W8A16 consumes FP16, BF16, or FP32 activation storage directly. W8A8 consumes
two FP8 operands, which may use different E4M3FN/E5M2 encodings and independent
scale tables. Products and reductions accumulate in FP32. Bias and activation
epilogues observe the FP32 accumulator before output conversion.

Invalid dimensions, absent metadata, negative scales, or non-finite scales are
contract errors. Kernels must not silently reinterpret E4M3FN as E5M2.
