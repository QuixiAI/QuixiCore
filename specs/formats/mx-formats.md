# MXFP8, MXFP4, and NVFP4 Contract

This specification defines logical row-major microscale representations.
Backend-specific scale swizzles and matrix-instruction tiles are rebuildable
prepared data and must not be serialized as canonical bytes.

## E8M0 scale

E8M0 is an unsigned eight-bit exponent with bias 127. Codes 0 through 254
decode to `2^(code-127)`; code 255 is NaN. It has no zero or infinity value.
QuixiCore producers use round-up scaling: for a non-zero finite block, choose
the smallest representable power of two that prevents finite element overflow.
An all-zero block uses scale code 0 and all-zero element codes; consumers must
therefore avoid inferring non-zero values from the scale alone. Non-finite
input is rejected by canonical packers.

## MXFP8

- One E8M0 scale is shared by each contiguous group of 32 K elements.
- Elements are FP8 E4M3FN bytes in logical K order.
- Reconstruction is `e8m0(scale_code) * e4m3fn(element_code)`.
- The canonical block is one scale byte followed by 32 element bytes.

## MXFP4

- One E8M0 scale is shared by each contiguous group of 32 K elements.
- Elements are FP4 E2M1 nibbles using the packing in `fp4.md`.
- Reconstruction is `e8m0(scale_code) * e2m1(element_code)`.
- The canonical block is one scale byte followed by 16 packed element bytes.

## NVFP4

NVFP4 uses two levels of scaling:

- one positive finite FP32 global scale for the tensor or declared 2-D scale
  domain;
- one unsigned E4M3 local scale per contiguous group of 16 K elements; and
- 16 FP4 E2M1 values, packed low-K nibble first.

The local scale uses the positive E4M3FN magnitude encoding: `0x00` is zero,
codes `0x01` through `0x7e` use E4M3FN positive decode, and `0x7f` is reserved
and must not be emitted. Reconstruction is
`global_scale * local_scale * e2m1(code)`.

For dynamic quantization, the global scale is `tensor_amax / (448 * 6)`.
Each local scale is the nearest-even E4M3FN encoding of
`block_amax / (6 * global_scale)`, saturated to 448. If the complete scale
domain is zero, the global scale and all codes are zero. In 1-D mode each row
has independent local scales. In 2-D mode a local scale is selected over a
declared group of at most 16 adjacent rows and one 16-element K block; the
scale-domain row count is required metadata.

The canonical logical representation stores packed elements, the row-major
local-scale table, the global scale, and the 1-D/2-D scale mode as separate
fields. A GGUF-compatible `block_nvfp4` is a distinct container adapter and
must be normalized before generic NVFP4 APIs are called.

## Arithmetic

Weight-only paths consume FP16, BF16, or FP32 activations. Dual-operand paths
apply each operand's scale before FP32 accumulation. Scale products may be
hoisted per block but may not be rounded to FP16 unless an operation explicitly
defines that behavior. Ragged K is rejected for canonical blocks; importers
must pad explicitly and retain the logical K.
