# Kernel Capability Map

Inventory date: 2026-07-27.

This document is the operation-level companion to
[backend-coverage.md](backend-coverage.md). It records the union of
kernel capabilities published by the checked-out QuixiCore backend
repositories and identifies the platforms with an implementation or
semantic mapping.

This is an inventory, not a blanket performance-tier, dtype, or
cross-architecture claim. Backend-specific constraints remain in each
backend's manifest, tests, and performance notebooks.

## Source snapshot

| Backend | Platform | Source snapshot | Notes |
|---|---|---|---|
| CUDA | NVIDIA CUDA (Ampere+) | `main` @ `d959679b0163` | Clean working tree. |
| Metal | Apple Silicon / Metal | `agent/basert-kernel-parity` @ `a6d984377288` | Clean tracked feature branch; used instead of the divergent default branch. |
| ROCm | AMD ROCm / CDNA | `main` @ `636ae5ae983f` | Clean working tree. |
| XPU | Intel GPU / oneAPI / SYCL | `main` @ `67c70fe4dc0c` | Clean working tree. |
| Gaudi | Intel Gaudi HPU | `main` @ `024b544fa93c` | Planned scaffold only; ignored for implementation work until hardware is available. |
| CPU | x86-64 and AArch64 | `main` @ `0159223979db` | 35 pre-existing tracked changes; the capability ledgers used here are unchanged. |

Authoritative inputs:

- Metal, ROCm, and XPU: `.quixicore/kernels.yaml` operation entries.
- CUDA: `.quixicore/kernels.yaml` family entries; its manifest currently
  publishes no operation-level entries.
- CPU: `parity/sibling_operations.tsv`, `parity/llama_ops.tsv`, the public
  numerical headers under `include/quixicore_cpu/`, and the semantic
  collapses documented in `docs/sibling-port-matrix.md`.
- Quant formats: each backend's `.quixicore/quant-formats.yaml` plus CPU's
  `parity/sibling_quant_families.tsv`.

## Status legend

| Mark | Meaning |
|---|---|
| ✅ | Published implementation, imported/ported implementation, optimized implementation, or CPU semantic mapping. |
| ✅ opt | Backend manifest explicitly labels the operation optimized. |
| ✅ port | ROCm manifest explicitly labels the operation imported from a sibling backend and records local correctness evidence. |
| 🚧 | Partial family or operation coverage. |
| 🧪 | Experimental implementation. |
| 🔒 | Capability-gated family; availability depends on hardware/runtime configuration. |
| ◇ | CUDA family-level implementation claim only; CUDA does not publish this exact operation ID. |
| ⬜ | Planned. |
| — | No exact operation-level claim in the selected source snapshot. This does not mean unsupported. |

Operation identifiers below are the exact IDs published by backend
manifests. Identical IDs are merged into one row; differently named aliases
remain separate. CPU cells refer to equivalent public semantics and may
collapse accelerator stages, layouts, or fused variants into another CPU
entry point. Where backends assign the same ID to different families, the row
appears once in its most specific section (for example, vision RoPE under
Vision and relative audio attention under Audio).

## Inventory summary

| Measure | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| Published operation entries | 0 | 55 | 215 | 31 | 0 | n/a |
| Union operation semantics represented | family-only | 55 | 215 | 31 | 0 | 257 + 6 CPU-only |

The exact manifest union contains **257 operation IDs**.
CPU maps every one of those semantics and adds **6 numerical
capabilities** from its llama.cpp parity ledger that no selected accelerator
manifest publishes as the same operation ID.

### Canonical contract view

The evidence inventory above preserves backend spellings, variants, and
aggregate markers. The callable contract in `registry/operations.yaml`
normalizes the 263 inventory IDs into **229 observed canonical operations** and
classifies **13 aggregate manifest markers** as non-callable. It also carries
**74 planned practical inference and fused operations**, for **303 canonical
operations** in the adapter ABI.

Every active backend receives the same operation names and
`Status(const KernelCall&)` signature. Missing or unproven entries are generated
as explicit `not_implemented` adapter stubs; those stubs do not change the
evidence marks in this map.

## Family status

