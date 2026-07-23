# TurboQuant KV-Cache Contract

TurboQuant is a compressed KV-cache representation, not a weight format.
Supported head sizes are 64, 128, and 256. Key and value bit widths are
independently selected in `[2,8]`. Every scale group contains 32 adjacent head
elements.

Codes are packed as a contiguous least-significant-bit-first stream: element
`i` starts at bit `i * bits`. A row occupies `ceil(head_size * bits / 8)` bytes
and unused high bits in the final byte are zero.

Keys use a per-group FP16-rounded scale and FP16-rounded zero offset. Unsigned
decode is `(code + zero) * scale`. Signed eight-bit keys interpret the byte as
two's-complement before the same formula; other signed widths retain their raw
bit pattern until their format-specific signed decode is selected. The signed
mode and bit width are required metadata.

Values are multiplied by a caller-supplied finite sign vector, transformed by
an unnormalized FWHT, and multiplied by `1/sqrt(head_size)`. Each group is
divided by its FP16-rounded RMS. Codes select from an ascending table of
`2^value_bits` finite centroids, with adjacent midpoints as decision boundaries
and the lower centroid winning equality. Decode reverses the transform and
sign multiplication.

Slot mapping less than zero means skip; non-negative slots must be in range.
Cache metadata includes key/value bits, key signedness, head size, group size,
centroid identity, sign-vector identity, and scale precision. Direct attention
must be numerically equivalent to decode followed by FP32 online softmax within
the quantized tolerance.
