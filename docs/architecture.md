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