| Family | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| Norms | ✅ | ✅ | ✅ | 🚧 | ⬜ | ✅ |
| Activations | ✅ | ✅ | 🚧 | 🚧 | ⬜ | ✅ |
| Attention | ✅ | ✅ | 🚧 | 🚧 | ⬜ | ✅ |
| Linear attention | ✅ | ✅ | 🚧 | 🚧 | ⬜ | ✅ |
| State-space models | ✅ | ✅ | 🚧 | 🚧 | ⬜ | ✅ |
| Dense matmul and projections | ✅ | ✅ | ✅ | 🚧 | ⬜ | ✅ |
| Quantization | ✅ | ✅ | 🚧 | 🚧 | ⬜ | ✅ |
| Mixture of experts | ✅ | ✅ | 🚧 | 🚧 | ⬜ | ✅ |
| Sampling | ✅ | ✅ | 🚧 | 🚧 | ⬜ | ✅ |
| Serving and caches | ✅ | ✅ | 🚧 | 🚧 | ⬜ | ✅ |
| Optimizers | ✅ | ✅ | 🚧 | 🚧 | ⬜ | ✅ |
| Collectives | 🔒 | ⬜ | 🧪 | 🔒 | ⬜ | ✅ |
| Vision | — | ✅ | 🚧 | — | — | ✅ |
| Audio | — | ✅ | 🚧 | — | — | ✅ |
| Convolution | — | — | 🚧 | — | — | ✅ |
| Pooling | — | — | ✅ | — | — | ✅ |
| Utilities and training | ✅ | ✅ | 🚧 | 🚧 | ⬜ | ✅ |

CPU family marks mean semantic reference coverage, not that every operation
has a native SIMD tier. Gaudi remains planned. XPU families remain partial
even where individual operations below are implemented.

### CUDA family-only detail

CUDA's `docs/repository-structure.md` documents the semantic surface below,
but `.quixicore/kernels.yaml` does not yet enumerate these as exact operation
entries. This table explains the `◇` cells; it does not upgrade them to
operation-level claims.

| CUDA family | Status | Documented capability surface |
|---|---:|---|
| Norms | ✅ | RMSNorm, LayerNorm, add-norm, norm-to-quant, and QK norm. |
| Activations | ✅ | GELU, GLU, SiLU/SwiGLU helpers, and standalone softmax. |
| Attention | ✅ | Flash, causal/noncausal, variable-length and backward attention; paged attention, MLA, rotary, quantized-KV attention, and state merging. |
| Linear attention | ✅ | Based, Hedgehog, linear/causal/decay attention, GDN, and complex linear-attention primitives. |
| State-space models | ✅ | Mamba, SSD, selective scan, and FFT convolution. |
| Dense matmul and projections | ✅ | Dense and staged GEMM, complex matmul, Flux, and architecture-tuned GEMM. |
| Quantization | ✅ | Activation/runtime quantization, QGEMM, QGEMV, quantized LM head, FP8/INT8/FP4 packing, and TurboQuant. |
| Mixture of experts | ✅ | Routing, alignment, gather/scatter, grouped and quantized MoE GEMM, LoRA alignment, and finalize. |
| Sampling | ✅ | Sampling, logit transforms and penalties, rejection sampling, beam search, speculative decode, and EAGLE helpers. |
| Serving and caches | ✅ | KV-cache mutation, page/block tables, indexers, MInference, and cache copy/gather helpers. |
| Optimizers | ✅ | AdamW and other training optimizer kernels. |
| Collectives | 🔒 | All-reduce, all-gather, reduce-scatter, all-to-all, fused collective/GEMM paths, ring attention, Ulysses attention, and distributed MoE dispatch. |
| Utilities and training | ✅ | Bit packing, column permutation, Hadamard/FWHT, and small user-visible utilities. |

## Published operation capabilities

### Norms

| Capability | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| `layernorm` | ◇ | — | ✅ | ✅ | — | ✅ |
| `norm_quant` | ◇ | — | ✅ | — | — | ✅ |
| `qk_norm_rope` | ◇ | — | ✅ | — | — | ✅ |
| `qk_norm_rope_kv_f16` | ◇ | — | ✅ | — | — | ✅ |
| `qk_norm_rope_positioned` | ◇ | ✅ | — | — | — | ✅ |
| `rms_norm` | ◇ | — | — | ✅ | — | ✅ |
| `rms_norm_residual_next` | ◇ | — | ✅ | — | — | ✅ |
| `rms_residual_next` | ◇ | — | ✅ | — | — | ✅ |
| `rmsnorm` | ◇ | — | ✅ port | — | — | ✅ |

