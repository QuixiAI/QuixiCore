# Agent Instructions

This is the QuixiCore umbrella repository. It defines shared contracts,
registries, benchmark shapes, tolerances, and cross-backend status. Backend
kernel implementations live in the sibling repositories:

- `QuixiCore-Metal`
- `QuixiCore-CUDA`
- `QuixiCore-ROCm`
- `QuixiCore-XPU`
- `QuixiCore-Gaudi`
- `QuixiCore-CPU`

## Core Rules

- Preserve the public QuixiCore contract. Backend-specific layouts and fast paths
  must stay behind the shared API semantics.
- Read the relevant registry or matrix before changing contracts:
  `registry/kernels.yaml`, `registry/quant-formats.yaml`,
  `registry/benchmark-shapes.yaml`, `registry/tolerances.yaml`, and the files
  under `matrices/`.
- Keep umbrella changes backend-neutral unless the file is explicitly about one
  backend.
- Do not claim a backend supports a kernel, dtype, quant format, or performance
  tier unless the corresponding backend repo has correctness and performance
  evidence.

## Git Publishing Policy

- Never create, switch, rename, or choose a branch unless the user explicitly
  requests it. The user owns branch selection.
- Never create a pull request unless the user explicitly requests one.
- When asked to "commit and push," commit on the branch that is already checked
  out and push that same branch to its configured upstream.
- Apply this policy to the umbrella repository and every child repository.
- If the current branch has no upstream, pushing it is blocked, or branch
  selection is ambiguous, stop and ask the user rather than creating or
  switching branches or opening a pull request.

## Performance Optimization Requirement

Before committing any kernel implementation, kernel routing change, benchmark
change, or performance claim in a backend repo, the agent must complete at least
one focused performance optimization run on an affected kernel in that backend.

A valid optimization run includes:

- A named kernel, operation, dtype/format, and shape set.
- A correctness check for the touched path.
- A baseline measurement and a candidate/current measurement.
- Hardware, driver/runtime, command line, git commit or working-tree label,
  warmups, iterations, median, and variance or min/max.
- A keep/reject decision recorded in the backend's
  `perf/optimization_status.md`.

If the required hardware or runtime is unavailable, do not commit a kernel
optimization or performance claim. Stop and report the blocker, or restrict the
commit to docs/scaffolding that makes no speedup claim.

Pure umbrella documentation, registry cleanup, or metadata changes may skip a
kernel performance run, but they must not assert performance improvements
without backend evidence.

## Where To Record Evidence

- Backend operating guide: `<backend>/perf/perf.md`.
- Optimization notebook: `<backend>/perf/optimization_status.md`.
- Baseline index: `<backend>/perf/baseline_status.md`.
- Raw outputs: `<backend>/perf/results/` or the backend's documented legacy
  path. Do not commit large profiler traces.

## Agent Workflow

1. Check `git status` before editing. Do not revert user changes.
2. Identify the backend and contract surface touched by the task.
3. For kernel work, read the backend's `perf/perf.md` before designing the
   experiment.
4. Run correctness first, then at least one focused performance run.
5. Update the relevant status or registry files with measured facts.
6. Commit only the intended files. Keep commit messages normal and descriptive.
