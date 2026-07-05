# Backend Repositories

The QuixiCore backend repositories are separate first-class projects:

| Backend | Repository | Platform |
|---|---|---|
| CUDA | `QuixiAI/quixicore-cuda` | NVIDIA CUDA, Ampere+ |
| Metal | `QuixiAI/quixicore-metal` | Apple Silicon / Metal |
| ROCm | `QuixiAI/quixicore-rocm` | AMD ROCm / CDNA2-4 |
| XPU | `QuixiAI/quixicore-xpu` | Intel GPU / oneAPI / SYCL / Level Zero |
| Gaudi | `QuixiAI/quixicore-gaudi` | Intel Gaudi2-3 / HPU / SynapseAI / TPC |

## Ownership Boundary

The umbrella repository owns the contract. Backend repositories own implementation.

No backend should import implementation code from another backend or from this umbrella repository.

