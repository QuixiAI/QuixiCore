#!/usr/bin/env ruby
# frozen_string_literal: true

require "fileutils"
require "open3"
require "yaml"

ROOT = File.expand_path("..", __dir__)
CAPABILITY_MAP = File.join(ROOT, "matrices", "capability-map.md")
NORMALIZATION = File.join(ROOT, "registry", "operation-normalization.yaml")
OPERATIONS_REGISTRY = File.join(ROOT, "registry", "operations.yaml")
ABI_HEADER = File.join(ROOT, "include", "quixicore", "contract", "kernel_abi.hpp")
OPERATIONS_HEADER = File.join(ROOT, "include", "quixicore", "contract", "operations.hpp")

BACKENDS = {
  "metal" => File.join(ROOT, "QuixiCore-Metal"),
  "cuda" => File.join(ROOT, "QuixiCore-CUDA"),
  "rocm" => File.join(ROOT, "QuixiCore-ROCm"),
  "xpu" => File.join(ROOT, "QuixiCore-XPU"),
  "cpu" => File.join(ROOT, "QuixiCore-CPU")
}.freeze

DISPLAY_FAMILIES = {
  "Norms" => "norms",
  "Activations" => "activations",
  "Attention" => "attention",
  "Linear attention" => "linear_attention",
  "State-space models" => "ssm",
  "Dense matmul and projections" => "matmul",
  "Quantization" => "quantization",
  "Mixture of experts" => "moe",
  "Sampling" => "sampling",
  "Serving and caches" => "serving",
  "Optimizers" => "optimizers",
  "Collectives" => "collectives",
  "Vision" => "vision",
  "Audio" => "audio",
  "Convolution" => "convolution",
  "Pooling" => "pooling",
  "Utilities and training" => "utils"
}.freeze

MANIFEST_FAMILIES = {
  "convolution" => "conv"
}.freeze

CPU_ONLY_FAMILIES = {
  "attention_with_lse" => "attention",
  "cross_entropy_backward" => "utils",
  "embedding_backward" => "serving",
  "indexer_k_gather" => "serving",
  "rms_norm_backward" => "norms",
  "swiglu_oai" => "activations"
}.freeze

COVERED_STATUSES = %w[implemented optimized imported].freeze
FAMILY_GAPS = {
  "implemented" => "family-only metadata; canonical adapter not wired",
  "partial" => "partial family; canonical operation not implemented",
  "capability_gated" => "capability-gated family",
  "planned" => "planned family",
  "experimental" => "experimental family",
  "unsupported" => "unsupported family"
}.freeze
EXACT_GAPS = {
  "partial" => "partial operation",
  "experimental" => "experimental operation",
  "capability_gated" => "capability-gated operation",
  "planned" => "planned operation",
  "unsupported" => "unsupported operation"
}.freeze

def inventory_date
  line = File.foreach(CAPABILITY_MAP).find { |candidate| candidate.start_with?("Inventory date:") }
  raise "missing inventory date in #{CAPABILITY_MAP}" unless line

  line[/\d{4}-\d{2}-\d{2}/]
end

