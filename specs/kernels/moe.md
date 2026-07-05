# Mixture-Of-Experts Kernels

This specification covers:

- MoE Routing
- Grouped MoE GEMM

## Contract Notes

MoE routing should define top-k selection, score normalization, capacity behavior, token ordering, and tie-breaking.

Grouped MoE GEMM should define expert grouping, input packing, output scatter, quantization compatibility, and accumulation behavior.

