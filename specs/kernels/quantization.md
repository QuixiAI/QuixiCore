# Quantization Kernel Contract

This specification covers quantized GEMV/GEMM, activation quantization,
projection fusions, packed serving operations, and compressed-cache consumers.
Format bytes and reconstruction rules live under `specs/formats/`.

## Common matrix semantics

Packed weights have logical shape `[N,K]`, activations `[M,K]`, and output
`[M,N]`:

```text
Y[m,n] = sum(k, dequant(W[n,k]) * dequant_or_load(X[m,k]))
```

GEMV is the `M=1` case. W8A16 accepts FP16, BF16, or FP32 activation storage.
W4A8/W8A8 and W4A4 consume the declared canonical activation packet. Products
accumulate in INT32 where both operands are integer and otherwise in FP32;
scale application and cross-group reduction are FP32. Output is FP32 unless an
operation explicitly requests final FP16/BF16 conversion.

Logical dimensions exclude explicit importer padding. A backend may prepare a
different cache- or ISA-oriented layout but must retain canonical bytes and
produce the same logical result.

## Metadata

Every call or packed object supplies enough metadata to identify:

- canonical format and contract version;
- logical rows/columns and group or block size;
- scale mode, encoding, count, and table order;
- zero-point mode, precision, count, and correction data;
- optional act-order permutation;
- optional sparse mask/indices;
- optional global scale, centroid table, and sign-vector identity; and
- cache bit widths, signedness, head size, and scale group.

Missing or contradictory metadata is an error. A scheme name such as AWQ or
GPTQ is provenance, not a substitute for these fields.

## Operation families

- `quantize` / `dequantize`: deterministic canonical lifecycle conversion.
- `quant_gemv`: one activation row against packed weights.
- `quant_gemm`: an activation tile against packed weights with weight reuse.
- `quantized_lm_head`: tiled vocabulary projection with streaming selection.
- `quantized_embedding`: selected packed rows without full-table decode.
- `quantized_moe`: packed expert tiles with routing-defined row subsets.
- projection fusions: bias/activation, gate/up/SwiGLU, and QKV/RoPE/KV-write.
- cache operations: canonical insertion/gather and direct attention consumption.

An implementation may compose public primitives when the result and externally
visible allocation behavior match the contract. A composition that materializes
the complete dequantized weight matrix does not satisfy direct packed compute.

## Determinism and exceptional inputs

Canonical packers use the rounding rule in the format spec. Deterministic
operations produce bit-identical output for a fixed backend variant and thread
count. Non-finite input to integer, MX, NVFP4, BitNet, or TurboQuant producers
is rejected. FP8 scalar encode handles NaN/infinity as defined by `fp8.md`.
Invalid permutations, centroid ordering, slot mappings, group divisibility, or
scale values are errors and must not be silently clamped.

## Correctness

Kernel error is measured against FP32/FP64 evaluation of the exact emitted
codes, independently from model quantization error. Default tolerances come
from `registry/tolerances.yaml`. Golden byte vectors additionally require exact
packing equality. Cross-backend parity uses the same canonical bytes and
metadata, not backend-prepared buffers.
