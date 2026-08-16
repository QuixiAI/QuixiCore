#!/usr/bin/env python3
"""Generate the canonical kernel-contract files from the capability map.

Reads matrices/capability-map.md and registry/operation-normalization.yaml,
then writes registry/operations.yaml, the umbrella contract headers, and each
sibling backend's contract headers and .quixicore/kernel-stubs.yaml.

Usage:
  python3 tools/sync_kernel_contract.py            # write all generated files
  python3 tools/sync_kernel_contract.py --check    # verify, exit 1 on drift

This is a behavior-preserving port of the retired tools/sync_kernel_contract.rb
(stdlib only; YAML via tools/qc_yaml.py). The YAML emitter reproduces Ruby
Psych's output style — quoting, sequence indentation, and 80-column plain-
scalar folding — so the port produces byte-identical files (verified against
the Ruby tool's output on the same inputs before the Ruby tool was removed).
"""

import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qc_yaml  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPABILITY_MAP = os.path.join(ROOT, "matrices", "capability-map.md")
NORMALIZATION = os.path.join(ROOT, "registry", "operation-normalization.yaml")
OPERATIONS_REGISTRY = os.path.join(ROOT, "registry", "operations.yaml")
ABI_HEADER = os.path.join(ROOT, "include", "quixicore", "contract", "kernel_abi.hpp")
OPERATIONS_HEADER = os.path.join(ROOT, "include", "quixicore", "contract", "operations.hpp")

BACKENDS = {
    "metal": os.path.join(ROOT, "QuixiCore-Metal"),
    "cuda": os.path.join(ROOT, "QuixiCore-CUDA"),
    "rocm": os.path.join(ROOT, "QuixiCore-ROCm"),
    "xpu": os.path.join(ROOT, "QuixiCore-XPU"),
    "cpu": os.path.join(ROOT, "QuixiCore-CPU"),
}

DISPLAY_FAMILIES = {
    "Norms": "norms",
    "Activations": "activations",
    "Attention": "attention",
    "Linear attention": "linear_attention",
    "State-space models": "ssm",
    "Dense matmul and projections": "matmul",
    "Quantization": "quantization",
    "Mixture of experts": "moe",
    "Sampling": "sampling",
    "Serving and caches": "serving",
    "Optimizers": "optimizers",
    "Collectives": "collectives",
    "Vision": "vision",
    "Audio": "audio",
    "Convolution": "convolution",
    "Pooling": "pooling",
    "Utilities and training": "utils",
}

MANIFEST_FAMILIES = {"convolution": "conv"}

CPU_ONLY_FAMILIES = {
    "attention_with_lse": "attention",
    "cross_entropy_backward": "utils",
    "embedding_backward": "serving",
    "indexer_k_gather": "serving",
    "rms_norm_backward": "norms",
    "swiglu_oai": "activations",
}

COVERED_STATUSES = ("implemented", "optimized", "imported")
FAMILY_GAPS = {
    "implemented": "family-only metadata; canonical adapter not wired",
    "partial": "partial family; canonical operation not implemented",
    "capability_gated": "capability-gated family",
    "planned": "planned family",
    "experimental": "experimental family",
    "unsupported": "unsupported family",
}
EXACT_GAPS = {
    "partial": "partial operation",
    "experimental": "experimental operation",
    "capability_gated": "capability-gated operation",
    "planned": "planned operation",
    "unsupported": "unsupported operation",
}


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def inventory_date():
    with open(CAPABILITY_MAP) as f:
        for line in f:
            if line.startswith("Inventory date:"):
                m = re.search(r"\d{4}-\d{2}-\d{2}", line)
                if m:
                    return m.group(0)
    die(f"missing inventory date in {CAPABILITY_MAP}")


