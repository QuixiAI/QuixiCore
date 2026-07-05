# Sampling Kernels

This specification covers:

- Sampling
- Beam Search
- Speculative Decode

## Contract Notes

Sampling kernels should define random source requirements, temperature handling, top-k and top-p behavior, repetition penalties, and determinism expectations where seeds are supplied.

Beam search should define score accumulation, tie-breaking, and finished-sequence handling.

Speculative decode should define draft-token acceptance semantics and output reporting.

