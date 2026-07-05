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

