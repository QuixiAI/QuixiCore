#!/usr/bin/env bash
#
# Run every cross-repo consistency check the umbrella defines. CI runs the
# umbrella-only subset (see .github/workflows/contracts.yml); this script is
# the local superset that can see the sibling backend checkouts. Run it before
# committing umbrella changes and after finishing a backend phase.

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

rc=0
step() {
    local label="$1"
    shift
    echo "==> $label"
    if ! "$@"; then
        echo "FAILED: $label" >&2
        rc=1
    fi
    echo
}

step "quant vectors match the generator" python3 scripts/gen_quant_vectors.py --check
step "bench fixture matches the reporting format" python3 scripts/perf_diff.py validate test-vectors/bench/sample-run
step "matrix status symbols" python3 scripts/lint_matrices.py
step "kernel contract is synchronized" ruby tools/sync_kernel_contract.rb --check
step "perf tooling is synchronized" ruby tools/sync_perf_tooling.rb --check
step "backend metadata matches the schema" ruby tools/check_backend_metadata.rb
step "agent docs match the templates" python3 tools/sync_agent_docs.py --check
step "notebooks are canonical" python3 tools/perf_notebook.py check QuixiCore-*/perf/optimization_status.md

if [ -f scripts/gen_format_conformance.py ]; then
    step "format conformance table is generated" python3 scripts/gen_format_conformance.py --check
fi

if [ "$rc" -eq 0 ]; then
    echo "fleet check: all green"
else
    echo "fleet check: FAILURES above" >&2
fi
exit "$rc"
