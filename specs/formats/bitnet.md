# BitNet b1.58 and a4.8 Contract

## Canonical ternary weight block

The portable block represents 32 K-contiguous weights in 10 bytes:

```text
offset  size  meaning
0       2     little-endian IEEE FP16 scale
2       8     32 two-bit codes, four per byte
```

Within each code byte, the lower-K element occupies the least-significant two
bits. Codes decode as `0 -> -1`, `1 -> 0`, and `2 -> +1`; code 3 is reserved
and rejected by checked importers. Reconstruction is `fp16_scale * ternary`.
K must be divisible by 32. Products accumulate in signed INT32 when paired
with integer activations and are converted to FP32 before applying scales.

Canonical quantization uses a finite non-negative scale for each declared
`group_k`, with `group_k` divisible by 32. Zero groups emit scale zero and code
1. The deterministic nearest ternary code is selected after division by the
group scale; exact half-way cases select zero.

I2_S, TL1, and TL2 are importer or CPU-prepared layouts. They do not replace
the canonical block and must carry their source revision and transformation
version.

## b1.58 activation contract

The default b1.58 projection dynamically quantizes each activation row to
signed INT8 using `scale = max(abs(x))/127`, round-to-nearest-even, and clamp
to `[-127,127]`. A zero row has scale zero and codes zero. The integer dot is
rescaled by the activation scale and each ternary weight-block scale.

## a4.8 activation contract

a4.8 preserves the same canonical ternary weights and adds an explicit
activation policy descriptor:

- layer input: signed INT4 or FP4 E2M1, including group size and scale mode;
- intermediate: signed INT8 plus a bit mask or sorted compact index list;
- sparsity threshold: finite FP32, with equality retained; and
- logical K: retained independently from prepared padding.

INT4 uses the canonical two's-complement packing in `integer.md`; FP4 uses
`fp4.md`. Compact indices are strictly increasing unsigned 32-bit positions.
An absent element is numerically zero. The sparse dot accumulates in INT32 and
applies FP32 scales once per activation/weight group intersection.

## Cache extension

The optional a4.8 KV3 cache stores three-bit codes least-significant-bit first,
one FP16 or FP32 scale per declared group, and an explicit signedness and
zero-point mode. KV3 support is a separate cache capability; b1.58 or a4.8
weight support does not imply it.
