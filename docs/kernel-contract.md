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

## Contract Levels

The kernel contract has three levels:

- **Family**: a broad operation group, such as attention, quantization, or sampling.
- **Operation**: a concrete behavior backends must expose, such as RMSNorm or Quant GEMM.
- **Variant**: an implementation-specific or shape-specific specialization that still obeys the operation semantics.

The umbrella repository standardizes families and operations. Backend repositories may add variants as long as they do not change the shared operation semantics.

## Required Per-Kernel Fields

Every stable kernel specification should eventually define:

- Operation name
- Kernel family
- Input tensors
- Output tensors
- Supported dtypes
- Supported quant formats, if applicable
- Shape constraints
- Layout constraints
- Accumulation precision
- Determinism expectations
- Numerical tolerances
- Benchmark shapes
- Reference behavior
- Error behavior for unsupported inputs

## Backend Requirements

A backend can claim support for a kernel only when it has:

- A native implementation in the backend repository
- Correctness coverage against the shared semantics
- Benchmark coverage for the required shapes
- Status reflected in `matrices/backend-coverage.md`
- Compatibility metadata naming the implemented contract version

## Platform Freedom

The contract defines what the operation means, not how it is implemented. Backends may choose platform-specific memory layouts, fusion strategies, scheduling, compiler flags, and runtime APIs.

Those choices must remain invisible to contract-level behavior unless the backend documents a supported platform-specific extension.
