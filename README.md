# QuixiCore

**QuixiCore is a family of native high-performance AI kernel libraries for modern accelerators.**

QuixiCore is one kernel library contract with five standalone native implementations: CUDA, Metal, ROCm, XPU, and Gaudi.

Each backend is a standalone implementation written directly for its target platform. The repositories share no implementation code. They share a common kernel contract: the same operations, quant formats, correctness expectations, benchmark methodology, and public library identity.

## Backends

| Backend | Platform | Repository | Status |
|---|---|---|---|
| QuixiCore CUDA | NVIDIA CUDA, Ampere+ | `QuixiAI/quixicore-cuda` | Active |
| QuixiCore Metal | Apple Silicon / Metal | `QuixiAI/quixicore-metal` | Active |
| QuixiCore ROCm | AMD ROCm / CDNA2-4 | `QuixiAI/quixicore-rocm` | Planned |
| QuixiCore XPU | Intel GPU / oneAPI / SYCL | `QuixiAI/quixicore-xpu` | Planned |
| QuixiCore Gaudi | Intel Gaudi2-3 / HPU | `QuixiAI/quixicore-gaudi` | Planned |

## Design Philosophy

QuixiCore is built around one principle:

**Native implementations. Shared contract. No shared code.**

CUDA kernels should be written like CUDA kernels. Metal kernels should be written like Metal kernels. ROCm kernels should be written like ROCm kernels. XPU kernels should be written for Intel GPU tooling. Gaudi kernels should be written for the Gaudi HPU/TPC stack.

The shared layer is not source code. The shared layer is the definition of what each backend must implement.

## Repository Role

This repository is the umbrella contract repository for the QuixiCore family. It contains:

- Backend registry metadata
- Kernel and quant format registries
- Correctness and benchmarking specifications
- Coverage and architecture support matrices
- Release and naming policy
- Test-vector organization

It intentionally does not contain backend implementation code, shared kernel code, platform bindings, or build systems.

