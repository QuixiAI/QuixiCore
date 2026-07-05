# Backend Repositories

The QuixiCore backend repositories are separate first-class projects:

| Backend | Repository | Platform |
|---|---|---|
| CUDA | `QuixiAI/QuixiCore-CUDA` | NVIDIA CUDA, Ampere+ |
| Metal | `QuixiAI/QuixiCore-Metal` | Apple Silicon / Metal |
| ROCm | `QuixiAI/QuixiCore-ROCm` | AMD ROCm / CDNA2-4 |
| XPU | `QuixiAI/QuixiCore-XPU` | Intel GPU / oneAPI / SYCL / Level Zero |
| Gaudi | `QuixiAI/QuixiCore-Gaudi` | Intel Gaudi2-3 / HPU / SynapseAI / TPC |

## Ownership Boundary

The umbrella repository owns the contract. Backend repositories own implementation.

No backend should import implementation code from another backend or from this umbrella repository.

## No Submodules

The umbrella repository does not use git submodules for backend repositories.

Submodules would make the umbrella repository look like an integration checkout and would introduce pinned-SHA maintenance overhead. QuixiCore is instead a contract repository:

- Backend locations are recorded in `registry/backends.yaml`.
- Backend compatibility is declared by backend metadata.
- Backend implementation code stays in the backend repositories.
- Cross-backend status is tracked by matrices and registries.

## Backend Compatibility

Each backend should declare the QuixiCore contract version it implements. The recommended location is:

```text
.quixicore/backend.yaml
```

The expected shape is defined in `docs/backend-metadata.md` and `registry/backend-metadata.schema.yaml`.
