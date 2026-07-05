# Benchmarking

QuixiCore benchmarking is defined at the contract level and executed by each backend using native tooling.

The umbrella repository defines:

- Benchmark shape names
- Required input and output dimensions
- Warmup and measurement expectations
- Reporting fields
- Status vocabulary

Backend repositories should implement benchmarks in the tooling appropriate for the platform.

## Measurement Policy

Backend benchmarks should report enough information to make results reproducible:

- Backend repository and commit
- QuixiCore contract version
- Hardware target
- Driver/runtime/compiler versions
- Kernel family and operation
- Shape name and concrete dimensions
- Input and output dtypes
- Quant format, if applicable
- Warmup iterations
- Measurement iterations
- Latency summary
- Throughput summary where applicable

## Native Tooling

Benchmarks should use native platform timing and synchronization:

- CUDA uses CUDA events or equivalent native timing.
- Metal uses Metal command buffer timing or a documented host-side synchronization method.
- ROCm uses HIP/ROCm timing facilities.
- XPU uses oneAPI/SYCL/Level Zero timing facilities.
- Gaudi uses HPU/SynapseAI profiling and timing facilities.

## Comparability

Cross-backend benchmarks should be treated as comparable only when they use the same operation semantics, shape, dtype, quant format, and measurement policy. Backend-specific optimized variants may be reported separately.

## Shape Registry

`registry/benchmark-shapes.yaml` defines the initial shape families. Backend repositories may add local exploratory shapes, but contract compatibility should be measured against registry shapes.
