# GGUF Formats

This specification tracks GGUF-oriented quantization format compatibility for QuixiCore.

The contract should define supported block layouts, scale placement, metadata assumptions, packing rules, and dequantization semantics.


## E8M0 scale: GGUF is not OCP MX

GGUF's MXFP4 shares the E8M0 scale byte with `mx-formats.md` but not its edge
semantics, and the two must not share a decoder.

ggml reconstructs the scale by bit-punning the code into the fp32 exponent
field with no special cases:

```c
scale = __uint_as_float((uint32_t)code << 23);
```

so codes 0..254 give `2^(code-127)` exactly as MX does, and code 255 gives
**+Inf** where MX specifies **NaN**. ggml's quantizer does not emit 255, so the
divergence is unreachable from files produced by conformant writers -- but a
decoder shared between the two paths is wrong for one of them, and matching
ggml is a requirement here because the purpose is to read the GGUF files that
already exist.

Note that code 0 decodes to `2^-127`, which is **subnormal**. A decoder that
treats it as zero, or a test that compares with a tolerance rather than by
bits, will not notice the difference.

Contract vectors: `test-vectors/quant/e8m0_gguf.json` (and `e8m0.json` for the
MX contract they diverge from).

## MXFP4 element order

The low nibble of packed byte `i` is element `i`; the high nibble is element
`i + 16`. This is **not** an even/odd interleave. Swapping the halves leaves
the value multiset and the block norm essentially unchanged, so a norm-only
check will pass a decoder that has them backwards. `test-vectors/quant/
mxfp4.json` pins element positions for that reason.

## IQ2_XXS decode cost

IQ2_XXS is an E8-lattice codebook format: each 32-weight group costs four
dependent random reads of a 256-entry grid plus a sign-table read. Backends
implementing a tiled GEMM must decode at **tile load**, once per weight, rather
than inside the inner dot, which runs once per (row, column) pair. Decoding in
the dot multiplies the gather by the tile width: measured on CDNA3 that is 1.07x
the per-row vector kernel against 3.4x for decode-at-load. This is a property of
the format, not of any one backend.
