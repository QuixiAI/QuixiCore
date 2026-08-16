# Backend Agent-Doc Templates

The backend repositories' `AGENTS.md`, `CLAUDE.md`, and `.claude/settings.json`
are generated from the templates in this directory by
`tools/sync_agent_docs.py`. Do not hand-edit shared sections in a backend repo;
edit the template (or `agents-params.json`) here and re-run the tool.

## Files

- `backend-AGENTS.md` — the AGENTS.md template. `<!-- qx:section <name> -->`
  starts an umbrella-owned shared section; `<!-- qx:slot <name> -->` marks a
  position where backend-owned free text lives. `{{param}}` placeholders are
  substituted from `agents-params.json`.
- `backend-CLAUDE.md` — the CLAUDE.md template. Fully generated; no slots.
- `backend-claude-settings.json` — the `.claude/settings.json` template. The
  `"{{settings_allow_extra}}"` element in the allow list is replaced by each
  backend's extra tool allowances. Fully generated; no slots.
- `agents-params.json` — per-backend parameter values and initial slot content.

## Ownership model

In a rendered backend file:

- `<!-- qx:shared:begin <name> v1 -->` … `<!-- qx:shared:end <name> -->` blocks
  are owned by the umbrella. `sync_agent_docs.py --check` compares them
  byte-for-byte against the rendered template and fails on drift.
- `<!-- qx:backend:begin <name> -->` … `<!-- qx:backend:end <name> -->` blocks
  are owned by the backend repo. Their content is preserved verbatim by
  `--write`; only their presence and position are checked.

`CLAUDE.md` and `.claude/settings.json` have no markers and are compared as
whole files.

## Workflow

```bash
python3 tools/sync_agent_docs.py --check              # verify the fleet
python3 tools/sync_agent_docs.py --check --diff       # show drift as diffs
python3 tools/sync_agent_docs.py --write              # regenerate shared blocks
python3 tools/sync_agent_docs.py --write --backend cpu
```

Backend repos are resolved as sibling checkouts under the umbrella root, per
the paths in `agents-params.json`. Changing shared wording means editing the
template here, bumping nothing (the `v1` in the marker is the marker-grammar
version, not a content version), and running `--write` across the fleet in the
same working session, then committing each repo.
