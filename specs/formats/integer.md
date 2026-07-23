# Integer Quantization Contract

## Signed INT4

Signed INT4 codes use two's-complement values `[-8,7]`. Two adjacent K values
share a byte, lower-K in the low nibble. Reconstruction is `scale * code`.
Canonical symmetric producers use `scale = max(abs(x))/7`, round-to-nearest-
even, and clamp to `[-8,7]`; a zero group emits zero scale and codes.

## Affine U4

Affine U4 codes are integers `[0,15]`, packed lower-K nibble first.
Reconstruction is `scale * (code - zero_point)`. The scale is positive and
finite for a non-zero-range group. The canonical zero point is FP32 so AWQ
artifacts with a fractional dequantization offset can be represented without
loss; integer-only kernels may prepare an equivalent integer zero point plus a
correction term. Group size, scale precision, and zero-point precision are
mandatory metadata.

## Signed INT8

Signed INT8 codes are bytes interpreted as two's-complement. Symmetric
producers use range `[-127,127]`, `scale = max(abs(x))/127`, and zero point 0.
Affine producers use `[-128,127]` and reconstruct
`scale * (code - zero_point)`. Per-row, per-channel, and per-group scale modes
are distinct and must be declared.

W8A8 and W4A8 asymmetric kernels additionally receive the relevant weight row
sum so zero-point correction is algebraically equivalent to direct decode.
Products accumulate in INT32; scale application and epilogues use FP32.

## Group and padding rules

Groups are contiguous along K. Canonical tensors reject a non-divisible K.
Importers may append explicit zero codes for padding but must retain logical K
as metadata so padding never contributes to public output.
