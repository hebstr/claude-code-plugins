# audit

Review workflows for code, Claude Code skills and MCP servers. Covers point-by-point walkthroughs, full-project sweeps, and adversarial cross-model review with circularity detection.

Every skill is **explicit-invocation only**: invoked by typing its slash command, never auto-triggered from natural language.

## Install

```bash
claude plugin marketplace add hebstr/claude-code-plugins
claude plugin install audit@hebstr
```

## Skills

| Skill | Invocation | Purpose |
|---|---|---|
| [`walkthrough`](./walkthrough/) | `/audit:walkthrough [target] [--reviewer name] [--revisit-deferred] [--batch\|--no-batch]` | Interactive, point-by-point walkthrough of a review report. Orchestrator mode launches a reviewer first; walkthrough-only mode processes an existing report; revisit-deferred mode processes the project's `.claude/DEFERRED.md` backlog and rewrites it in place. Re-evaluates each finding, proposes fixes, checks impacted files for regressions, waits for approval before moving on. |
| [`sweep`](./sweep/) | `/audit:sweep` | Full-coverage project review. Detects project type and size, spawns specialist background agents with disjoint scopes (architecture, quality, tests, docs), consolidates findings into one deduplicated report sorted by severity, then conducts an interactive walkthrough. |
| [`blindspot`](./blindspot/) | `/audit:blindspot` | Reviewer orchestrator that detects circularity (reviewer shares its target's codebase, prompts, or model family) and runs cross-model judging via [OpenRouter](https://openrouter.ai), then convergence analysis over the resulting verdicts. |
| [`skill-adversary`](./skill-adversary/) | `/audit:skill-adversary <skill-path>` | Adversarial reviewer for Claude Code skills. Reviews a skill's full directory and surfaces trigger edge cases (false positives and negatives), instruction ambiguities, contradictions, cross-file coherence issues, and gaps. |
| [`mcp-adversary`](./mcp-adversary/) | `/audit:mcp-adversary <server-path>` | Adversarial reviewer for MCP servers. Reviews tool descriptions, parameter schemas, and implementation code; surfaces tool-selection ambiguity, schema anti-patterns, semantic drift between description and behavior, and undocumented workflow dependencies. |

## How the skills compose

- `walkthrough` is the terminal consumer: it takes a structured report from any reviewer (`sweep`, `skill-adversary`, `mcp-adversary`, or the external [`critical-code-reviewer`](https://github.com/posit-dev/skills)) and works through it finding by finding, proposing fixes and checking impacted files for regressions.
- `sweep` is the broad-coverage entry point for whole-project audits. `skill-adversary` and `mcp-adversary` are narrow specialists, one per artifact type (Claude Code skills and MCP servers).
- `blindspot` wraps any of the reviewers above when self-preference risk is credible: Claude reviewing Claude-authored skills, or sister skills in the same marketplace. It re-runs the target through a second model family via [OpenRouter](https://openrouter.ai) and compares verdicts to surface what either model missed.

## Common usage

The `--reviewer` flag takes a `plugin:skill` identifier (e.g. `posit-dev:critical-code-reviewer`); both orchestrators (`walkthrough` and `blindspot`) scan installed skills at runtime, no hardcoded list.

```bash
# Review a single file with a specific reviewer, then walk through findings interactively
/audit:walkthrough path/to/script.py --reviewer posit-dev:critical-code-reviewer

# Full-project audit
/audit:sweep

# Audit a custom Claude Code skill
/audit:skill-adversary path/to/skill/

# Audit a custom MCP server
/audit:mcp-adversary path/to/mcp-server/

# Cross-model check on a Claude-authored skill
/audit:blindspot path/to/skill/ --reviewer audit:skill-adversary

# Cross-model check on Claude-generated code
/audit:blindspot path/to/script.py --reviewer posit-dev:critical-code-reviewer

# Omit --reviewer to let blindspot suggest one interactively
/audit:blindspot path/to/target/

# Process the report from any command above interactively (walkthrough-only mode)
/audit:walkthrough
```

## Requirements

**Required:** [Claude Code](https://claude.com/claude-code) with plugin marketplaces enabled, and `git` (most review skills operate on git state).

**Optional**, per skill. Each skill degrades gracefully: a missing dependency disables the affected feature and is reported. The rest of the skill runs.

| Skill | Optional dependency | When missing |
|---|---|---|
| `walkthrough` | [Ouroboros](https://github.com/Q00/ouroboros) plugin | Consensus QA verdicts, evaluate + drift, and lateral-think rescue are skipped. Transparency block reports the missing layers. |
| `walkthrough`, `blindspot` | [OpenRouter](https://openrouter.ai) API key (`OPENROUTER_API_KEY` env var) + `jq` CLI | Cross-provider validation (walkthrough) and cross-model judging (blindspot) disabled. Blindspot falls back to single-model mode with an explicit warning. |
| `walkthrough` | [GitHub CLI](https://cli.github.com) (`gh`) | PR body cannot be fetched for the evaluate prompt. Falls back to the latest commit message. |
| `sweep` (Agent A) | [`critical-code-reviewer`](https://github.com/posit-dev/skills) (posit-dev/skills) | Agent A reverts to inline code review. Report labels the source as `inline fallback`. |
| `walkthrough` (`--reviewer` flag) | [`critical-code-reviewer`](https://github.com/posit-dev/skills) (posit-dev/skills) | `--reviewer posit-dev:critical-code-reviewer` is unavailable; use another reviewer or fall back to inline. |
| `sweep` (Agent C/D, R projects only) | [`testing-r-packages`, `r-package-development`, `cran-extrachecks`](https://github.com/posit-dev/skills) (posit-dev/skills, `r-lib`) | Per-skill fallback to a less specialized review. The sweep report names which skills were active. |

`sweep`'s Agent B (Architecture & Structure) uses Claude Code's built-in `Explore` subagent. No external dependency.

### Install the optional plugins

```bash
# Ouroboros
claude plugin marketplace add Q00/ouroboros
claude plugin install ouroboros@ouroboros

# Posit-dev skills
claude plugin marketplace add posit-dev/skills
claude plugin install posit-dev@posit-dev-skills
claude plugin install r-lib@posit-dev-skills
```

### Set the OpenRouter key

```bash
# add to ~/.bashrc or ~/.zshrc for persistence
export OPENROUTER_API_KEY=<your-key>
```

## License

[MIT](../LICENSE.md)