### Activations

| Capability | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| `elementwise` | ◇ | — | ✅ opt | — | — | ✅ |
| `gelu` | ◇ | — | — | ✅ | — | ✅ |
| `gelu_backward` | ◇ | — | — | ✅ | — | ✅ |
| `glu` | ◇ | — | — | ✅ | — | ✅ |
| `leaky_relu` | ◇ | — | ✅ | — | — | ✅ |
| `sigmoid_mul` | ◇ | ✅ | ✅ | — | — | ✅ |
| `sigmoid_mul_backward` | ◇ | — | ✅ | — | — | ✅ |
| `silu` | ◇ | — | — | ✅ | — | ✅ |
| `silu_backward` | ◇ | — | ✅ | — | — | ✅ |
| `softmax` | ◇ | — | ✅ | ✅ | — | ✅ |
| `softmax_backward` | ◇ | — | ✅ | — | — | ✅ |
| `unary` | ◇ | — | ✅ | — | — | ✅ |
| `value_clip` | ◇ | ✅ | ✅ | — | — | ✅ |

### Attention

| Capability | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| `attention` | ◇ | — | — | ✅ | — | ✅ |
| `attn_composites` | ◇ | — | ✅ | — | — | ✅ |
| `attn_decode_bh` | ◇ | ✅ | ✅ | — | — | ✅ |
| `attn_fwd_sg_d256` | ◇ | — | ✅ | — | — | ✅ |
| `biased_attention` | ◇ | — | ✅ | — | — | ✅ |
| `cross_attention` | ◇ | ✅ | ✅ | — | — | ✅ |
| `decode_cache_attention` | ◇ | ✅ | ✅ | — | — | ✅ |
| `gqa` | ◇ | — | ✅ | — | — | ✅ |
| `gqa_backward` | ◇ | — | ✅ | — | — | ✅ |
| `gqa_causal` | ◇ | — | ✅ | — | — | ✅ |
| `gqa_causal_backward` | ◇ | — | ✅ | — | — | ✅ |
| `gqa_swa` | ◇ | — | ✅ | — | — | ✅ |
| `mrope` | ◇ | ✅ | — | — | — | ✅ |
| `paged_attention_q8_0` | ◇ | ✅ | — | — | — | ✅ |
| `rope` | ◇ | — | — | ✅ | — | ✅ |
| `rope_variants` | ◇ | — | ✅ | — | — | ✅ |
| `rotary` | ◇ | — | ✅ | — | — | ✅ |
| `rotary_positioned` | ◇ | ✅ | — | — | — | ✅ |

### Linear attention

| Capability | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| `based` | ◇ | — | ✅ port | — | — | ✅ |
| `gated_linear_attention` | ◇ | — | ✅ | — | — | ✅ |
| `gdn_gate_beta` | ◇ | ✅ | ✅ | — | — | ✅ |
| `gdn_gated_rmsnorm` | ◇ | ✅ | ✅ | — | — | ✅ |
| `gdn_qkv_prepare` | ◇ | ✅ | ✅ | — | — | ✅ |
| `gdn_recur` | ◇ | ✅ | — | — | — | ✅ |
| `gdn_recurrence` | ◇ | — | ✅ | — | — | ✅ |
| `gdn_short_conv` | ◇ | ✅ | ✅ | — | — | ✅ |
| `hedgehog` | ◇ | — | ✅ port | — | — | ✅ |
| `linear_attention_unnormalized` | ◇ | — | ✅ | — | — | ✅ |
| `linear_attn` | ◇ | — | — | ✅ | — | ✅ |
| `rwkv_wkv6` | ◇ | — | ✅ | — | — | ✅ |
| `rwkv_wkv7` | ◇ | — | ✅ | — | — | ✅ |

### State-space models

