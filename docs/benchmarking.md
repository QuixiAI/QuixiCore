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

## Reporting Format (schema 1)

Every benchmark run writes one run directory in the backend repo:

```
perf/results/YYYY-MM-DD/<run-id>/
    run.json         # environment and invocation (one JSON object)
    results.jsonl    # one JSON object per benchmarked case
    summary.md       # human table generated from results.jsonl (recommended)
    *.log, *.txt     # raw harness output (backend-specific, optional)
```

`perf/results/` is git-ignored; runs cited as evidence are summarized into
`perf/optimization_status.md`, and curated rows are promoted into the tracked
`perf/baselines/<host-fingerprint>/` directory (see Baselines below).

### results.jsonl rows

Required fields: `schema` (integer, currently `1`), `kernel`, `variant`,
`shape` (object; `{}` is allowed when the harness has no structured dims and
the variant string carries identity), `dtype`, and `status`
(`ok` | `skip` | `fail`). Rows with `status: "ok"` additionally require
`target_ms` (the median) plus one variance group:

- preferred: `target_p20_ms`, `target_p80_ms`, `target_cv`
- accepted: `target_min_ms`, `target_max_ms`, `target_spread` (max/min ratio)

A harness that measures throughput only (no per-case latency) may omit
`target_ms` on an `ok` row if the row carries a throughput field (`gflops`,
`tflops`, `tops`, `gbps`, `weight_gbps`, or a `measurements` list); such rows
validate with a warning and can never be used to gate a regression decision.

Reserved optional fields (do not repurpose these names): `format`, `notes`,
`batch`, `check_passed`, `max_abs_err`, `max_rel_err`, `baselines` (a map of
baseline name to an object with required `ms` and `speedup`, optional
`p20_ms`, `p80_ms`, `cv`, `batch`), `gbps`, `weight_gbps`, `gflops`,
`skip_reason`, `phase`.

The key `schema` is canonical; readers accept the legacy `schema_version`
spelling during the transition.

### run.json

Required fields: `schema` (`1`), `backend` (registry backend id), `repo`
(`Org/Name`), `contract` (`vX.Y`), `git` (short SHA, `-dirty` suffix when the
tree is dirty), `timestamp` (ISO-8601), `warmup`, `iters`, and enough host
identity to derive a fingerprint: `os` and `arch`, plus `device` (GPU
backends) or `cpu_model` (CPU). Optional fields include `preset`, `kernels`,
`formats`, `wall_s`, `threads`, `compiler`, `build_type`, `cpu_features`,
`affinity_policy`, `frequency_policy`, framework versions, and `container`.

### Host fingerprint

`slug(backend) + "-" + slug(device or cpu_model) + "-" + slug(arch)`,
lowercased with non-alphanumerics collapsed to `-`, e.g.
`metal-apple-m5-max-arm64` or `cpu-intel-r-xeon-r-gold-6454s-x86-64`.
Results from different fingerprints are never comparable; `scripts/perf_diff.py`
refuses to gate across them.

### Baselines

Each backend commits curated baselines under
`perf/baselines/<host-fingerprint>/{results.jsonl,run.json}`. A baseline row
must come from a completed, correctness-checked, low-noise run; the refresh
procedure is documented in the backend's `perf/baselines/README.md` and goes
through `perf_diff.py promote`, which filters accordingly.

### Measurement rules

Report the median of `iters` timed iterations after `warmup` untimed ones;
adaptive batching is allowed and recorded in `batch`. A run whose noise
exceeds the guard limits (coefficient of variation above the backend's limit,
or min-to-max spread above 1.20x) must not be used for a keep/reject
decision — re-run on an idle host instead. A run that times out or crashes is
inconclusive, never a rejection and never a win.

### Field reconciliation

The umbrella `AGENTS.md` requires "median, and variance or min/max" in every
optimization run record. Those map to `target_ms` and either variance group
above. `scripts/perf_diff.py validate` checks a run directory against this
section.

## Native Tooling

Benchmarks should use native platform timing and synchronization:

- CUDA uses CUDA events or equivalent native timing.
- Metal uses Metal command buffer timing or a documented host-side synchronization method.
- ROCm uses HIP/ROCm timing facilities.
- XPU uses oneAPI/SYCL/Level Zero timing facilities.
- Gaudi uses HPU/SynapseAI profiling and timing facilities.
- CPU uses a monotonic host timer with documented synchronization, thread affinity, and frequency policy where applicable.

## Comparability

Cross-backend benchmarks should be treated as comparable only when they use the same operation semantics, shape, dtype, quant format, and measurement policy. Backend-specific optimized variants may be reported separately.

## Shape Registry

`registry/benchmark-shapes.yaml` defines the initial shape families. Backend repositories may add local exploratory shapes, but contract compatibility should be measured against registry shapes.