def parse_observed_operations():
    operations = {}
    section = None
    in_operations = False
    in_cpu_only = False
    with open(CAPABILITY_MAP) as f:
        for raw in f:
            line = raw.rstrip("\n")
            if line == "## Published operation capabilities":
                in_operations = True
                continue
            if line == "## Additional CPU numerical capabilities":
                in_operations = False
                in_cpu_only = True
                continue
            if line == "## Quant-format declarations":
                in_cpu_only = False
                continue
            if in_operations and line.startswith("### "):
                section = line[len("### "):]
                continue
            if in_operations:
                m = re.match(r"^\| `([^`]+)` \|", line)
                if m:
                    if section not in DISPLAY_FAMILIES:
                        die(f"unknown capability-map family {section!r}")
                    operations[m.group(1)] = DISPLAY_FAMILIES[section]
                    continue
            if in_cpu_only:
                m = re.match(r"^\| `([^`]+)` \| CPU \|", line)
                if m:
                    name = m.group(1)
                    operations[name] = CPU_ONLY_FAMILIES[name]
    if len(operations) != 263:
        die(f"expected 263 observed operation IDs, got {len(operations)}")
    return operations


def build_registry():
    normalization = qc_yaml.load_file(NORMALIZATION)
    aliases = normalization["aliases"]
    family_overrides = normalization.get("family_overrides") or {}
    aggregates = normalization["aggregates"]
    planned = normalization["planned_operations"]
    observed = parse_observed_operations()

    callable_ops = {}
    aggregate_records = {}

    for source_name, family in observed.items():
        if source_name in aggregates:
            aggregate_records[source_name] = {
                "family": family,
                "source_ids": [source_name],
                "maturity": "observed",
                "callable": False,
            }
            continue
        canonical_name = aliases.get(source_name, source_name)
        canonical_family = family_overrides.get(canonical_name, family)
        record = callable_ops.setdefault(canonical_name, {
            "family": canonical_family,
            "kind": "operation",
            "maturity": "observed",
            "abi": normalization["abi"],
            "source_ids": [],
        })
        if record["family"] != canonical_family:
            die(f"alias {source_name} crosses families: "
                f"{record['family']} vs {canonical_family}")
        record["source_ids"].append(source_name)

    for name, details in planned.items():
        if name in callable_ops:
            die(f"planned operation duplicates observed canonical name {name}")
        callable_ops[name] = {
            "family": details["family"],
            "kind": details["kind"],
            "maturity": "planned",
            "abi": normalization["abi"],
            "source_ids": [],
        }

    for record in callable_ops.values():
        record["source_ids"].sort()

    return {
        "schema_version": normalization["schema_version"],
        "inventory_date": inventory_date(),
        "abi": {
            "name": normalization["abi"],
            "cpp_signature": "quixicore::contract::Status(const quixicore::contract::KernelCall&) noexcept",
            "header": "include/quixicore/contract/kernel_abi.hpp",
        },
        "naming": {
            "style": "semantic_snake_case",
            "variant_rule": "dtype, format, layout, architecture, tile, and route are descriptors or backend variants",
        },
        "operations": dict(sorted(callable_ops.items())),
        "aggregates": dict(sorted(aggregate_records.items())),
    }


def cpp_string(value):
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def operations_header(registry):
    operations = registry["operations"]
    lines = ["#pragma once", "", "#include <array>", "#include <cstdint>",
             "#include <string_view>", "", "namespace quixicore::contract {", "",
             "enum class OperationId : std::uint16_t {"]
    for name in operations:
        lines.append(f"  {name},")
    lines += ["};", "", "struct OperationDescriptor {", "  OperationId id;",
              "  std::string_view name;", "  std::string_view family;",
              "  std::string_view kind;", "  std::string_view maturity;", "};", "",
              f"inline constexpr std::array<OperationDescriptor, {len(operations)}> kOperations{{{{"]
    for name, record in operations.items():
        lines.append(
            f"    {{OperationId::{name}, {cpp_string(name)}, "
            f"{cpp_string(record['family'])}, {cpp_string(record['kind'])}, "
            f"{cpp_string(record['maturity'])}}},"
        )
    lines += ["}};", "",
              "[[nodiscard]] constexpr std::string_view operation_name(OperationId id) noexcept {",
              "  for (const auto& operation : kOperations) {",
              "    if (operation.id == id) return operation.name;", "  }",
              "  return {};", "}", "", "}  // namespace quixicore::contract", ""]
    return "\n".join(lines)


def git_revision(path):
    try:
        out = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"],
                             cwd=path, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        die(f"cannot read git revision for {path}")
    return out.stdout.strip()