| Capability | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| `dsv4_hc_comb` | ◇ | — | ✅ | — | — | ✅ |
| `dsv4_hc_post` | ◇ | — | ✅ | — | — | ✅ |
| `dsv4_hc_pre` | ◇ | — | ✅ | — | — | ✅ |
| `fftconv` | ◇ | — | ✅ port | — | — | ✅ |
| `mamba2_backward` | ◇ | — | ✅ | — | — | ✅ |
| `selective_scan` | ◇ | — | — | ✅ | — | ✅ |
| `ssd_chunked_backward` | ◇ | — | ✅ | — | — | ✅ |
| `ssd_decode` | ◇ | — | ✅ | — | — | ✅ |

### Dense matmul and projections

| Capability | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| `bf16fp32_matmul` | ◇ | — | ✅ | — | — | ✅ |
| `complex_gemm` | ◇ | — | ✅ | — | — | ✅ |
| `decode_linear` | ◇ | — | ✅ | — | — | ✅ |
| `decode_linear_epilogue` | ◇ | ✅ | ✅ | — | — | ✅ |
| `decode_linear_epilogue_dense` | ◇ | — | ✅ | — | — | ✅ |
| `decode_linear_epilogue_packed` | ◇ | — | ✅ | — | — | ✅ |
| `decode_linear_q8` | ◇ | — | ✅ | — | — | ✅ |
| `decode_linear_residual` | ◇ | — | ✅ | — | — | ✅ |
| `decode_swiglu` | ◇ | ✅ | ✅ | — | — | ✅ |
| `decode_swiglu_dense` | ◇ | — | ✅ | — | — | ✅ |
| `decode_swiglu_packed` | ◇ | — | ✅ | — | — | ✅ |
| `dense_gemm` | ◇ | — | — | ✅ | — | ✅ |
| `flux` | ◇ | — | ✅ port | — | — | ✅ |
| `fp8fp32_matmul` | ◇ | — | ✅ | — | — | ✅ |
| `gemm_gate_residual` | ◇ | — | ✅ | — | — | ✅ |
| `gemm_staged` | ◇ | — | ✅ | — | — | ✅ |
| `grouped_gemm` | ◇ | — | ✅ | — | — | ✅ |
| `int8_matmul` | ◇ | — | ✅ | — | — | ✅ |
| `lora_apply` | ◇ | ✅ | — | — | — | ✅ |
| `lora_apply_direct_f16` | ◇ | — | ✅ | — | — | ✅ |
| `matmul_custom` | ◇ | — | ✅ | — | — | ✅ |
| `mxfp8_matmul` | ◇ | — | ✅ | — | — | ✅ |
| `nvfp4_matmul` | ◇ | — | ✅ | — | — | ✅ |
| `scaled_matmul` | ◇ | — | ✅ | — | — | ✅ |

### Quantization

