# workflow

Project workflow automation — file consistency sweeps, cross-repo synchronization, and prose editing.

## Install

```bash
claude plugin install workflow@hebstr
```

## Skills

| Skill | Invocation | Purpose |
|---|---|---|
| [`sync`](./sync/) | `/sync` | Scan all files in the current directory and subdirectories, identify ones that are stale relative to recent changes, and update them. Always runs a cross-repo semantic consistency scan with parallel agents. |
| [`write`](./write/) | `/write` | Strip AI writing patterns from prose and rewrite it to sound human. Routes to a French or English reference based on the text being edited. Includes a bilingual review mode (FR↔EN parity, typography, faux amis) and a release-note template mode. |

## What it does

`/sync` performs a single-repo sweep (drift between recently changed files and the rest of the tree — counts, references, doc tables, permission/config gates) followed by a cross-repo semantic scan (parallel agents check consistency between sibling repos sharing concepts: shared docs, shared manifests, mirrored APIs).

`/write` activates only on explicit editing requests (draft, polish, rewrite, relis, corrige, etc.). It detects the source language from the text itself, loads the matching reference (`references/write-fr.md` or `references/write-en.md`), and edits in place without commentary. Bilingual review mode kicks in for FR↔EN parity work (release notes, mixed-language docs).

User-invocable only — neither skill auto-triggers.

## Requirements

[Claude Code](https://claude.com/claude-code) with plugin marketplaces enabled.
