# workflow

Project workflow automation: file consistency sweeps, cross-repo synchronization, and prose editing.

## Install

```bash
claude plugin install workflow@hebstr
```

## Skills

| Skill | Invocation | Purpose |
|---|---|---|
| [`sync`](./sync/) | `/workflow:sync` | Scan all files in the current directory and subdirectories, identify ones that are stale relative to recent changes, and update them. Always runs a cross-repo semantic consistency scan with parallel agents. |
| [`write`](./write/) | `/workflow:write` | Strip AI writing patterns from prose and rewrite it to sound human. Routes to a French or English reference based on the text being edited. Includes a bilingual review mode (FR↔EN parity, typography, faux amis). |

## What it does

`/workflow:sync` performs a single-repo sweep (drift between recently changed files and the rest of the tree: counts, references, doc tables, permission/config gates) followed by a cross-repo semantic scan (parallel agents check consistency between sibling repos sharing concepts: shared docs, shared manifests, mirrored APIs).

`/workflow:write` runs only when the user explicitly types `/workflow:write`; it does not auto-trigger on mentions of "draft", "polish", "rewrite", "relis", "corrige", etc. It detects the source language from the text itself and loads the matching reference (`references/write-fr-core.md` for French, `references/write-en.md` for English), then edits in place without commentary. The French reference is split: a register-neutral core (~230 lines, always loaded) plus an exhaustive extended (`references/write-fr-extended.md`, ~680 lines) loaded only for bilingual reviews, deep passes, or edge cases. Bilingual review mode kicks in for FR↔EN parity work (release notes, mixed-language docs).

Both skills are user-invocable only; neither auto-triggers.

## Requirements

[Claude Code](https://claude.com/claude-code) with plugin marketplaces enabled.