def parse_observed_operations
  operations = {}
  section = nil
  in_operations = false
  in_cpu_only = false

  File.foreach(CAPABILITY_MAP, chomp: true) do |line|
    if line == "## Published operation capabilities"
      in_operations = true
      next
    end
    if line == "## Additional CPU numerical capabilities"
      in_operations = false
      in_cpu_only = true
      next
    end
    if line == "## Quant-format declarations"
      in_cpu_only = false
      next
    end

    if in_operations && line.start_with?("### ")
      section = line.delete_prefix("### ")
      next
    end

    if in_operations && line =~ /^\| `([^`]+)` \|/
      family = DISPLAY_FAMILIES.fetch(section) do
        raise "unknown capability-map family #{section.inspect}"
      end
      operations[Regexp.last_match(1)] = family
    elsif in_cpu_only && line =~ /^\| `([^`]+)` \| CPU \|/
      name = Regexp.last_match(1)
      operations[name] = CPU_ONLY_FAMILIES.fetch(name)
    end
  end

  raise "expected 263 observed operation IDs, got #{operations.size}" unless operations.size == 263

  operations
end

def build_registry
  normalization = YAML.load_file(NORMALIZATION)
  aliases = normalization.fetch("aliases")
  family_overrides = normalization.fetch("family_overrides", {})
  aggregates = normalization.fetch("aggregates")
  planned = normalization.fetch("planned_operations")
  observed = parse_observed_operations

  callable = {}
  aggregate_records = {}

  observed.each do |source_name, family|
    if aggregates.include?(source_name)
      aggregate_records[source_name] = {
        "family" => family,
        "source_ids" => [source_name],
        "maturity" => "observed",
        "callable" => false
      }
      next
    end

    canonical_name = aliases.fetch(source_name, source_name)
    canonical_family = family_overrides.fetch(canonical_name, family)
    record = (callable[canonical_name] ||= {
      "family" => canonical_family,
      "kind" => "operation",
      "maturity" => "observed",
      "abi" => normalization.fetch("abi"),
      "source_ids" => []
    })
    if record.fetch("family") != canonical_family
      raise "alias #{source_name} crosses families: #{record.fetch('family')} vs #{canonical_family}"
    end
    record.fetch("source_ids") << source_name
  end

  planned.each do |name, details|
    raise "planned operation duplicates observed canonical name #{name}" if callable.key?(name)

    callable[name] = {
      "family" => details.fetch("family"),
      "kind" => details.fetch("kind"),
      "maturity" => "planned",
      "abi" => normalization.fetch("abi"),
      "source_ids" => []
    }
  end

  callable.each_value { |record| record.fetch("source_ids").sort! }
  {
    "schema_version" => normalization.fetch("schema_version"),
    "inventory_date" => inventory_date,
    "abi" => {
      "name" => normalization.fetch("abi"),
      "cpp_signature" => "quixicore::contract::Status(const quixicore::contract::KernelCall&) noexcept",
      "header" => "include/quixicore/contract/kernel_abi.hpp"
    },
    "naming" => {
      "style" => "semantic_snake_case",
      "variant_rule" => "dtype, format, layout, architecture, tile, and route are descriptors or backend variants"
    },
    "operations" => callable.sort.to_h,
    "aggregates" => aggregate_records.sort.to_h
  }
end

def cpp_string(value)
  value.to_s.dump
end

def operations_header(registry)
  operations = registry.fetch("operations")
  lines = []
  lines << "#pragma once"
  lines << ""
  lines << "#include <array>"
  lines << "#include <cstdint>"
  lines << "#include <string_view>"
  lines << ""
  lines << "namespace quixicore::contract {"
  lines << ""
  lines << "enum class OperationId : std::uint16_t {"
  operations.each_key { |name| lines << "  #{name}," }
  lines << "};"
  lines << ""
  lines << "struct OperationDescriptor {"
  lines << "  OperationId id;"
  lines << "  std::string_view name;"
  lines << "  std::string_view family;"
  lines << "  std::string_view kind;"
  lines << "  std::string_view maturity;"
  lines << "};"
  lines << ""
  lines << "inline constexpr std::array<OperationDescriptor, #{operations.size}> kOperations{{"
  operations.each do |name, record|
    lines << "    {OperationId::#{name}, #{cpp_string(name)}, #{cpp_string(record.fetch('family'))}, #{cpp_string(record.fetch('kind'))}, #{cpp_string(record.fetch('maturity'))}},"
  end
  lines << "}};"
  lines << ""
  lines << "[[nodiscard]] constexpr std::string_view operation_name(OperationId id) noexcept {"
  lines << "  for (const auto& operation : kOperations) {"
  lines << "    if (operation.id == id) return operation.name;"
  lines << "  }"
  lines << "  return {};"
  lines << "}"
  lines << ""
  lines << "}  // namespace quixicore::contract"
  lines << ""
  lines.join("\n")
end

def git_revision(path)
  output, status = Open3.capture2("git", "rev-parse", "--short=12", "HEAD", chdir: path)
  raise "cannot read git revision for #{path}" unless status.success?

  output.strip
end

def backend_stubs(backend, path, registry)
  manifest_path = File.join(path, ".quixicore", "kernels.yaml")
  manifest = backend == "cpu" ? {} : YAML.load_file(manifest_path)
  exact = manifest.fetch("operations", {})
  families = manifest.fetch("families", {})
  stubs = {}

  registry.fetch("operations").each do |name, record|
    if record.fetch("maturity") == "planned"
      stubs[name] = record.merge("reason" => "planned contract; no backend implementation evidence")
      next
    end

    if backend == "cpu"
      next
    end

    exact_statuses = record.fetch("source_ids").each_with_object([]) do |source_id, statuses|
      status = exact.dig(source_id, "status")
      statuses << status if status
    end
    next if exact_statuses.any? { |status| COVERED_STATUSES.include?(status) }

    noncovered_exact = exact_statuses.find { |status| EXACT_GAPS.key?(status) }
    if noncovered_exact
      reason = EXACT_GAPS.fetch(noncovered_exact)
    else
      manifest_family = MANIFEST_FAMILIES.fetch(record.fetch("family"), record.fetch("family"))
      family_status = families.dig(manifest_family, "status")
      reason = family_status ? FAMILY_GAPS.fetch(family_status) : "no family claim"
    end
    stubs[name] = record.merge("reason" => reason)
  end

  [stubs, git_revision(path)]
end

def stub_header(backend, stubs)
  namespace = "quixicore::#{backend}::contract_stubs"
  lines = []
  lines << "#pragma once"
  lines << ""
  lines << "// Generated by QuixiCore/tools/sync_kernel_contract.rb. Do not edit."
  lines << "// These adapters are scaffolding only and make no implementation claim."
  lines << ""
  lines << "#include <array>"
  lines << ""
  lines << "#include \"quixicore/contract/kernel_abi.hpp\""
  lines << ""
  lines << "namespace #{namespace} {"
  lines << ""
  lines << "using quixicore::contract::KernelCall;"
  lines << "using quixicore::contract::Status;"
  lines << "using quixicore::contract::StubDescriptor;"
  lines << ""
  stubs.each do |name, record|
    lines << "[[nodiscard]] inline Status #{name}(const KernelCall&) noexcept {"
    lines << "  return quixicore::contract::not_implemented(#{cpp_string(name)}, #{cpp_string(record.fetch('reason'))});"
    lines << "}"
    lines << ""
  end
  lines << "inline constexpr std::array<StubDescriptor, #{stubs.size}> kStubs{{"
  stubs.each do |name, record|
    lines << "    {#{cpp_string(name)}, #{cpp_string(record.fetch('family'))}, #{cpp_string(record.fetch('reason'))}, &#{name}},"
  end
  lines << "}};"
  lines << ""
  lines << "}  // namespace #{namespace}"
  lines << ""
  lines.join("\n")
end

def backend_contract_header(backend, stubs)
  lines = []
  lines << "#pragma once"
  lines << ""
  lines << "// Generated canonical contract include for the #{backend} backend."
  lines << "// Native optimized APIs remain backend-owned behind this adapter surface."
  lines << ""
  lines << "#include \"quixicore/contract/kernel_abi.hpp\""
  lines << "#include \"quixicore/contract/operations.hpp\""
  lines << "#include \"quixicore/#{backend}/contract_stubs.hpp\""
  lines << ""
  lines << "namespace quixicore::#{backend}::contract_api {"
  lines << ""
  lines << "[[nodiscard]] inline quixicore::contract::Status dispatch("
  lines << "    quixicore::contract::OperationId operation,"
  lines << "    const quixicore::contract::KernelCall& call) noexcept {"
  lines << "  switch (operation) {"
  stubs.each_key do |name|
    lines << "    case quixicore::contract::OperationId::#{name}:"
    lines << "      return quixicore::#{backend}::contract_stubs::#{name}(call);"
  end
  lines << "    default:"
  lines << "      break;"
  lines << "  }"
  lines << "  const auto name = quixicore::contract::operation_name(operation);"
  lines << "  return quixicore::contract::adapter_not_wired("
  lines << "      name.empty() ? \"unknown_operation\" : name.data());"
  lines << "}"
  lines << ""
  lines << "}  // namespace quixicore::#{backend}::contract_api"
  lines << ""
  lines.join("\n")
end

def stub_manifest(backend, revision, registry, stubs)
  entries = stubs.transform_values do |record|
    {
      "family" => record.fetch("family"),
      "kind" => record.fetch("kind"),
      "reason" => record.fetch("reason"),
      "source_ids" => record.fetch("source_ids")
    }
  end
  {
    "schema_version" => 0.2,
    "backend" => backend,
    "backend_revision" => revision,
    "inventory_date" => registry.fetch("inventory_date"),
    "abi" => registry.dig("abi", "name"),
    "generated_from" => [
      "QuixiCore/registry/operations.yaml",
      ".quixicore/kernels.yaml"
    ],
    "canonical_operation_count" => registry.fetch("operations").size,
    "stub_count" => stubs.size,
    "stubs" => entries
  }
end

def generated_files(registry)
  files = {
    OPERATIONS_REGISTRY => YAML.dump(registry),
    OPERATIONS_HEADER => operations_header(registry)
  }
  abi = File.read(ABI_HEADER)

  BACKENDS.each do |backend, path|
    stubs, revision = backend_stubs(backend, path, registry)
    include_root = File.join(path, "include", "quixicore")
    files[File.join(include_root, "contract", "kernel_abi.hpp")] = abi
    files[File.join(include_root, "contract", "operations.hpp")] = operations_header(registry)
    files[File.join(include_root, backend, "contract_stubs.hpp")] = stub_header(backend, stubs)
    files[File.join(include_root, backend, "contract.hpp")] = backend_contract_header(backend, stubs)
    files[File.join(path, ".quixicore", "kernel-stubs.yaml")] = YAML.dump(
      stub_manifest(backend, revision, registry, stubs)
    )
  end

  files
end

check = ARGV.delete("--check")
abort "usage: #{File.basename($PROGRAM_NAME)} [--check]" unless ARGV.empty?

registry = build_registry
files = generated_files(registry)

if check
  stale = files.each_with_object([]) do |(path, expected), paths|
    paths << path unless File.file?(path) && File.read(path) == expected
  end
  unless stale.empty?
    warn "generated kernel-contract files are stale:"
    stale.each { |path| warn "  #{path}" }
    exit 1
  end
  puts "kernel contract is synchronized (#{registry.fetch('operations').size} canonical operations)"
else
  files.each do |path, content|
    FileUtils.mkdir_p(File.dirname(path))
    File.write(path, content) unless File.file?(path) && File.read(path) == content
  end
  puts "wrote #{files.size} generated files for #{registry.fetch('operations').size} canonical operations"
end
