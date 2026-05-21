# workflow

Project workflow automation: file consistency sweeps, cross-repo synchronization, prose editing, session handoffs, source-backed recommendations, and documentation layout audits.

## Install

```bash
claude plugin install workflow@hebstr
```

## Skills

| Skill | Invocation | Purpose |
|---|---|---|
| [`sync`](./sync/) | `/workflow:sync` | Scan all files in the current directory and subdirectories, identify ones that are stale relative to recent changes, and update them. Always runs a cross-repo semantic consistency scan with parallel agents. |
| [`write`](./write/) | `/workflow:write` | Strip AI writing patterns from prose and rewrite it to sound human. Routes to a French or English reference based on the text being edited. Includes a bilingual review mode (FR↔EN parity, typography, faux amis). |
| [`continue`](./continue/) | `/workflow:continue` | Flush durable facts to memory, update `.claude/PLAN.md`, and print a minimal continuation prompt. No handoff document is written: PLAN.md and memory are the authoritative stores. |
| [`reco`](./reco/) | `/workflow:reco` | Deep-mode recommendation backed by external sources. Spawns parallel agents to research official documentation (WebFetch) and community practice (WebSearch), then synthesizes a structured recommendation with verified citations. Light-mode recommendations (ending a choice-presenting reply with your own pick) live in CLAUDE.md as a communication rule, not in this skill. |
| [`doc-structure`](./doc-structure/) | `/workflow:doc-structure` | Audit project documentation layout (CLAUDE.md vs README.md), propose verbatim migrations of misplaced prose, and update the CLAUDE.md index. Adapted from solatis/claude-config:doc-sync. |

## What it does

`/workflow:sync` performs a single-repo sweep (drift between recently changed files and the rest of the tree: counts, references, doc tables, permission/config gates) followed by a cross-repo semantic scan (parallel agents check consistency between sibling repos sharing concepts: shared docs, shared manifests, mirrored APIs).

`/workflow:write` runs only when the user explicitly types `/workflow:write`; it does not auto-trigger on mentions of "draft", "polish", "rewrite", "relis", "corrige", etc. It detects the source language from the text itself and loads the matching reference (`references/write-fr-core.md` for French, `references/write-en.md` for English), then edits in place without commentary. The French reference is split: a register-neutral core (~230 lines, always loaded) plus an exhaustive extended (`references/write-fr-extended.md`, ~680 lines) loaded only for bilingual reviews, deep passes, or edge cases. Bilingual review mode kicks in for FR↔EN parity work (release notes, mixed-language docs).

`/workflow:continue` runs only when the user explicitly types `/workflow:continue`. It writes durable facts from the session to memory, updates `.claude/PLAN.md` (creating it only if absent and the session had a multi-step task), and prints a minimal continuation prompt directly: no file is written for the prompt. The prompt adapts to what was actually done: it lists written memory files by name and includes PLAN.md references only when PLAN.md was written or updated.

`/workflow:reco` runs only when the user explicitly types `/workflow:reco`. It spawns two parallel agents (official documentation via WebFetch, community practice via WebSearch), then produces a structured output (my take, tradeoffs, official docs, community, final recommendation). URLs are verified before being cited. Disagreement between sources is surfaced, not papered over. Use it when external grounding matters; the lighter "what do you recommend?" reflex is already handled by the CLAUDE.md communication rule.

`/workflow:doc-structure` is captured from the 2026-05-16 audit of `solatis/claude-config:doc-sync`. It walks a 5-phase workflow (Discovery, Audit, Migration, Index updates, Verification) to classify documentation content as HOW (operational, belongs in CLAUDE.md) or WHY (architectural, belongs in README.md), then proposes verbatim moves with per-file approval. Phase 1 scans an explicit short list of paths (`<project>/CLAUDE.md`, `<project>/.claude/CLAUDE.md`, `<project>/README.{md,Rmd,qmd}`); generated-source files (`README.Rmd`/`README.qmd`) are detected and the source is edited rather than the generated target.

All skills are user-invocable only; none auto-triggers.

## Requirements

[Claude Code](https://claude.com/claude-code) with plugin marketplaces enabled. `workflow:sync` additionally uses `git` to detect modified files; outside a git repo, it asks the user to provide the file list. No other external dependencies.
