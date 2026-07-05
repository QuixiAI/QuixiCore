# Benchmarking

QuixiCore benchmarking is defined at the contract level and executed by each backend using native tooling.

The umbrella repository defines:

- Benchmark shape names
- Required input and output dimensions
- Warmup and measurement expectations
- Reporting fields
- Status vocabulary

Backend repositories should implement benchmarks in the tooling appropriate for the platform.

