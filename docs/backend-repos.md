# Backend Repositories

The QuixiCore backend repositories are separate first-class projects:

| Backend | Repository | Platform |
|---|---|---|
| CUDA | `QuixiAI/QuixiCore-CUDA` | NVIDIA CUDA, Ampere+ |
| Metal | `QuixiAI/QuixiCore-Metal` | Apple Silicon / Metal |
| ROCm | `QuixiAI/QuixiCore-ROCm` | AMD ROCm / CDNA2-4 |
| XPU | `QuixiAI/QuixiCore-XPU` | Intel GPU / oneAPI / SYCL / Level Zero |
| Gaudi | `QuixiAI/QuixiCore-Gaudi` | Intel Gaudi2-3 / HPU / SynapseAI / TPC |
| CPU | `QuixiAI/QuixiCore-CPU` | Host CPU / SIMD / threading |

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

## Generated Agent Docs and Perf Tooling

Each backend's `AGENTS.md`, `CLAUDE.md`, and `.claude/settings.json` are
generated from `docs/templates/` by `tools/sync_agent_docs.py`, and each
backend's `perf/harness/{run_bench_core.sh,perf_diff.py}` are synced copies of
the umbrella canonicals (`tools/sync_perf_tooling.py`). Run
`bash tools/fleet_check.sh` from the umbrella before committing cross-cutting
changes; it verifies both, plus the notebooks, metadata, matrices, and
conformance snapshots.
