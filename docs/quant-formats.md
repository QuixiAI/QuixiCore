# Quant Formats

QuixiCore quant formats are defined at the contract level so that backend behavior is comparable across accelerators.

The registry in `registry/quant-formats.yaml` is the canonical index. Detailed format notes live under `specs/formats/`.

## Initial Format Families

- GGUF-oriented formats
- MX formats
- FP8
- FP4
- BitNet formats

Format specifications should define layout, scaling behavior, packing, rounding, accumulation expectations, and dequantization semantics.

## Required Per-Format Fields

Every stable quant format specification should eventually define:

- Format name
- Bit width
- Signedness
- Block size or group size
- Scale layout
- Zero-point behavior
- Packing order
- Rounding behavior
- Saturation behavior
- Dequantization formula
- Accumulation expectations
- Supported kernel families
- Reference test vectors

## Compatibility

Backend implementations should not use the same format name for incompatible layouts. If a backend needs a hardware-specific layout, it should document that layout as a backend-local variant and map it back to the contract format at API boundaries.

## Registry

`registry/quant-formats.yaml` is the canonical index of quant format families. Detailed behavior belongs in `specs/formats/`.
