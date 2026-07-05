# Attention Kernels

This specification covers attention-related kernel families:

- Softmax
- Causal Attention
- Paged Attention
- MLA Decode

## Contract Notes

Attention kernels should define tensor layout, mask semantics, sequence length handling, KV-cache behavior, accumulation type, and output tolerance.

Paged attention specifications should define page size, block table semantics, cache layout, and invalid-page behavior.

MLA decode specifications should define projection layout, cache layout, and compatibility expectations for decode-only execution.