def backend_stubs(backend, path, registry):
    manifest_path = os.path.join(path, ".quixicore", "kernels.yaml")
    manifest = {} if backend == "cpu" else qc_yaml.load_file(manifest_path)
    exact = manifest.get("operations") or {}
    families = manifest.get("families") or {}
    stubs = {}

    for name, record in registry["operations"].items():
        if record["maturity"] == "planned":
            stubs[name] = dict(record, reason="planned contract; no backend implementation evidence")
            continue
        if backend == "cpu":
            continue
        exact_statuses = []
        for source_id in record["source_ids"]:
            entry = exact.get(source_id) or {}
            status = entry.get("status")
            if status:
                exact_statuses.append(status)
        if any(s in COVERED_STATUSES for s in exact_statuses):
            continue
        noncovered = next((s for s in exact_statuses if s in EXACT_GAPS), None)
        if noncovered:
            reason = EXACT_GAPS[noncovered]
        else:
            manifest_family = MANIFEST_FAMILIES.get(record["family"], record["family"])
            family_status = (families.get(manifest_family) or {}).get("status")
            reason = FAMILY_GAPS[family_status] if family_status else "no family claim"
        stubs[name] = dict(record, reason=reason)
    return stubs, git_revision(path)


def stub_header(backend, stubs):
    namespace = f"quixicore::{backend}::contract_stubs"
    lines = ["#pragma once", "",
             "// Generated by QuixiCore/tools/sync_kernel_contract.py. Do not edit.",
             "// These adapters are scaffolding only and make no implementation claim.",
             "", "#include <array>", "",
             '#include "quixicore/contract/kernel_abi.hpp"', "",
             f"namespace {namespace} {{", "",
             "using quixicore::contract::KernelCall;",
             "using quixicore::contract::Status;",
             "using quixicore::contract::StubDescriptor;", ""]
    for name, record in stubs.items():
        lines.append(f"[[nodiscard]] inline Status {name}(const KernelCall&) noexcept {{")
        lines.append(f"  return quixicore::contract::not_implemented({cpp_string(name)}, {cpp_string(record['reason'])});")
        lines.append("}")
        lines.append("")
    lines.append(f"inline constexpr std::array<StubDescriptor, {len(stubs)}> kStubs{{{{")
    for name, record in stubs.items():
        lines.append(f"    {{{cpp_string(name)}, {cpp_string(record['family'])}, {cpp_string(record['reason'])}, &{name}}},")
    lines += ["}};", "", f"}}  // namespace {namespace}", ""]
    return "\n".join(lines)


def backend_contract_header(backend, stubs):
    lines = ["#pragma once", "",
             f"// Generated canonical contract include for the {backend} backend.",
             "// Native optimized APIs remain backend-owned behind this adapter surface.",
             "", '#include "quixicore/contract/kernel_abi.hpp"',
             '#include "quixicore/contract/operations.hpp"',
             f'#include "quixicore/{backend}/contract_stubs.hpp"', "",
             f"namespace quixicore::{backend}::contract_api {{", "",
             "[[nodiscard]] inline quixicore::contract::Status dispatch(",
             "    quixicore::contract::OperationId operation,",
             "    const quixicore::contract::KernelCall& call) noexcept {",
             "  switch (operation) {"]
    for name in stubs:
        lines.append(f"    case quixicore::contract::OperationId::{name}:")
        lines.append(f"      return quixicore::{backend}::contract_stubs::{name}(call);")
    lines += ["    default:", "      break;", "  }",
              "  const auto name = quixicore::contract::operation_name(operation);",
              "  return quixicore::contract::adapter_not_wired(",
              '      name.empty() ? "unknown_operation" : name.data());', "}", "",
              f"}}  // namespace quixicore::{backend}::contract_api", ""]
    return "\n".join(lines)


def stub_manifest(backend, revision, registry, stubs):
    entries = {
        name: {
            "family": record["family"],
            "kind": record["kind"],
            "reason": record["reason"],
            "source_ids": record["source_ids"],
        }
        for name, record in stubs.items()
    }
    return {
        "schema_version": 0.2,
        "backend": backend,
        "backend_revision": revision,
        "inventory_date": registry["inventory_date"],
        "abi": registry["abi"]["name"],
        "generated_from": [
            "QuixiCore/registry/operations.yaml",
            ".quixicore/kernels.yaml",
        ],
        "canonical_operation_count": len(registry["operations"]),
        "stub_count": len(stubs),
        "stubs": entries,
    }


