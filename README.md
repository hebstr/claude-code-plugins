# Claude Code plugins

![CI](https://github.com/hebstr/claude-code-plugins/actions/workflows/ci.yml/badge.svg)
![Release](https://img.shields.io/github/v/release/hebstr/claude-code-plugins)

Two [Claude Code](https://claude.com/claude-code) plugins bundling slash-command skills: `audit` (review workflows) and `workflow` (project workflow automation). Each skill is invoked explicitly via its slash command.
See each plugin's README for skill-level details. See the [Claude Skills documentation](https://support.claude.com/en/articles/12512180-using-skills-in-claude) for how Claude Skills work.

## Install

Add the marketplace:

```bash
claude plugin marketplace add hebstr/claude-code-plugins
```

Then install plugins individually:

```bash
claude plugin install audit@hebstr
claude plugin install workflow@hebstr
```

## Plugins

### `audit`

Review workflows for code, Claude Code skills and MCP servers. Covers point-by-point walkthroughs, full-project sweeps, and adversarial cross-model review with circularity detection.

| Skill | Purpose |
|---|---|
| [`walkthrough`](./audit/walkthrough/) | Interactive, point-by-point walkthrough of any audit report. Re-evaluates findings, proposes fixes, and checks impacted files for regressions |
| [`sweep`](./audit/sweep/) | Full project review. Spawns parallel agents (architecture, quality, tests, docs) and consolidates findings into one deduplicated report |
| [`blindspot`](./audit/blindspot/) | Reviewer orchestrator that detects circularity (reviewer shares its target's codebase or model family) and injects cross-model judging via [OpenRouter](https://openrouter.ai) |
| [`skill-adversary`](./audit/skill-adversary/) | Adversarial reviewer for Claude Code skills. Surfaces trigger edge cases, instruction ambiguities, cross-file coherence issues, and gaps |
| [`mcp-adversary`](./audit/mcp-adversary/) | Adversarial reviewer for MCP servers. Surfaces tool-selection ambiguity, schema anti-patterns, semantic drift, and undocumented workflow dependencies |

See [`audit/README.md`](./audit/README.md) for per-skill details.

### `workflow`

Project workflow automation: file consistency sweeps, cross-repo synchronization, prose editing, session handoffs, source-backed recommendations, and documentation layout audits.

| Skill | Purpose |
|---|---|
| [`sync`](./workflow/sync/) | Scans all project files, identifies those stale relative to recent changes, and updates them. Always runs a cross-repo semantic consistency pass with parallel agents |
| [`write`](./workflow/write/) | Strips AI writing patterns and rewrites prose to read naturally. Routes to a French or English reference per text language. Includes a bilingual review mode (FR-EN parity, typo, faux amis) |
| [`continue`](./workflow/continue/) | Flushes durable facts to memory, updates `.claude/PLAN.md`, and prints a continuation prompt. No handoff document: PLAN.md and memory are authoritative |
| [`reco`](./workflow/reco/) | Deep recommendation backed by external sources. Parallel agents pull official docs (WebFetch) and community practice (WebSearch); the skill synthesizes a structured recommendation with verified citations |
| [`doc-structure`](./workflow/doc-structure/) | Audits documentation layout (CLAUDE.md vs README.md), proposes verbatim migrations of misplaced prose, and updates the CLAUDE.md index |

See [`workflow/README.md`](./workflow/README.md) for per-skill details.

## Requirements

**Required for both plugins:**

- [Claude Code](https://claude.com/claude-code) with plugin marketplaces enabled
- `git` (review targets and `workflow:sync` operate on git state)

**Optional, per feature.** Skills degrade gracefully: a missing dependency disables the affected feature and is reported. The rest of the skill runs.

| Dependency | Used by | Unlocks |
|---|---|---|
| `OPENROUTER_API_KEY` env var (+ `jq` CLI) | [`audit:blindspot`](./audit/blindspot/), [`audit:walkthrough`](./audit/walkthrough/) | Cross-model judging and cross-provider validation via [OpenRouter](https://openrouter.ai) |
| [Ouroboros](https://github.com/Q00/ouroboros) plugin | [`audit:walkthrough`](./audit/walkthrough/) | Consensus QA verdicts, evaluate + drift checks, lateral-think rescue |
| [`critical-code-reviewer`](https://github.com/posit-dev/skills) (posit-dev/skills) | [`audit:sweep`](./audit/sweep/), [`audit:walkthrough`](./audit/walkthrough/) | Specialist code-review agent. Default reviewer in `audit:sweep`; recommended `--reviewer` for `audit:walkthrough` on code targets. Falls back to inline review when absent |
| [`r-lib`](https://github.com/posit-dev/skills) skills `testing-r-packages`, `r-package-development`, `cran-extrachecks` (posit-dev/skills) | [`audit:sweep`](./audit/sweep/) on R projects | R-specific test, package, and CRAN-readiness audits |
| `gh` CLI | [`audit:walkthrough`](./audit/walkthrough/) | PR body as evaluate context (falls back to latest commit message) |

## License

[MIT](./LICENSE.md)