| Capability | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| `act_quant_int8` | ◇ | — | — | ✅ | — | ✅ |
| `base_q_dequant` | ◇ | ✅ | ✅ | — | — | ✅ |
| `base_q_embedding` | ◇ | ✅ | ✅ | — | — | ✅ |
| `base_q_fused_consumers` | ◇ | ✅ | — | — | — | ✅ |
| `base_q_gemm` | ◇ | ✅ | ✅ | — | — | ✅ |
| `base_q_gemv` | ◇ | ✅ | ✅ | — | — | ✅ |
| `base_q_gemv_qkv` | ◇ | — | ✅ | — | — | ✅ |
| `base_q_gemv_swiglu` | ◇ | — | ✅ | — | — | ✅ |
| `base_q_lm_head_argmax` | ◇ | ✅ | ✅ | — | — | ✅ |
| `base_q_moe_gemm` | ◇ | ✅ | ✅ | — | — | ✅ |
| `base_q_moe_swiglu` | ◇ | ✅ | ✅ | — | — | ✅ |
| `base_q_qkv` | ◇ | ✅ | — | — | — | ✅ |
| `base_q_swiglu` | ◇ | ✅ | — | — | — | ✅ |
| `calibration_absmax` | ◇ | ✅ | ✅ | — | — | ✅ |
| `dequant_gather` | ◇ | — | ✅ | — | — | ✅ |
| `fake_quant_float8` | ◇ | — | ✅ | — | — | ✅ |
| `fake_quant_int8` | ◇ | — | ✅ | — | — | ✅ |
| `fp8_gemm` | ◇ | — | — | 🧪 | — | ✅ |
| `gguf_gemv` | ◇ | — | — | ✅ | — | ✅ |
| `lm_head` | ◇ | — | ✅ port | — | — | ✅ |
| `lm_head_beam_advance` | ◇ | ✅ | ✅ | — | — | ✅ |
| `lm_head_candidates` | ◇ | ✅ | ✅ | — | — | ✅ |
| `lm_head_masked` | ◇ | ✅ | ✅ | — | — | ✅ |
| `mxfp4_gemv` | ◇ | — | ✅ | ✅ | — | ✅ |
| `nvfp4_gemv` | ◇ | — | — | ✅ | — | ✅ |
| `qgeglu` | ◇ | — | ✅ | — | — | ✅ |
| `qgemm` | ◇ | — | ✅ opt | — | — | ✅ |
| `qgemm_backward_input` | ◇ | — | ✅ | — | — | ✅ |
| `qgemm_int` | ◇ | — | ✅ | — | — | ✅ |
| `qgemm_int8` | ◇ | — | — | ✅ | — | ✅ |
| `qgemm_q4q8` | ◇ | — | ✅ | — | — | ✅ |
| `qgemv` | ◇ | — | ✅ port | — | — | ✅ |
| `qgemv_int4` | ◇ | — | — | ✅ | — | ✅ |
| `qgemv_q4_0_f32_qkv` | ◇ | — | ✅ | — | — | ✅ |
| `qgemv_q4_0_f32_up_gate` | ◇ | — | ✅ | — | — | ✅ |
| `qgemv_q4_0_f32_up_gate_gelu` | ◇ | — | ✅ | — | — | ✅ |
| `qkv_proj_fused` | ◇ | — | ✅ | — | — | ✅ |
| `quant_rt` | ◇ | — | ✅ | — | — | ✅ |
| `quantize_int4_group` | ◇ | — | — | ✅ | — | ✅ |
| `quantized_embedding` | ◇ | ✅ | ✅ | — | — | ✅ |
| `quantized_embedding_bag` | ◇ | ✅ | ✅ | — | — | ✅ |
| `ternary_code_flip_count` | ◇ | — | ✅ | — | — | ✅ |
| `ternary_pack` | ◇ | — | ✅ | — | — | ✅ |
| `ternary_stats` | ◇ | — | ✅ | — | — | ✅ |
| `ternary_unpack` | ◇ | — | ✅ | — | — | ✅ |
| `tq2_0_pack` | ◇ | — | ✅ | — | — | ✅ |
| `tq2_0_unpack` | ◇ | — | ✅ | — | — | ✅ |
| `turboquant` | ◇ | — | ✅ port | — | — | ✅ |

### Mixture of experts

| Capability | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| `moe` | ◇ | — | ✅ port | — | — | ✅ |
| `moe_finalize_backward` | ◇ | — | ✅ | — | — | ✅ |
| `moe_gather_backward` | ◇ | — | ✅ | — | — | ✅ |
| `moe_grouped_gemm_backward_input` | ◇ | — | ✅ | — | — | ✅ |
| `moe_grouped_gemm_backward_weight` | ◇ | — | ✅ | — | — | ✅ |
| `moe_grouped_qgemm` | ◇ | — | ✅ | — | — | ✅ |
| `moe_grouped_qswiglu` | ◇ | — | ✅ | — | — | ✅ |
| `moe_quant` | ◇ | — | ✅ port | — | — | ✅ |
| `moe_route_grouped` | ◇ | — | ✅ | — | — | ✅ |
| `moe_route_topk` | ◇ | — | — | ✅ | — | ✅ |

### Sampling

| Capability | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| `argmax` | ◇ | — | — | ✅ | — | ✅ |
| `logits_softcap` | ◇ | ✅ | ✅ | — | — | ✅ |
| `sample_categorical` | ◇ | — | — | ✅ | — | ✅ |
| `top_k_renorm` | ◇ | — | ✅ | — | — | ✅ |
| `top_k_sample` | ◇ | — | — | ✅ | — | ✅ |
| `top_p_renorm` | ◇ | — | ✅ | — | — | ✅ |

### Serving and caches