# --------------------------------------------------------------------------
# Psych-compatible YAML emitter (for exactly the shapes this tool writes)
# --------------------------------------------------------------------------

_QUOTE_SINGLE = re.compile(
    r"^(-?\d+(\.\d+)?|\d{4}-\d{2}-\d{2}|true|false|yes|no|on|off|null|~)$",
    re.IGNORECASE,
)
_BEST_WIDTH = 80


def _emit_scalar(value):
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return ""
    if isinstance(value, float):
        text = repr(value)
        return text
    if isinstance(value, int):
        return str(value)
    text = str(value)
    if text == "" or _QUOTE_SINGLE.match(text):
        return "'" + text.replace("'", "''") + "'"
    if text.startswith("."):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def _fold(prefix, scalar, indent):
    """Psych-style plain-scalar folding: break at the first space once the
    column reaches the best width; continuations indent two deeper."""
    line = prefix + scalar
    if len(line) <= _BEST_WIDTH or scalar.startswith(("'", '"')) or " " not in scalar:
        return [line]
    out = []
    col = len(prefix)
    current = prefix
    for word in scalar.split(" "):
        if current != prefix and current != " " * (indent + 2):
            if col >= _BEST_WIDTH:
                out.append(current)
                current = " " * (indent + 2)
                col = indent + 2
            else:
                current += " "
                col += 1
        current += word
        col += len(word)
    out.append(current)
    return out


def _emit_block(value, indent):
    pad = " " * indent
    lines = []
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, dict) and item:
                lines.append(f"{pad}{key}:")
                lines.extend(_emit_block(item, indent + 2))
            elif isinstance(item, list) and item:
                lines.append(f"{pad}{key}:")
                for entry in item:
                    lines.append(f"{pad}- {_emit_scalar(entry)}")
            elif isinstance(item, (dict, list)):
                lines.append(f"{pad}{key}: {'{}' if isinstance(item, dict) else '[]'}")
            else:
                lines.extend(_fold(f"{pad}{key}: ", _emit_scalar(item), indent))
        return lines
    raise TypeError(f"unsupported top-level YAML value: {type(value)}")


def yaml_dump(value):
    return "\n".join(["---"] + _emit_block(value, 0)) + "\n"


def generated_files(registry):
    files = {
        OPERATIONS_REGISTRY: yaml_dump(registry),
        OPERATIONS_HEADER: operations_header(registry),
    }
    with open(ABI_HEADER) as f:
        abi = f.read()
    for backend, path in BACKENDS.items():
        stubs, revision = backend_stubs(backend, path, registry)
        include_root = os.path.join(path, "include", "quixicore")
        files[os.path.join(include_root, "contract", "kernel_abi.hpp")] = abi
        files[os.path.join(include_root, "contract", "operations.hpp")] = operations_header(registry)
        files[os.path.join(include_root, backend, "contract_stubs.hpp")] = stub_header(backend, stubs)
        files[os.path.join(include_root, backend, "contract.hpp")] = backend_contract_header(backend, stubs)
        files[os.path.join(path, ".quixicore", "kernel-stubs.yaml")] = yaml_dump(
            stub_manifest(backend, revision, registry, stubs)
        )
    return files


def main():
    argv = sys.argv[1:]
    check = "--check" in argv
    argv = [a for a in argv if a != "--check"]
    if argv:
        die(f"usage: {os.path.basename(sys.argv[0])} [--check]")

    registry = build_registry()
    files = generated_files(registry)

    if check:
        stale = []
        for path, expected in files.items():
            try:
                with open(path) as f:
                    current = f.read()
            except OSError:
                current = None
            if current != expected:
                stale.append(path)
        if stale:
            print("generated kernel-contract files are stale:", file=sys.stderr)
            for path in stale:
                print(f"  {path}", file=sys.stderr)
            sys.exit(1)
        print(f"kernel contract is synchronized ({len(registry['operations'])} canonical operations)")
    else:
        for path, content in files.items():
            os.makedirs(os.path.dirname(path), exist_ok=True)
            try:
                with open(path) as f:
                    if f.read() == content:
                        continue
            except OSError:
                pass
            with open(path, "w") as f:
                f.write(content)
        print(f"wrote {len(files)} generated files for {len(registry['operations'])} canonical operations")


if __name__ == "__main__":
    main()
