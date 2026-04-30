---
name: sync
description: Scan all files in the current directory and subdirectories, identify files that are stale relative to recent changes, and update them. Always performs a cross-repo semantic consistency scan with parallel agents. User-invocable only via /workflow:sync.
allowed-tools: Read Write Edit Glob Grep Agent
---

# Sync

Scan all files in the current working directory (recursively), identify files that are stale relative to uncommitted changes (staged + unstaged), and update them. Always includes a cross-repo semantic consistency scan with parallel agents.

## Context (injected at invocation)

**Modified files (staged + unstaged):**
!`git rev-parse --git-dir >/dev/null 2>&1 && { git diff --name-only 2>/dev/null; git diff --cached --name-only 2>/dev/null; } || echo "__NO_GIT__"`

**Directory listing:**
!`find . -type f ! -path './.git/*' ! -path '*/node_modules/*' ! -path '*/renv/*' ! -path '*/venv/*' ! -path '*/.venv/*' ! -path '*/vendor/*' ! -path '*/.Rproj.user/*' ! -path '*/dist/*' ! -path '*/_site/*' ! -path '*/_book/*' ! -path '*/_freeze/*' ! -path '*.lock' 2>/dev/null | sort`

## Workflow

### Step 1 — Parse context

From the injected context above, extract:
- **Modified files**: the list of files with uncommitted changes (staged + unstaged)
- **All files**: the full directory listing

If the modified files context contains `__NO_GIT__`, this directory is not a git repository.
In that case, ask the user which files were recently changed (or use file modification timestamps via `find . -type f -newer <reference> ...` if the user provides a reference point).
If neither git nor the user provides a list of modified files, tell the user and stop. Nothing to audit.

If the directory is a git repo but no modified files are detected (empty git diff), tell the user and stop. Nothing to audit.

### Step 2 — Dependency map

For each modified file, identify which unmodified files may depend on it. Use these heuristics:

| Modified file pattern | Likely dependents |
|----------------------|-------------------|
| `SKILL.md` | `CONTEXT.md`, `README.md`, all other `*.md` at the same directory level (e.g. `ROBUST.md`, `CHANGELOG.md`, `DEFERRED.md`), files in `agents/`, `docs/`, `templates/` |
| `R/*.R` | `tests/testthat/test-*.R`, `man/*.Rd`, `NAMESPACE`, `DESCRIPTION` |
| `src/*.py` or `*.py` | `tests/test_*.py`, `pyproject.toml`, `docs/` |
| `*.qmd` | `_quarto.yml`, `index.qmd` |
| Config files (`*.toml`, `*.yaml`, `*.yml`, `*.json`, `.env*`) | `README.md`, `docs/`, and any file that imports or parses the config |

In addition, always Grep for each modified filename across all unmodified files. The dependency set is the union of heuristic matches and Grep matches.

### Step 3 — Staleness check

For each dependent identified in Step 2, read it and assess consistency with the modified files. A file is **stale** if:
- It describes behavior or structure that has changed
- It contains outdated references, examples, or cross-references
- It lists items (features, backlog, design decisions) that no longer match the modified files

A file is **not stale** if its content remains consistent with the current state despite referencing modified files.

### Step 4 — Report

```
## Audit — [directory name]

Modified: [list] (N files)
Scanned: M dependents across K subdirectories

| File | Status | Issue |
|------|--------|-------|
| CONTEXT.md | STALE | Missing section about X |
| README.md | OK | — |

N stale / M checked.
```

### Step 5 — Update

Update each stale file with the minimal changes needed to restore consistency. After each edit, re-read the file to verify correctness. If the edit introduced an error, attempt one corrective edit; if still incorrect, revert to the original content, report the failure in the update summary, and move on.

Report:
```
Updated N files:
- CONTEXT.md: added X, updated Y
- agents/foo.md: fixed reference to Z
```

If no files are stale, say so. Then proceed to Step 6.

### Step 6 — Deep consistency scan

This step goes beyond surface-level cross-references. It checks semantic consistency across related repositories and within files — things that grep-based checks miss.

#### 6a — Identify related repos

From the modified files and directory structure, identify sibling repos or skill directories that could be affected by the changes. Heuristics:
- If `SKILL.md` or `allowed-tools` changed → check all sub-skill directories and the MCP server they reference
- If `server.py` or MCP tool files changed → check all skills that use those tools
- If `README.md` changed → check that it matches the actual tool list, phase table, architecture description

Build a **component list**: each entry is a directory path + a short description of what to check.

#### 6b — Spawn parallel agents

Launch one `Explore` agent per component (2–4 agents max). Each agent gets a focused, non-overlapping prompt:

Each agent should check:
1. **Structural**: do `allowed-tools` in frontmatter match what the body describes? Are all referenced MCP tools real?
2. **Semantic**: are step numbers sequential? Do parameter names in instructions match the actual tool signatures? Are descriptions accurate?
3. **Cross-repo**: do tool counts, tool names, and tool descriptions match between the MCP server and the skills that use them?
4. **Naming**: are tool/function/variable names consistent across references? (e.g., `search_s2` not `search_semantic_scholar`)

Each agent returns a list of issues with file paths and line numbers.

#### 6c — Triage and fix

Collect agent results. For each reported issue:
- **True positive**: fix it (same minimal edit rules as Step 5)
- **False positive**: skip it silently (do not report FPs to the user — they add noise)

Report using the same format as Step 5:
```
## Deep scan — N components checked

Agents: [component names]

| File | Issue | Fix |
|------|-------|-----|
| litrev-search/SKILL.md:67 | Step 0 after Step 1 | Reordered |
| DEFERRED.md:9 | search_semantic_scholar → search_s2 | Fixed typo |

Fixed N issues across M files.
```

If no true issues found, say so.

## Constraints

- **Minimal edits.** Only fix staleness. No refactoring, no style changes, no additions beyond restoring consistency.
- **No new files.** Update existing files only.
- **Transparent.** Always show the report table before updating. Then start issuing edits without an extra "shall I proceed?" prompt — the user validates each edit individually via the tool permission flow (Edit/Write approval dialogs are the only gate).
