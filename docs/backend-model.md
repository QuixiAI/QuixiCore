# Backend Model

QuixiCore is one kernel library contract with five standalone native implementations: CUDA, Metal, ROCm, XPU, and Gaudi.

The umbrella repository defines the shared contract. Backend repositories implement that contract independently.

## Why No Submodules

QuixiCore does not use git submodules for backend repositories.

Submodules would make this repository behave like a source checkout for all backends. That is not the project model. The umbrella repository should stay small, readable, and focused on contracts, registries, matrices, test-vector definitions, and release policy.

## How Repositories Are Connected

Backend repositories are connected to the umbrella repository by metadata and documentation:

- `registry/backends.yaml` records canonical backend locations.
- `.quixicore/backend.yaml` in each backend declares contract compatibility.
- `matrices/` summarizes coverage across backends.
- `docs/` and `specs/` define shared behavior.

## Backend Responsibilities

Each backend repository owns:

- Native source code
- Build system
- Runtime bindings
- Platform-specific tests
- Platform-specific benchmarks
- Backend releases
- Hardware support policy

## Umbrella Responsibilities

The umbrella repository owns:

- Kernel contract
- Quant format contract
- Correctness methodology
- Benchmark methodology
- Backend registry
- Compatibility metadata schema
- Coverage matrices
- Contract releases

## Compatibility Declaration

Each backend should include:

```text
.quixicore/backend.yaml
```

That file should name the backend, repository, umbrella repository, implemented contract version, status, and target architectures. See `docs/backend-metadata.md`.

