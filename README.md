# QuixiCore

**QuixiCore is a family of native high-performance AI kernel libraries for modern hardware platforms.**

QuixiCore is one kernel library contract with six standalone native implementations: CUDA, Metal, ROCm, XPU, Gaudi, and CPU.

Each backend is a standalone implementation written directly for its target platform. The repositories share no implementation code. They share a common kernel contract: the same operations, quant formats, correctness expectations, benchmark methodology, and public library identity.

## Backends

| Backend | Platform | Repository |
|---|---|---|
| QuixiCore CUDA | NVIDIA CUDA, Ampere+ | [QuixiAI/QuixiCore-CUDA](https://github.com/QuixiAI/QuixiCore-CUDA) |
| QuixiCore Metal | Apple Silicon / Metal | [QuixiAI/QuixiCore-Metal](https://github.com/QuixiAI/QuixiCore-Metal) |
| QuixiCore ROCm | AMD ROCm / CDNA2-4 | [QuixiAI/QuixiCore-ROCm](https://github.com/QuixiAI/QuixiCore-ROCm) |
| QuixiCore XPU | Intel GPU / oneAPI / SYCL | [QuixiAI/QuixiCore-XPU](https://github.com/QuixiAI/QuixiCore-XPU) |
| QuixiCore Gaudi | Intel Gaudi2-3 / HPU | [QuixiAI/QuixiCore-Gaudi](https://github.com/QuixiAI/QuixiCore-Gaudi) |
| QuixiCore CPU | Host CPU / SIMD / threading | [QuixiAI/QuixiCore-CPU](https://github.com/QuixiAI/QuixiCore-CPU) |

## Design Philosophy

QuixiCore is built around one principle:

**Native implementations. Shared contract. No shared code.**

CUDA kernels should be written like CUDA kernels. Metal kernels should be written like Metal kernels. ROCm kernels should be written like ROCm kernels. XPU kernels should be written for Intel GPU tooling. Gaudi kernels should be written for the Gaudi HPU/TPC stack. CPU kernels should be written for host CPU vectorization and threading.

The shared layer is not source code. The shared layer is the definition of what each backend must implement.

## Backend Relationship

The umbrella repository links to backend repositories but does not vendor them.

QuixiCore does not use git submodules. Each backend declares the QuixiCore contract version it implements using backend metadata, and implementation work happens in that backend repository.

## Repository Role

This repository is the umbrella contract repository for the QuixiCore family. It contains:

- Backend registry metadata
- Kernel and quant format registries
- Correctness and benchmarking specifications
- Build artifact and profile conventions
- Coverage and architecture support matrices
- Release and naming policy
- Test-vector organization

It intentionally does not contain backend implementation code, shared kernel code, platform bindings, or build systems.

Backend build systems remain native to their repositories, while generated
artifact layout and reusable profile names follow
[`docs/build-conventions.md`](docs/build-conventions.md).

## Contract Version

The initial contract target is `v0.1`. See `roadmap/v0.1-checklist.md` for the checklist that turns the current scaffold into a usable compatibility target.
