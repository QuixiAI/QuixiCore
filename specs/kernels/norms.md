# Norm And Activation Kernels

This specification covers:

- RMSNorm
- LayerNorm
- GELU
- GLU

## Contract Notes

Norm kernels should define epsilon behavior, accumulation precision, supported input and output types, and whether residual fusion is part of the contract.

Activation kernels should define approximation mode, exactness expectations, and shape constraints.

