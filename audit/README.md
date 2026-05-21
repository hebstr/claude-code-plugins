# audit

Code, skill, and MCP review workflows: orchestrated walkthroughs, full-project audits, adversarial critique, and circularity-aware cross-model review.

## Install

```bash
claude plugin install audit@hebstr
```

## Skills

| Skill | Invocation | Purpose |
|---|---|---|
| [`walkthrough`](./walkthrough/) | `/audit:walkthrough [target] [--reviewer name] [--revisit-deferred] [--batch\|--no-batch]` | Interactive, point-by-point walkthrough of a review report. Orchestrator mode launches a reviewer first; walkthrough-only mode processes an existing report; revisit-deferred mode processes the project's `DEFERRED.md` backlog and rewrites it in place. Re-evaluates each finding, proposes fixes, checks impacted files for regressions, waits for approval before moving on. Adversarial cross-provider validation (L2) is always active on Blocking/Required findings when `OPENROUTER_API_KEY` is set. |
| [`sweep`](./sweep/) | `/audit:sweep` | Full-coverage project review: detects project type and size, spawns specialist background agents with disjoint scopes (architecture, quality, tests, docs), consolidates findings into one deduplicated report sorted by severity, then offers interactive walkthrough. |
| [`blindspot`](./blindspot/) | `/audit:blindspot` | Circularity-aware orchestrator. Detects when an audit skill is about to review an artifact that shares its codebase, prompts, or model family, then injects cross-model judging via OpenRouter and convergence analysis. Explicit-invocation only. |
| [`skill-adversary`](./skill-adversary/) | natural language ("audit this skill", "find flaws in `<skill>`") | Adversarial critic for Claude Code skills. Reviews a skill's full directory and reports trigger edge cases (false positives and negatives), instruction ambiguities, contradictions, cross-file coherence issues, and gaps. |
| [`mcp-adversary`](./mcp-adversary/) | natural language ("review my MCP server", "audit these tool descriptions") | Adversarial critic for MCP servers. Reviews tool descriptions, parameter schemas, and implementation code for inter-tool discrimination issues, schema anti-patterns, semantic drift between description and behavior, and undocumented workflow dependencies. |

## How the skills compose

```
┌──────────────────────┐
│   skill-adversary    │ ─┐
│    mcp-adversary     │  │  produce reports
│        sweep         │  ├─►  consumed by
│   critical-code-…    │ ─┘
└──────────────────────┘             │
                                     ▼
                          ┌──────────────────────┐
                          │     walkthrough      │  ◄──  orchestrator mode runs the reviewer first
                          └──────────────────────┘
                                     ▲
                                     │  optional wrapper when reviewer
                                     │  shares codebase/model with target
                          ┌──────────────────────┐
                          │      blindspot       │  ──► adds cross-model judge via OpenRouter
                          └──────────────────────┘
```

- `walkthrough` is the consumer: every other skill in this plugin produces reports it can process.
- `sweep` is the broad-spectrum entry point for whole-project audits; `skill-adversary` and `mcp-adversary` are narrow specialists for their respective artifact types.
- `blindspot` wraps any of the above when there's a credible self-preference risk (Claude reviewing Claude-authored skills, sister skills in the same marketplace, etc.).

## Requirements

**Required:** [Claude Code](https://claude.com/claude-code) with plugin marketplaces enabled, and `git` (most review skills operate on git state).

**Optional**, per skill. Each skill degrades gracefully: the missing feature is reported and the rest continues.

| Skill | Optional dependency | Effect when absent |
|---|---|---|
| `walkthrough` | [Ouroboros](https://github.com/Q00/ouroboros) plugin | L1 consensus QA, evaluate + drift, and lateral-think rescue are skipped; transparency block reports the missing layers. |
| `walkthrough`, `blindspot` | [OpenRouter](https://openrouter.ai) API key (`OPENROUTER_API_KEY` env var) + `jq` CLI | L2 cross-provider validation (walkthrough) and cross-model judging (blindspot) disabled; blindspot falls back to single-model mode with an explicit warning. |
| `walkthrough` | [GitHub CLI](https://cli.github.com) (`gh`) | PR body cannot be fetched for the evaluate prompt; falls back to the latest commit message. |
| `sweep` (Agent A) | [`critical-code-reviewer`](https://github.com/posit-dev/skills) (posit-dev/skills) | Agent A reverts to inline code review; report labels the source as `inline fallback`. |
| `sweep` (Agent C/D, R projects only) | [`testing-r-packages`, `r-package-development`, `cran-extrachecks`](https://github.com/posit-dev/skills) (posit-dev/skills, `r-lib`) | Per-skill fallback to a less specialized review; Phase 3 Agents line names which skills were active. |

### Install the optional plugins

```bash
claude plugin marketplace add Q00/ouroboros
claude plugin install ouroboros@ouroboros

claude plugin marketplace add posit-dev/skills
claude plugin install posit-dev@posit-dev-skills
claude plugin install r-lib@posit-dev-skills
```

### Set the OpenRouter key

```bash
export OPENROUTER_API_KEY=<your-key>   # add to ~/.bashrc or ~/.zshrc for persistence
```
