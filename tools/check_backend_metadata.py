#!/usr/bin/env python3
"""Validate each sibling backend's .quixicore/backend.yaml against
registry/backend-metadata.schema.yaml.

The schema is JSON-Schema-shaped; this is a hand-rolled validator for exactly
the constructs it uses (required, enum, pattern, const, additional_properties,
typed arrays). Runs locally — CI cannot see the sibling checkouts. Stdlib
only; YAML via tools/qc_yaml.py.

Usage: python3 tools/check_backend_metadata.py   # exit 1 on any violation
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qc_yaml  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = qc_yaml.load_file(
    os.path.join(ROOT, "registry", "backend-metadata.schema.yaml")
)["schema"]

BACKEND_DIRS = [
    "QuixiCore-Metal", "QuixiCore-CUDA", "QuixiCore-ROCm",
    "QuixiCore-XPU", "QuixiCore-Gaudi", "QuixiCore-CPU",
]


def validate(doc, schema, path, problems):
    stype = schema.get("type")
    if stype == "object":
        if not isinstance(doc, dict):
            problems.append(f"{path}: expected object, got {type(doc).__name__}")
            return
        for key in schema.get("required") or []:
            if key not in doc:
                problems.append(f"{path}: missing required key '{key}'")
        props = schema.get("properties") or {}
        if schema.get("additional_properties") is False:
            for extra in doc:
                if extra not in props:
                    problems.append(f"{path}: unknown key '{extra}'")
        for key, value in doc.items():
            if key in props:
                validate(value, props[key], f"{path}.{key}", problems)
    elif stype == "string":
        if not isinstance(doc, str):
            problems.append(f"{path}: expected string, got {type(doc).__name__}")
            return
        enum = schema.get("enum")
        if enum and doc not in enum:
            problems.append(f"{path}: '{doc}' not in {enum!r}")
        pattern = schema.get("pattern")
        if pattern and not re.search(pattern, doc):
            problems.append(f"{path}: '{doc}' does not match {pattern}")
        const = schema.get("const")
        if const and doc != const:
            problems.append(f"{path}: '{doc}' != required constant '{const}'")
    elif stype == "array":
        if not isinstance(doc, list):
            problems.append(f"{path}: expected array, got {type(doc).__name__}")
            return
        min_items = schema.get("min_items")
        if min_items and len(doc) < min_items:
            problems.append(f"{path}: needs at least {min_items} item(s)")
        items = schema.get("items")
        if items:
            for i, item in enumerate(doc):
                validate(item, items, f"{path}[{i}]", problems)


def main():
    failures = 0
    for dirname in BACKEND_DIRS:
        file = os.path.join(ROOT, dirname, ".quixicore", "backend.yaml")
        if not os.path.exists(file):
            print(f"{dirname}: MISSING .quixicore/backend.yaml")
            failures += 1
            continue
        problems = []
        validate(qc_yaml.load_file(file), SCHEMA, dirname, problems)
        if problems:
            failures += 1
            print(f"{dirname}: FAIL")
            for p in problems:
                print(f"  {p}")
        else:
            print(f"{dirname}: ok")
    print(f"{'OK' if not failures else 'FAIL'}: backend metadata schema")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
