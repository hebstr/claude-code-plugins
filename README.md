# Claude Code plugins

![CI](https://github.com/hebstr/claude-code-plugins/actions/workflows/ci.yml/badge.svg)
![Release](https://img.shields.io/github/v/release/hebstr/claude-code-plugins)

Two plugins of [Claude Code](https://claude.com/claude-code) skills: `audit` (review workflows) and `workflow` (project automation). Most skills are invoked via slash command rather than auto-triggered; see each plugin's README for exact invocations. Background on the underlying mechanism: [Claude Skills documentation](https://support.claude.com/en/articles/12512180-using-skills-in-claude).

## Install

Add the marketplace, then install plugins individually:

```bash
claude plugin marketplace add hebstr/claude-code-plugins
claude plugin install audit@hebstr
claude plugin install workflow@hebstr
```

## Plugins

### `audit`

Code, skill, and MCP review workflows: orchestrated walkthroughs, full-project audits, adversarial critique, and circularity-aware cross-model review.

| Skill | Purpose |
|---|---|
| [`walkthrough`](./audit/walkthrough/) | Interactive, point-by-point walkthrough of any review report: re-evaluates findings, proposes fixes, checks impacted files for regressions |
| [`sweep`](./audit/sweep/) | Full-coverage project review with parallel specialist agents (architecture, quality, tests, docs), consolidated into a single deduplicated report |
| [`blindspot`](./audit/blindspot/) | Circularity-aware orchestrator that detects when a reviewer shares its target's codebase or model family, then injects cross-model judging via OpenRouter |
| [`skill-adversary`](./audit/skill-adversary/) | Adversarial critic for Claude Code skills: finds trigger edge cases, instruction ambiguities, cross-file coherence issues, and gaps |
| [`mcp-adversary`](./audit/mcp-adversary/) | Adversarial critic for MCP servers: finds inter-tool discrimination issues, schema anti-patterns, semantic drift, and undocumented workflow dependencies |

### `workflow`

Project workflow automation: file consistency sweeps, cross-repo synchronization, prose editing, session handoffs, source-backed recommendations, and documentation layout audits.

| Skill | Purpose |
|---|---|
| [`sync`](./workflow/sync/) | Scan all files, identify ones that are stale relative to recent changes, and update them. Always runs a cross-repo semantic consistency scan with parallel agents |
| [`write`](./workflow/write/) | Strip AI writing patterns from prose and rewrite it to sound human. Routes to a French or English reference based on the text being edited. Includes a bilingual review mode (FR↔EN parity, typography, faux amis) |
| [`continue`](./workflow/continue/) | Flush durable facts to memory, update `.claude/PLAN.md`, and print a minimal continuation prompt. No handoff document is written; PLAN.md and memory are the authoritative stores |
| [`reco`](./workflow/reco/) | Deep-mode recommendation backed by external sources. Parallel agents research official docs (WebFetch) and community practice (WebSearch), then synthesize a structured recommendation with verified citations |
| [`doc-structure`](./workflow/doc-structure/) | Audit project documentation layout (CLAUDE.md vs README.md), propose verbatim migrations of misplaced prose, and update the CLAUDE.md index. Adapted from solatis/claude-config:doc-sync |

## Requirements

**Required for both plugins:**

- [Claude Code](https://claude.com/claude-code) with plugin marketplaces enabled
- `git` (review targets and `workflow:sync` operate on git state)

**Optional, per feature.** Skills degrade gracefully when a dependency is absent: the missing feature is reported, and the rest of the skill continues.

| Dependency | Used by | Unlocks |
|---|---|---|
| `OPENROUTER_API_KEY` env var (+ `jq`) | [`audit:blindspot`](./audit/blindspot/), [`audit:walkthrough`](./audit/walkthrough/) | Cross-model judging and L2 cross-provider validation via OpenRouter |
| [Ouroboros](https://github.com/Q00/ouroboros) plugin | [`audit:walkthrough`](./audit/walkthrough/) | Consensus QA, evaluate + drift checks, lateral-think rescue |
| [`critical-code-reviewer`](https://github.com/posit-dev/skills) (posit-dev/skills) | [`audit:sweep`](./audit/sweep/) | Specialist code-review agent; sweep falls back to inline review when absent |
| [`r-lib`](https://github.com/posit-dev/skills) skills `testing-r-packages`, `r-package-development`, `cran-extrachecks` (posit-dev/skills) | [`audit:sweep`](./audit/sweep/) on R projects | R-specific test, package, and CRAN-readiness audits |
| `gh` CLI | [`audit:walkthrough`](./audit/walkthrough/) | PR body as evaluate context (falls back to latest commit message) |

The `workflow` plugin has no external dependencies beyond Claude Code and `git`. See [`audit/README.md`](./audit/README.md) for per-skill detail.

## License

[MIT](./LICENSE.md)
