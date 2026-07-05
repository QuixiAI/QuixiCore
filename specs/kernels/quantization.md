# Quantization Kernels

This specification covers:

- Quant GEMV
- Quant GEMM
- Quantized LM Head

## Contract Notes

Quantized kernels should define packing, scale layout, zero-point behavior, group size, dequantization semantics, accumulation type, and supported output types.

Format-specific details should point to `specs/formats/`.

