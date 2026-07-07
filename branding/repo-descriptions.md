# Repository Descriptions

## Umbrella

QuixiCore is one kernel library contract with six standalone native implementations: CUDA, Metal, ROCm, XPU, Gaudi, and CPU.

## Backend Short Descriptions

- `QuixiCore-CUDA`: Native NVIDIA CUDA implementation for Ampere+ GPUs.
- `QuixiCore-Metal`: Native Apple Silicon implementation using Metal.
- `QuixiCore-ROCm`: Native AMD ROCm implementation for CDNA accelerators.
- `QuixiCore-XPU`: Native Intel GPU implementation using oneAPI, SYCL, and Level Zero.
- `QuixiCore-Gaudi`: Native Intel Gaudi implementation using the HPU/SynapseAI/TPC ecosystem.
- `QuixiCore-CPU`: Native CPU implementation using host SIMD vectorization and threaded runtimes.
