# Claude Instructions

Follow `AGENTS.md` in this repository. The most important rule is the
performance gate:

Before committing any backend kernel implementation, routing change, benchmark
change, or performance claim, complete at least one focused performance
optimization run on an affected kernel and record the result in that backend's
`perf/optimization_status.md`.

If the right hardware or runtime is unavailable, do not commit the kernel
optimization as a measured win. Report the blocker or limit the change to
docs/scaffolding with no performance claim.
