# Backend Coverage

| Kernel Family | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| RMSNorm / LayerNorm | ✅ | ✅ | 🚧 | ⬜ | ⬜ | ✅ |
| Softmax | ✅ | ✅ | 🚧 | ⬜ | ⬜ | ✅ |
| GELU / GLU | ✅ | ✅ | 🚧 | ⬜ | ⬜ | ✅ |
| Causal Attention | ✅ | ✅ | 🚧 | ⬜ | ⬜ | ✅ |
| Paged Attention | ✅ | ✅ | 🚧 | ⬜ | ⬜ | ✅ |
| MLA Decode | ✅ | ✅ | 🚧 | ⬜ | ⬜ | ✅ |
| Quant GEMV | ✅ | ✅ | 🚧 | ⬜ | ⬜ | ✅ |
| Quant GEMM | ✅ | ✅ | 🚧 | ⬜ | ⬜ | ✅ |
| Quantized LM Head | ✅ | ✅ | 🚧 | ⬜ | ⬜ | ✅ |
| Sampling | ✅ | ✅ | 🚧 | ⬜ | ⬜ | ✅ |
| Beam Search | ✅ | ✅ | 🚧 | ⬜ | ⬜ | ✅ |
| Speculative Decode | ✅ | ✅ | 🚧 | ⬜ | ⬜ | ✅ |
| Mamba / SSD | ✅ | ✅ | 🚧 | ⬜ | ⬜ | ✅ |
| MoE Routing | ✅ | ✅ | 🚧 | ⬜ | ⬜ | ✅ |
| Grouped MoE GEMM | ✅ | ✅ | 🚧 | ⬜ | ⬜ | ✅ |
| Optimizers | ✅ | ✅ | 🚧 | ⬜ | ⬜ | ✅ |

## Status Legend

```text
✅ complete
🟡 beta
🚧 in progress
🧪 experimental
⬜ planned
❌ unsupported / not applicable
```

ROCm status records operation-level CDNA3 progress, not complete dtype,
quant-format, or CDNA2-through-CDNA4 coverage. As of 2026-07-26, the backend
manifest still labels most families partial, while its MI300X correctness and
focused performance evidence is indexed in that backend's
`docs/metal-cpu-parity-gaps.md`, `perf/optimization_status.md`, and
`perf/results/`.

CPU status is semantic contract coverage, not a claim that every
format-by-ISA cell has an optimized tier. As of 2026-07-25, QuixiCore-CPU's
enforced parity inventory maps 127 sibling operations, its Apple AArch64
Release suite passes 55/55 tests, and its Intel Sapphire Rapids suite passes
all 57 locally executable tests. Correctness and per-kernel performance
evidence are indexed in that backend's `parity/`, `perf/baseline_status.md`,
and `perf/optimization_status.md`.
