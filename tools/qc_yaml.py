"""Minimal YAML loader for QuixiCore's registry and manifest files.

Python's standard library has no YAML parser and the repo's tooling is
deliberately dependency-free, so this module implements exactly the subset
those files use: block mappings and sequences by indentation, flow mappings
and sequences, single/double-quoted and plain scalars, full-line comments,
and int/float/bool/null coercion. It is validated against Ruby Psych's
parse of every consumed file (see tools/sync_kernel_contract.py history) and
fails loudly on anything outside the subset rather than guessing.

Not supported (not used by these files): anchors/aliases, tags, multi-line
block scalars (| and >), multi-document streams, complex keys.
"""

import re

_NUM_INT = re.compile(r"^-?\d+$")
_NUM_FLOAT = re.compile(r"^-?\d+\.\d+([eE][+-]?\d+)?$")


class YamlError(ValueError):
    pass


def _unquote_double(s):
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            if i + 1 >= len(s):
                raise YamlError(f"dangling escape in {s!r}")
            n = s[i + 1]
            mapping = {"\\": "\\", '"': '"', "n": "\n", "t": "\t", "0": "\0"}
            if n not in mapping:
                raise YamlError(f"unsupported escape \\{n} in {s!r}")
            out.append(mapping[n])
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _scalar(text):
    text = text.strip()
    if text == "" or text == "~" or text == "null":
        return None
    if text.startswith('"'):
        if not text.endswith('"') or len(text) < 2:
            raise YamlError(f"unterminated double quote: {text!r}")
        return _unquote_double(text[1:-1])
    if text.startswith("'"):
        if not text.endswith("'") or len(text) < 2:
            raise YamlError(f"unterminated single quote: {text!r}")
        return text[1:-1].replace("''", "'")
    if text.startswith("{"):
        return _flow(text)
    if text.startswith("["):
        return _flow(text)
    if text == "true":
        return True
    if text == "false":
        return False
    if _NUM_INT.match(text):
        return int(text)
    if _NUM_FLOAT.match(text):
        return float(text)
    return text


def _split_flow(body):
    """Split a flow body on top-level commas."""
    parts, depth, start, in_s, in_d = [], 0, 0, False, False
    for i, c in enumerate(body):
        if in_s:
            in_s = c != "'"
            continue
        if in_d:
            in_d = c != '"'
            continue
        if c == "'":
            in_s = True
        elif c == '"':
            in_d = True
        elif c in "{[":
            depth += 1
        elif c in "}]":
            depth -= 1
        elif c == "," and depth == 0:
            parts.append(body[start:i])
            start = i + 1
    tail = body[start:]
    if tail.strip():
        parts.append(tail)
    return parts


def _flow(text):
    text = text.strip()
    if text.startswith("{"):
        if not text.endswith("}"):
            raise YamlError(f"unterminated flow mapping: {text!r}")
        body = text[1:-1].strip()
        result = {}
        if body:
            for part in _split_flow(body):
                if ":" not in part:
                    raise YamlError(f"flow mapping entry without colon: {part!r}")
                k, v = part.split(":", 1)
                result[_scalar(k)] = _scalar(v)
        return result
    if text.startswith("["):
        if not text.endswith("]"):
            raise YamlError(f"unterminated flow sequence: {text!r}")
        body = text[1:-1].strip()
        return [_scalar(p) for p in _split_flow(body)] if body else []
    raise YamlError(f"not a flow collection: {text!r}")


def _lines(text):
    out = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.strip() == "---":
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if "\t" in raw[:indent]:
            raise YamlError("tab indentation is not supported")
        out.append((indent, raw.strip()))
    return out


def _key_split(content):
    """Split 'key: value' / 'key:' at the first colon ending the key."""
    if content.startswith(("'", '"')):
        raise YamlError(f"quoted keys are not supported: {content!r}")
    m = re.match(r"^([^:#]+?):(?:\s+(.*))?$", content)
    if not m:
        raise YamlError(f"expected a mapping entry: {content!r}")
    return m.group(1).strip(), m.group(2)


_MAPPISH = re.compile(r"^[^:#\s][^:#]*:(\s|$)")


def _parse_block(lines, i, indent):
    """Parse the block starting at lines[i] whose items sit at `indent`."""
    if lines[i][1].startswith("- ") or lines[i][1] == "-":
        seq = []
        while i < len(lines) and lines[i][0] == indent and (
            lines[i][1].startswith("- ") or lines[i][1] == "-"
        ):
            item = lines[i][1][1:].strip()
            i += 1
            # gather this item's continuation lines (deeper than the dash)
            sub = []
            while i < len(lines) and lines[i][0] > indent:
                sub.append(lines[i])
                i += 1
            if item.startswith(("{", "[")):
                if sub:
                    raise YamlError(f"unexpected indent under flow item {item!r}")
                seq.append(_scalar(item))
            elif _MAPPISH.match(item) or (not item and sub):
                # a mapping (or nested block) spread across the item lines
                item_lines = ([(indent + 2, item)] if item else []) + sub
                value, j = _parse_block(item_lines, 0, item_lines[0][0])
                if j != len(item_lines):
                    raise YamlError(
                        f"trailing content in sequence item near {item!r}"
                    )
                seq.append(value)
            elif sub:
                raise YamlError(f"unexpected indent under sequence item {item!r}")
            else:
                seq.append(_scalar(item))
        return seq, i
    mapping = {}
    while i < len(lines) and lines[i][0] == indent:
        ind, content = lines[i]
        if content.startswith("- "):
            break
        key, rest = _key_split(content)
        if rest in (">", ">-", "|", "|-"):
            i += 1
            body = []
            while i < len(lines) and lines[i][0] > indent:
                body.append(lines[i][1])
                i += 1
            joiner = " " if rest.startswith(">") else "\n"
            value = joiner.join(body)
            if not rest.endswith("-"):
                value += "\n"
            mapping[key] = value
        elif rest is not None and rest != "":
            mapping[key] = _scalar(rest)
            i += 1
            if i < len(lines) and lines[i][0] > indent:
                raise YamlError(
                    f"multi-line plain scalars are not supported (near {content!r})"
                )
        else:
            i += 1
            if i < len(lines) and lines[i][0] > indent:
                value, i = _parse_block(lines, i, lines[i][0])
            elif i < len(lines) and lines[i][0] == indent and (
                lines[i][1].startswith("- ") or lines[i][1] == "-"
            ):
                value, i = _parse_block(lines, i, indent)
            else:
                value = None
            mapping[key] = value
    if i < len(lines) and lines[i][0] > indent:
        raise YamlError(f"unexpected indent at {lines[i][1]!r}")
    return mapping, i


def load(text):
    lines = _lines(text)
    if not lines:
        return None
    value, i = _parse_block(lines, 0, lines[0][0])
    if i != len(lines):
        raise YamlError(f"trailing content from {lines[i][1]!r}")
    return value


def load_file(path):
    with open(path) as f:
        return load(f.read())