| Capability | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| `embedding_lookup` | ◇ | — | — | ✅ | — | ✅ |
| `embedding_lookup_types` | ◇ | ✅ | ✅ | — | — | ✅ |
| `kv_cache_copy_blocks_q8_0` | ◇ | ✅ | — | — | — | ✅ |
| `kv_cache_gather` | ◇ | — | — | ✅ | — | ✅ |
| `kv_cache_gather_bitnet_kv3` | ◇ | — | ✅ | — | — | ✅ |
| `kv_cache_gather_q8_0` | ◇ | ✅ | — | — | — | ✅ |
| `kv_cache_q8_0` | ◇ | — | ✅ | — | — | ✅ |
| `kv_cache_scatter` | ◇ | — | — | ✅ | — | ✅ |
| `kv_cache_scatter_bitnet_kv3` | ◇ | — | ✅ | — | — | ✅ |
| `kv_cache_scatter_q8_0` | ◇ | ✅ | — | — | — | ✅ |
| `masked_mean_pool_rms_l2` | ◇ | ✅ | — | — | — | ✅ |
| `mean_pool_rms_l2` | ◇ | — | ✅ | — | — | ✅ |
| `paged_attention_advanced` | ◇ | — | ✅ | — | — | ✅ |
| `paged_attention_bitnet_kv3` | ◇ | — | ✅ | — | — | ✅ |
| `paged_attention_turboquant` | ◇ | — | ✅ | — | — | ✅ |
| `quantized_attention` | ◇ | — | ✅ | — | — | ✅ |
| `serving` | ◇ | — | ✅ port | — | — | ✅ |

### Optimizers

| Capability | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| `adamw` | ◇ | — | — | ✅ | — | ✅ |
| `adamw_masked` | ◇ | — | ✅ | — | — | ✅ |
| `sgd` | ◇ | — | ✅ | — | — | ✅ |

### Collectives

| Capability | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| `broadcast` | 🔒 | — | ✅ | — | — | ✅ |
| `fp8_gemm_collectives` | 🔒 | — | ✅ | — | — | ✅ |
| `reduce_sum` | 🔒 | — | ✅ | — | — | ✅ |
| `standalone_collectives` | 🔒 | — | ✅ | — | — | ✅ |

### Vision

| Capability | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| `add_relative_position_2d` | — | — | ✅ | — | — | ✅ |
| `avg_pool2d_tokens` | — | ✅ | ✅ | — | — | ✅ |
| `edge_mlp_256x7` | — | ✅ | ✅ | — | — | ✅ |
| `extract_patches_2d` | — | ✅ | ✅ | — | — | ✅ |
| `extract_patches_3d` | — | ✅ | ✅ | — | — | ✅ |
| `factorized_position_2d` | — | ✅ | ✅ | — | — | ✅ |
| `get_relative_position` | — | — | ✅ | — | — | ✅ |
| `interpolate_position_2d` | — | ✅ | ✅ | — | — | ✅ |
| `patch_merge_layer_norm` | — | — | ✅ | — | — | ✅ |
| `pool_tokens_by_position` | — | ✅ | ✅ | — | — | ✅ |
| `qwen_vision_rope_2d` | ◇ | ✅ | ✅ | — | — | ✅ |
| `space_to_depth_norm_linear` | — | ✅ | ✅ | — | — | ✅ |
| `timestep_embedding` | — | — | ✅ | — | — | ✅ |
| `upscale_nearest_2d` | — | — | ✅ | — | — | ✅ |
| `vision_patch_projection` | — | ✅ | ✅ | — | — | ✅ |
| `vision_patch_projection_3d` | — | ✅ | ✅ | — | — | ✅ |
| `vision_rope_2d` | ◇ | ✅ | ✅ | — | — | ✅ |
| `window_partition` | — | — | ✅ | — | — | ✅ |
| `window_unpartition` | — | — | ✅ | — | — | ✅ |

### Audio

| Capability | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| `audio_causal_depthwise_conv1d` | — | ✅ | ✅ | — | — | ✅ |
| `audio_conv1d` | — | ✅ | — | — | — | ✅ |
| `audio_conv1d_direct` | — | — | ✅ | — | — | ✅ |
| `audio_depthwise_conv1d` | — | ✅ | ✅ | — | — | ✅ |
| `audio_relative_attention` | ◇ | ✅ | ✅ | — | — | ✅ |

