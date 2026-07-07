# Correctness

QuixiCore correctness is defined by shared semantics and backend-specific validation against common test vectors.

Correctness methodology should cover:

- Reference implementation choice
- Input shape coverage
- Data type coverage
- Quant format coverage
- Tolerance thresholds
- Determinism requirements
- Edge-case behavior

The tolerance registry in `registry/tolerances.yaml` defines the initial vocabulary for numerical comparisons.

## Reference Policy

Each kernel family should name a reference behavior. The reference may be:

- A simple scalar reference implementation
- A PyTorch expression
- A NumPy expression
- A format-specific decoder or encoder
- A published model-equivalent formula

The reference is not shared implementation code for backends. It exists to define expected behavior and generate test vectors.

## Test Vector Policy

Shared test vectors should be small, deterministic, and easy to inspect. They should cover:

- Representative shapes from `registry/benchmark-shapes.yaml`
- Boundary shapes
- Dtype combinations
- Quant format edge cases
- Masking and padding cases
- Determinism-sensitive sampling cases where applicable

Large generated fixture sets should be reproducible rather than checked in directly.

## Tolerance Policy

Tolerance expectations are defined by dtype and kernel family. A backend should report:

- Maximum absolute error
- Maximum relative error
- Mean absolute error where useful
- Failed element count
- Shape, dtype, and quant format

Tolerance exceptions must be documented in the backend repository and reflected in umbrella status if they affect contract compatibility.

## Determinism

Deterministic kernels should produce stable outputs for the same inputs, backend version, and hardware target. Stochastic kernels should define seed behavior and make non-deterministic behavior explicit.
