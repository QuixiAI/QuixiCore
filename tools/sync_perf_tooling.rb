#!/usr/bin/env ruby
# frozen_string_literal: true

# Distribute the shared perf tooling to the sibling backend checkouts, or
# verify (--check) that the committed copies still match the canonicals.
#
# Canonical files (edit these, never the copies):
#   tools/templates/run_bench_core.sh  -> <backend>/perf/harness/run_bench_core.sh
#   scripts/perf_diff.py               -> <backend>/perf/harness/perf_diff.py
#
# The copies are committed in each backend repo so a standalone clone works;
# six hand-maintained variants of the guard logic is exactly the drift this
# repo's sync pattern (tools/sync_kernel_contract.rb) exists to prevent.
#
# Usage:
#   ruby tools/sync_perf_tooling.rb           # write copies into all six
#   ruby tools/sync_perf_tooling.rb --check   # verify, exit 1 on drift

ROOT = File.expand_path("..", __dir__)

BACKENDS = {
  "metal" => "QuixiCore-Metal",
  "cuda"  => "QuixiCore-CUDA",
  "rocm"  => "QuixiCore-ROCm",
  "xpu"   => "QuixiCore-XPU",
  "gaudi" => "QuixiCore-Gaudi",
  "cpu"   => "QuixiCore-CPU",
}.freeze

FILES = {
  File.join(ROOT, "tools", "templates", "run_bench_core.sh") => "run_bench_core.sh",
  File.join(ROOT, "scripts", "perf_diff.py") => "perf_diff.py",
}.freeze

check = ARGV.include?("--check")
problems = []
written = 0

BACKENDS.each do |name, dir|
  repo = File.join(ROOT, dir)
  unless Dir.exist?(repo)
    problems << "#{name}: sibling checkout #{dir} not found"
    next
  end
  harness = File.join(repo, "perf", "harness")
  FILES.each do |src, base|
    dst = File.join(harness, base)
    expected = File.read(src)
    actual = File.exist?(dst) ? File.read(dst) : nil
    next if actual == expected

    if check
      problems << "#{name}: perf/harness/#{base} #{actual.nil? ? 'missing' : 'drifted'}"
    else
      require "fileutils"
      FileUtils.mkdir_p(harness)
      File.write(dst, expected)
      File.chmod(0o755, dst) if base.end_with?(".sh", ".py")
      written += 1
      puts "wrote #{dir}/perf/harness/#{base}"
    end
  end
end

if problems.any?
  problems.each { |p| puts "drift: #{p}" }
  exit 1
end
puts check ? "perf tooling is synchronized (#{BACKENDS.size} backends)" : "perf tooling synced (#{written} file(s) written)"