### Convolution

| Capability | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| `col2im_1d` | — | — | ✅ | — | — | ✅ |
| `col2im_2d` | — | — | ✅ | — | — | ✅ |
| `conv2d` | — | — | ✅ | — | — | ✅ |
| `conv3d` | — | — | ✅ | — | — | ✅ |
| `conv_transpose_1d` | — | — | ✅ | — | — | ✅ |
| `conv_transpose_2d` | — | — | ✅ | — | — | ✅ |
| `depthwise_conv2d` | — | — | ✅ | — | — | ✅ |
| `im2col_2d` | — | — | ✅ | — | — | ✅ |
| `im2col_3d` | — | — | ✅ | — | — | ✅ |
| `pool1d` | — | — | ✅ | — | — | ✅ |
| `pool2d` | — | — | ✅ | — | — | ✅ |
| `pool2d_backward` | — | — | ✅ | — | — | ✅ |

### Pooling

| Capability | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| `pool_mean_rms_l2` | — | — | ✅ | — | — | ✅ |

### Utilities and training

| Capability | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| `accumulate` | ◇ | — | ✅ | — | — | ✅ |
| `add_id` | ◇ | — | ✅ | — | — | ✅ |
| `add_scalar` | ◇ | — | ✅ | — | — | ✅ |
| `arange` | ◇ | — | ✅ | — | — | ✅ |
| `argsort` | ◇ | — | ✅ | — | — | ✅ |
| `clamp` | ◇ | — | ✅ | — | — | ✅ |
| `concat` | ◇ | — | ✅ | — | — | ✅ |
| `cosine` | ◇ | — | ✅ | — | — | ✅ |
| `count_equal` | ◇ | — | ✅ | — | — | ✅ |
| `cross_entropy` | ◇ | — | — | ✅ | — | ✅ |
| `cumulative_sum` | ◇ | — | ✅ | — | — | ✅ |
| `diag_embed` | ◇ | — | ✅ | — | — | ✅ |
| `diag_mask` | ◇ | — | ✅ | — | — | ✅ |
| `divide` | ◇ | — | ✅ | — | — | ✅ |
| `dropout` | ◇ | — | — | ✅ | — | ✅ |
| `fill` | ◇ | — | ✅ | — | — | ✅ |
| `group_norm` | ◇ | — | ✅ | — | — | ✅ |
| `hadamard` | ◇ | — | — | ✅ | — | ✅ |
| `kd_ce_fused_bwd` | ◇ | — | ✅ | — | — | ✅ |
| `kd_ce_fused_fwd` | ◇ | — | ✅ | — | — | ✅ |
| `kd_kl_dense_bwd` | ◇ | — | ✅ | — | — | ✅ |
| `kd_kl_dense_fwd` | ◇ | — | ✅ | — | — | ✅ |
| `kd_kl_topk_bwd` | ◇ | — | ✅ | — | — | ✅ |
| `kd_kl_topk_fwd` | ◇ | — | ✅ | — | — | ✅ |
| `l2_normalize` | ◇ | — | ✅ | — | — | ✅ |
| `logarithm` | ◇ | — | ✅ | — | — | ✅ |
| `marginal` | ◇ | — | ✅ | — | — | ✅ |
| `multiply` | ◇ | — | ✅ | — | — | ✅ |
| `outer_product` | ◇ | — | ✅ | — | — | ✅ |
| `pad_2d` | ◇ | — | ✅ | — | — | ✅ |
| `pad_reflect_1d` | ◇ | — | ✅ | — | — | ✅ |
| `reduce_mean` | ◇ | — | ✅ | — | — | ✅ |
| `reduce_sum_all` | ◇ | — | ✅ | — | — | ✅ |
| `repeat_2d` | ◇ | — | ✅ | — | — | ✅ |
| `repeat_backward_2d` | ◇ | — | ✅ | — | — | ✅ |
| `roll_2d` | ◇ | — | ✅ | — | — | ✅ |
| `scale` | ◇ | — | ✅ | — | — | ✅ |
| `set_rows` | ◇ | — | ✅ | — | — | ✅ |
| `sine` | ◇ | — | ✅ | — | — | ✅ |
| `solve_lower_triangular` | ◇ | — | ✅ | — | — | ✅ |
| `square` | ◇ | — | ✅ | — | — | ✅ |
| `square_root` | ◇ | — | ✅ | — | — | ✅ |
| `subtract` | ◇ | — | ✅ | — | — | ✅ |
| `tensor_copy` | ◇ | — | ✅ | — | — | ✅ |
| `tensor_set_4d` | ◇ | — | ✅ | — | — | ✅ |
| `threshold_topk_indices` | ◇ | — | ✅ | — | — | ✅ |
| `triangular_fill` | ◇ | — | ✅ | — | — | ✅ |

