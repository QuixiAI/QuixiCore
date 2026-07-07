# Philosophy

QuixiCore is organized around a simple rule:

**Native implementations. Shared contract. No shared code.**

The goal is to let every backend use the programming model, compiler stack, memory hierarchy, and runtime integration that fit that platform best.

The umbrella repository defines what must be implemented. Backend repositories decide how to implement it.

## Principles

- Native code should feel native to the platform.
- Correctness expectations should be common across backends.
- Benchmark methodology should be common across backends.
- Quant format definitions should be common across backends.
- Implementation techniques should not be forced across unrelated hardware.

## Non-Goals

- No portable kernel abstraction layer.
- No shared implementation library.
- No lowest-common-denominator runtime.
- No umbrella build system.
