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

