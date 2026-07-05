# Release Policy

QuixiCore releases are contract releases.

A QuixiCore umbrella release identifies a version of the shared contract. Backend repositories may then declare compatibility with that contract version.

## Versioning

- Contract versions use `vMAJOR.MINOR`.
- Patch-level backend implementation releases belong in backend repositories.
- Breaking contract changes require a major version bump.
- Additive kernel, quant format, or benchmark coverage may use a minor version bump.

## Compatibility

Backend compatibility claims should name the umbrella contract version they implement.

