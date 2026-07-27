# Kernel Contract

The QuixiCore kernel contract defines the operations each backend is expected to implement, how those operations behave, and how correctness is measured.

The contract covers:

- Operation names and families
- Tensor shape conventions
- Supported data types and quant formats
- Numerical tolerance expectations
- Determinism expectations where applicable
- Benchmark shape coverage
- Status reporting

Backend repositories may expose platform-specific tuning knobs, but the common contract should remain recognizable across all implementations.

## Canonical Operation ABI

`registry/operations.yaml` is the normalized callable-operation registry. Every
entry uses a semantic `snake_case` name and the same framework-neutral adapter
signature:

```cpp
quixicore::contract::Status(
    const quixicore::contract::KernelCall&) noexcept
```

`KernelCall` carries typed tensor views, named scalar or byte attributes,
backend context, stream, and workspace. The ABI is declared in
`include/quixicore/contract/kernel_abi.hpp`. Backend-native typed entry points
remain private implementation details and are connected through adapters.
Each backend exposes the normalized dispatcher as
`quixicore::<backend>::contract_api::dispatch(OperationId, KernelCall)`.

Dtype, layout, architecture, tile size, and dense/packed route do not create new
public operation names when they preserve host-visible and stored-byte
semantics. They belong in tensor descriptors, attributes, or backend variants.
A quant encoding may retain a distinct operation when its packed-byte contract
is itself observable. Only documented semantic differences receive separate
canonical names.

The normalization ledger is `registry/operation-normalization.yaml`. It records
proven spelling/variant aliases, excludes aggregate manifest markers from the
callable ABI, and carries planned practical inference and fused operations.

## Generated Backend Stubs

Run `ruby tools/sync_kernel_contract.rb` after changing the capability map or
normalization ledger. For each active backend it generates:

- an identical copy of the canonical ABI and operation descriptor headers;
- `include/quixicore/<backend>/contract.hpp`, the normalized backend contract
  include;
- `include/quixicore/<backend>/contract_stubs.hpp`, containing header-only
  `not_implemented` adapters for every unimplemented or unproven operation;
- `.quixicore/kernel-stubs.yaml`, which records every stub and why it exists.

The generated stubs are scaffolding, not support claims. A family-level claim
without an exact operation entry remains an adapter stub until the backend
wires and evidences the canonical operation. A stub may be removed only after
the native path, correctness coverage, performance evidence, and manifest entry
exist. Evidenced native paths without a canonical wrapper return
`adapter_not_wired`, keeping that integration gap distinct from an unimplemented
kernel. `ruby tools/sync_kernel_contract.rb --check` verifies synchronization.

## Contract Levels

The kernel contract has three levels:

- **Family**: a broad operation group, such as attention, quantization, or sampling.
- **Operation**: a concrete behavior backends must expose, such as RMSNorm or Quant GEMM.
- **Variant**: an implementation-specific or shape-specific specialization that still obeys the operation semantics.

The umbrella repository standardizes families and operations. Backend repositories may add variants as long as they do not change the shared operation semantics.

## Required Per-Kernel Fields

Every stable kernel specification should eventually define:

- Operation name
- Kernel family
- Input tensors
- Output tensors
- Supported dtypes
- Supported quant formats, if applicable
- Shape constraints
- Layout constraints
- Accumulation precision
- Determinism expectations
- Numerical tolerances
- Benchmark shapes
- Reference behavior
- Error behavior for unsupported inputs

## Backend Requirements

A backend can claim support for a kernel only when it has:

- A native implementation in the backend repository
- Correctness coverage against the shared semantics
- Benchmark coverage for the required shapes
- Status reflected in `matrices/backend-coverage.md`
- Compatibility metadata naming the implemented contract version

## Platform Freedom

The contract defines what the operation means, not how it is implemented. Backends may choose platform-specific memory layouts, fusion strategies, scheduling, compiler flags, and runtime APIs.

Those choices must remain invisible to contract-level behavior unless the backend documents a supported platform-specific extension.
