# Checkpoint Quantization Scheme Normalization

AWQ, GPTQ, AutoRound, and SmoothQuant are checkpoint-production schemes, not
new arithmetic element types. Importers normalize their fields to canonical
QuixiCore layouts before CPU preparation.

| Scheme | Required source metadata | Canonical target |
|---|---|---|
| AWQ | `qweight`, `qzeros`, scales, group size, source word width, transpose and nibble order | affine U4 |
| GPTQ | packed weights, scales, optional packed zeros, `g_idx`, `desc_act`, group size, GPTQ/GPTQ-v2 zero convention | symmetric or affine U4 plus optional act-order map |
| AutoRound | target format name, bits, group size, symmetry, scale/zero fields, per-layer override | the named U4, FP8, MXFP4, MXFP8, or NVFP4 layout |
| SmoothQuant | signed INT8 weights, per-channel weight scales, activation scale policy, optional activation zero point | W8A8 symmetric or affine metadata |

Importers must declare the source integer word endianness and packing order.
Act-order maps are permutations from packed K position to logical activation K
position. Duplicate, missing, or out-of-range indices are invalid. No importer
may infer a zero-point convention solely from tensor shape.

Importer output is deterministic. Golden checkpoint fragments must check both
canonical bytes and dequantized values. Scheme names remain provenance in
metadata but do not force scheme-specific GEMV/GEMM entry points.
