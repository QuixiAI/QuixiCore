# Architecture Support

| Backend | Minimum Architecture | Targets |
|---|---|---|
| CUDA | `sm80` | `sm80`, `sm86`, `sm89`, `sm90`, `sm100` |
| Metal | `apple_m1` | `apple_m1`, `apple_m2`, `apple_m3`, `apple_m4` |
| ROCm | `cdna2` | `cdna2`, `cdna3`, `cdna4` |
| XPU | TBD | `intel_arc`, `intel_data_center_gpu`, `future_xpu` |
| Gaudi | `gaudi2` | `gaudi2`, `gaudi3` |
| CPU | portable scalar | `x86_64`, `aarch64` |

CPU, XPU, and Gaudi are intentionally separate architecture families.
