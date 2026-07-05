# Architecture

QuixiCore is a federated kernel library.

The QuixiCore umbrella repository defines the shared contract. Backend repositories implement that contract independently.

## What Is Shared

- Kernel names
- Kernel semantics
- Quant format definitions
- Correctness expectations
- Benchmark shapes
- Status vocabulary
- Documentation structure
- Release/spec versioning

## What Is Not Shared

- Source code
- Build systems
- Runtime bindings
- Kernel languages
- Compiler flags
- Hardware-specific scheduling
- Platform-specific APIs

## Backend Model

Each backend is a first-class native implementation:

- CUDA for NVIDIA GPUs
- Metal for Apple Silicon
- ROCm for AMD CDNA accelerators
- XPU for Intel GPUs
- Gaudi for Gaudi HPUs

XPU and Gaudi are separate backends because they have different compiler stacks, runtime systems, programming models, performance constraints, and user workflows.

## Repository Topology

The umbrella repository is not an integration checkout. It does not vendor, mirror, or pin backend repositories as git submodules.

Backend repositories are related to the umbrella repository through:

- Repository links in `registry/backends.yaml`
- Contract compatibility metadata in each backend
- Coverage matrices in `matrices/`
- Shared docs and specs in `docs/` and `specs/`

This keeps implementation history, issue tracking, CI, releases, and platform-specific dependencies inside each backend repo.

## Compatibility Flow

1. The umbrella repository publishes or tags a QuixiCore contract version.
2. Backend repositories implement that contract natively.
3. Each backend declares compatibility using `.quixicore/backend.yaml`.
4. The umbrella coverage matrices summarize current implementation status.
