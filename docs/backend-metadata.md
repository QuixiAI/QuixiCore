# Backend Metadata

Backend metadata is the compatibility declaration each backend repository should publish.

Recommended path:

```text
.quixicore/backend.yaml
```

The schema is defined in `registry/backend-metadata.schema.yaml`.

## Required Fields

- `backend`: stable backend key: `cuda`, `metal`, `rocm`, `xpu`, or `gaudi`
- `name`: user-facing backend name
- `repo`: GitHub repository in `owner/name` form
- `umbrella`: umbrella repository, normally `QuixiAI/QuixiCore`
- `contract`: implemented QuixiCore contract version
- `status`: backend status
- `targets`: supported architecture targets

## Optional Fields

- `upstream`: upstream source repository for forks or lineage tracking
- `notes`: short backend-specific notes
- `integrations`: runtime or framework integrations

## Example

```yaml
backend: cuda
name: QuixiCore CUDA
repo: QuixiAI/QuixiCore-CUDA
umbrella: QuixiAI/QuixiCore
contract: v0.1
status: active
targets:
  - sm80
  - sm86
  - sm89
  - sm90
  - sm100
integrations:
  - CUDA
notes: Native NVIDIA CUDA implementation for Ampere and newer GPUs.
```

## Backend Examples

```yaml
backend: metal
name: QuixiCore Metal
repo: QuixiAI/QuixiCore-Metal
umbrella: QuixiAI/QuixiCore
contract: v0.1
status: active
targets:
  - apple_m1
  - apple_m2
  - apple_m3
  - apple_m4
integrations:
  - Metal
  - MLX
  - PyTorch MPS
```

```yaml
backend: rocm
name: QuixiCore ROCm
repo: QuixiAI/QuixiCore-ROCm
umbrella: QuixiAI/QuixiCore
contract: v0.1
status: active
targets:
  - cdna2
  - cdna3
  - cdna4
integrations:
  - ROCm
  - HIP
```

```yaml
backend: xpu
name: QuixiCore XPU
repo: QuixiAI/QuixiCore-XPU
umbrella: QuixiAI/QuixiCore
contract: v0.1
status: planned
targets:
  - intel_arc
  - intel_data_center_gpu
  - future_xpu
integrations:
  - oneAPI
  - SYCL
  - Level Zero
```

```yaml
backend: gaudi
name: QuixiCore Gaudi
repo: QuixiAI/QuixiCore-Gaudi
umbrella: QuixiAI/QuixiCore
contract: v0.1
status: planned
targets:
  - gaudi2
  - gaudi3
integrations:
  - HPU
  - SynapseAI
  - TPC
```

