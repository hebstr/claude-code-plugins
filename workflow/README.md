# workflow

Project workflow automation: file consistency sweeps, cross-repo synchronization, prose editing, session handoffs, source-backed recommendations, and documentation layout audits.

Every skill is **explicit-invocation only**: invoked by typing its slash command, never auto-triggered from natural language.

## Install

```bash
claude plugin marketplace add hebstr/claude-code-plugins
claude plugin install workflow@hebstr
```

## Skills

| Skill | Invocation | Purpose |
|---|---|---|
| [`sync`](./sync/) | `/workflow:sync` | Scans all project files for staleness and updates them. Always runs a cross-repo semantic consistency pass with parallel agents. |
| [`write`](./write/) | `/workflow:write` | Strips AI writing patterns and rewrites prose to read naturally. Routes to a French or English reference per text language; includes a bilingual review mode (FR-EN parity, typography, false friends). |
| [`continue`](./continue/) | `/workflow:continue` | Flushes durable facts to memory, updates `.claude/PLAN.md`, and prints a continuation prompt. No handoff document: PLAN.md and memory are authoritative. |
| [`reco`](./reco/) | `/workflow:reco` | Deep recommendation backed by external sources. Parallel agents pull official docs (WebFetch) and community practice (WebSearch); the skill synthesizes a structured recommendation with verified citations. |
| [`doc-structure`](./doc-structure/) | `/workflow:doc-structure` | Audits documentation layout (CLAUDE.md vs README.md), proposes verbatim migrations of misplaced prose, and updates the CLAUDE.md index. |

## Per-skill details

### `/workflow:sync`

Performs a single-repo sweep for drift between recently changed files and the rest of the tree (counts, references, doc tables, permission/config gates). Then runs a cross-repo semantic scan with parallel agents that check consistency between sibling repos sharing concepts (shared docs, shared manifests, mirrored APIs).

### `/workflow:write`

Detects the source language from the text itself and loads the matching FR or EN reference, then edits in place without commentary. Bilingual review mode applies to FR-EN parity work (release notes, mixed-language docs).

### `/workflow:continue`

Writes durable facts from the session to memory, updates `.claude/PLAN.md` (creating it only if absent and the session had a multi-step task), and prints a minimal continuation prompt directly. No file is written for the prompt. The prompt adapts to what was actually done: it lists written memory files by name and includes PLAN.md references only when PLAN.md was written or updated.

### `/workflow:reco`

Spawns two parallel agents (official documentation via WebFetch, community practice via WebSearch), then produces a structured output (my take, tradeoffs, official docs, community, final recommendation). URLs are verified before being cited. Disagreement between sources is surfaced, not papered over. Use it when external grounding matters; for an unsourced recommendation based only on what Claude already knows, just ask directly.

### `/workflow:doc-structure`

Walks a 5-phase workflow (Discovery, Audit, Migration, Index updates, Verification) to classify documentation content as HOW (operational, belongs in CLAUDE.md) or WHY (architectural, belongs in README.md), then proposes verbatim moves with per-file approval. Generated-source files (`README.Rmd`/`README.qmd`) are detected and the source is edited rather than the generated target.

## Common usage

```bash
# At session end: sweep the current project for staleness and cross-repo inconsistencies
/workflow:sync

# Strip AI slop patterns from a draft
/workflow:write

# Deep, source-backed recommendation on a topic
/workflow:reco "topic"

# Audit documentation layout for the current project
/workflow:doc-structure

# At session end or near context limit: flush memory, update PLAN.md, and print a continuation prompt
/workflow:continue
```

## Requirements

**Required:**

- [Claude Code](https://claude.com/claude-code) with plugin marketplaces enabled
- `git` (for `workflow:sync`; outside a git repo, the skill asks the user for the file list)

No other external dependencies.

## License

[MIT](../LICENSE.md)
