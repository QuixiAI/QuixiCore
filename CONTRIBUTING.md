# Contributing

QuixiCore contributions should preserve the umbrella repository boundary:

- Contract, registry, documentation, matrix, and test-vector changes belong here.
- Backend implementation changes belong in the relevant backend repository.
- Shared implementation code is out of scope.

## Backend Boundaries

Each backend is expected to implement the shared contract natively for its platform. A change that requires CUDA, Metal, ROCm, XPU, or Gaudi source code should be made in the corresponding backend repository.

## Spec Changes

Contract changes should update the relevant docs and registries together:

- `docs/kernel-contract.md`
- `registry/kernels.yaml`
- `registry/quant-formats.yaml`
- `registry/tolerances.yaml`
- `matrices/`
- `specs/`

Spec changes should describe compatibility impact and whether existing backend behavior remains valid.

## Status Vocabulary

Use the status vocabulary from `registry/status-schema.yaml` and keep matrices consistent with it.

