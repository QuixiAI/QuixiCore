# Kernel Contract

The QuixiCore kernel contract defines the operations each backend is expected to implement, how those operations behave, and how correctness is measured.

The contract covers:

- Operation names and families
- Tensor shape conventions
- Supported data types and quant formats
- Numerical tolerance expectations
- Determinism expectations where applicable
- Benchmark shape coverage
- Status reporting

Backend repositories may expose platform-specific tuning knobs, but the common contract should remain recognizable across all five implementations.