## Additional CPU numerical capabilities

These CPU parity-ledger capabilities are not published under the same exact
operation ID by the selected accelerator manifests:

| Capability | Platform | Evidence class |
|---|---|---|
| `attention_with_lse` | CPU | llama.cpp numerical mapping |
| `cross_entropy_backward` | CPU | llama.cpp numerical mapping |
| `embedding_backward` | CPU | llama.cpp numerical mapping |
| `indexer_k_gather` | CPU | llama.cpp numerical mapping |
| `rms_norm_backward` | CPU | llama.cpp numerical mapping |
| `swiglu_oai` | CPU | llama.cpp numerical mapping |

The CPU `unary` capability covers 22 selector modes:
`abs`, `sgn`, `neg`, `step`, `tanh`, `elu`, `relu`, `sigmoid`, `gelu`, `gelu_quick`, `silu`, `hardswish`, `hardsigmoid`, `exp`, `expm1`, `softplus`, `gelu_erf`, `xielu`, `floor`, `ceil`, `round`, `trunc`.

The CPU `glu`/`swiglu_oai` surface covers 6 GLU modes:
`reglu`, `geglu`, `swiglu`, `swiglu_oai`, `geglu_erf`, `geglu_quick`.

## Quant-format declarations

This table preserves each backend's exact manifest identifier. For example,
`mx` is a family-level declaration while `mxfp8`, `mxfp6`, and `mxfp4`
are format-specific XPU declarations.

| Format ID | CUDA | Metal | ROCm | XPU | Gaudi | CPU |
|---|---:|---:|---:|---:|---:|---:|
| `awq` | — | — | — | ⬜ | — | ✅ |
| `base_qn` | — | ✅ | — | — | — | ✅ |
| `bitnet` | ✅ | ✅ | 🚧 | ⬜ | ⬜ | ✅ |
| `fp4` | ✅ | ✅ | 🚧 | ⬜ | ⬜ | ✅ |
| `fp8` | ✅ | ✅ | 🚧 | 🧪 | ⬜ | ✅ |
| `gguf` | ✅ | ✅ | 🚧 | ✅ | ⬜ | ✅ |
| `int4_group` | — | — | — | 🧪 | — | ✅ |
| `int8` | — | — | — | 🧪 | — | ✅ |
| `marlin_awq_gptq_hqq` | ✅ | — | — | — | — | ✅ |
| `mx` | ✅ | ✅ | 🚧 | — | ⬜ | ✅ |
| `mxfp4` | — | — | — | 🧪 | — | ✅ |
| `mxfp6` | — | — | — | ⬜ | — | ✅ |
| `mxfp8` | — | — | — | ⬜ | — | ✅ |
| `nvfp4` | — | — | — | 🧪 | — | ✅ |
| `q8_0_kv` | — | ✅ | — | — | — | ✅ |
| `tq2_0` | — | ✅ | — | — | — | ✅ |
| `turboquant` | — | ✅ | — | — | — | ✅ |

Format rows summarize encoding/decode families, not every operation-format,
dtype, layout, or ISA cell. Those finer matrices remain backend-owned.

## Evidence and maintenance

A platform mark is based on declared metadata plus the backend's evidence
index; directory presence alone is not counted. Relevant evidence lives in:

- `<backend>/perf/optimization_status.md`
- `<backend>/perf/baseline_status.md`
- `<backend>/perf/results/` (or that backend's documented legacy path)
- backend correctness tests and operation manifests

Update this map when a child manifest or CPU parity ledger changes. Record the
new source revisions above, preserve exact operation IDs, and do not promote
a `◇`, `🚧`, `🧪`, or `⬜` cell to `✅` without backend correctness and
performance evidence.
