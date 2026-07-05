# Backend Coverage

| Kernel Family | CUDA | Metal | ROCm | XPU | Gaudi |
|---|---:|---:|---:|---:|---:|
| RMSNorm / LayerNorm | ✅ | ✅ | 🚧 | ⬜ | ⬜ |
| Softmax | ✅ | ✅ | 🚧 | ⬜ | ⬜ |
| GELU / GLU | ✅ | ✅ | 🚧 | ⬜ | ⬜ |
| Causal Attention | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| Paged Attention | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| MLA Decode | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| Quant GEMV | ✅ | ✅ | 🚧 | ⬜ | ⬜ |
| Quant GEMM | ✅ | ✅ | 🚧 | ⬜ | ⬜ |
| Quantized LM Head | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| Sampling | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| Beam Search | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| Speculative Decode | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| Mamba / SSD | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| MoE Routing | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| Grouped MoE GEMM | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| Optimizers | ✅ | ✅ | ⬜ | ⬜ | ⬜ |

## Status Legend

```text
✅ complete
🟡 beta
🚧 in progress
🧪 experimental
⬜ planned
❌ unsupported / not applicable
```

