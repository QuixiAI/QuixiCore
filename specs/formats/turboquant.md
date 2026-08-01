# TurboQuant KV-Cache Contract

TurboQuant is a compressed KV-cache representation, not a weight format. It
derives from Zandieh et al., "TurboQuant: Online Vector Quantization with
Near-optimal Distortion Rate" (arXiv:2504.19874, ICLR 2026).

Format version 2. Version 1 gave values the rotated Lloyd-Max path and keys
plain uniform quantization, inverting the algorithm's tensor roles; caches
written under version 1 are not readable under this contract. Implementations
record the format version in cache metadata and refuse a version they do not
implement.

## Tensor roles

Attention scores are inner products between a query and a key, so key fidelity
governs the score distribution and keys take the rotated Lloyd-Max path. The
attention output is a convex combination of values, a reconstruction rather than
an inner product, so values take uniform quantization. Assigning the rotated path
to values instead is the version 1 defect.

Supported head sizes are 64, 128, and 256. Key and value bit widths are
independently selected in `[2,8]`. Every scale group contains 32 adjacent head
elements.

Codes are packed as a contiguous least-significant-bit-first stream: element `i`
starts at bit `i * bits`. A row occupies `ceil(head_size * bits / 8)` bytes and
unused high bits in the final byte are zero.

## Keys

Keys are multiplied by a caller-supplied finite sign vector, transformed by an
unnormalized FWHT, and multiplied by `1/sqrt(head_size)`. The rotation
concentrates the coordinate distribution, which is what admits a fixed scalar
quantizer. Each group is divided by its FP16-rounded RMS. Codes select from an
ascending table of `2^key_bits` finite centroids, with adjacent midpoints as
decision boundaries and the lower centroid winning equality. Decode reverses the
transform and sign multiplication.

Key bit width eight selects an unrotated FP8 key path instead, in which the
stored byte is an FP8 code and no sign vector, transform, or centroid table
applies. The selected key path is required metadata.

Norm correction is an optional key-side decode step that renormalizes the
decoded centroid vector to unit norm before the inverse transform, compensating
quantization-induced norm distortion. It changes decode only, never the stored
codes. Whether it is enabled is required metadata.

The residual QJL sign bit that the source paper adds for an unbiased
inner-product estimator is not part of this contract; independent evaluations
report it amplifies variance through softmax. It may return as a versioned
extension. Implementations do not emit it unless a later version defines it, and
record its absence.

## Values

Values use per-group uniform quantization with an FP16-rounded scale and
FP16-rounded zero offset. Unsigned decode is `(code + zero) * scale`. Signed
eight-bit values interpret the byte as two's-complement before the same formula;
other signed widths retain their raw bit pattern until their format-specific
signed decode is selected. The signed mode and bit width are required metadata.
Values are not rotated and use no sign vector or centroid table.

## Cache and attention

Slot mapping less than zero means skip; non-negative slots must be in range.
Cache metadata includes format version, key/value bits, key path, value
signedness, head size, group size, centroid identity, sign-vector identity,
norm-correction state, and scale precision. Direct attention must be numerically
equivalent to decode followed by FP32 online softmax within the quantized
tolerance.

Because keys are the rotated tensor, an attention implementation may hold the
query in the rotated domain and score against undecoded key codes, deferring the
inverse transform. Values, being unrotated, decode directly into the weighted
sum.
