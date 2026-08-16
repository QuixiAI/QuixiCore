# Build Conventions

QuixiCore backends use different native toolchains, but their generated
artifacts follow one directory and profile convention. This keeps local builds
predictable without imposing shared implementation code or a single build
system on every backend.

## Artifact Root

Generated build-system files, objects, libraries, executables, test logs, and
tool caches belong under the repository-local `build/` directory.

Use one subdirectory per incompatible configuration:

```text
build/
  dev/
  test/
  perf/
  sanitize/
  <platform>-<purpose>/
  scratch/
```

Do not create top-level peers such as `build-perf/`, `build-x86/`,
`build-fix-123/`, or `build-agent-name/`. A configuration that needs its own
cache belongs under `build/<profile>/`; the need for multiple caches does not
require multiple artifact roots.

Ecosystem-owned caches that cannot be redirected safely may retain their native
location, but backend-owned wrappers and instructions must use `build/` by
default.

## Standard Profiles

Backends should expose the profiles that apply to their toolchain using these
stable names:

| Profile | Purpose |
|---|---|
| `dev` | Normal local development with symbols and fast rebuilds. |
| `test` | The configuration exercised by the backend's correctness CI. |
| `perf` | Optimized build used for benchmark evidence. |
| `sanitize` | Debug build with the platform's supported sanitizers. |
| `<platform>-<purpose>` | A reusable platform-specific configuration, such as `macos-x86-test`. |
| `scratch` | Temporary experiments; remove them after the task. |

Profile names describe reusable intent, not a ticket, phase, agent, kernel, or
one-off optimization attempt.

## Backend Interface

- CMake backends should check in `CMakePresets.json` and place each preset at
  `build/${presetName}` or another stable subdirectory of `build/`.
- Make-, Xcode-, language-, and vendor-native backends should provide their
  normal wrapper or documented command with equivalent profile semantics.
- The default build command should use `dev`; CI should use `test`; performance
  evidence must use `perf`.
- Build wrappers should fail clearly when obsolete top-level build directories
  are present rather than silently adding another cache.
- Backend documentation, CI, and benchmark wrappers must use the same paths.

## Cleanup And Evidence

The entire `build/` tree is disposable and must be ignored by Git. Durable
correctness and performance records belong in the backend's documented test,
status, and `perf/results/` locations. Before finishing a task, remove temporary
profiles and leave only reusable local configurations that still serve the
developer.

The umbrella repository defines this convention; each standalone backend owns
the presets or wrappers that implement it for its native toolchain.
