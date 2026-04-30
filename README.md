# Claude Code plugins

![CI](https://github.com/hebstr/claude-code-plugins/actions/workflows/ci.yml/badge.svg)
![Release](https://img.shields.io/github/v/release/hebstr/claude-code-plugins)

Skills extend Claude Code with specialized workflows that activate automatically based on the task. Learn more at the [Claude Skills documentation](https://support.claude.com/en/articles/12512180-using-skills-in-claude).

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

Project workflow automation: file consistency sweeps, cross-repo synchronization, prose editing, and session handoffs.

| Skill | Purpose |
|---|---|
| [`sync`](./workflow/sync/) | Scan all files, identify ones that are stale relative to recent changes, and update them. Always runs a cross-repo semantic consistency scan with parallel agents |
| [`write`](./workflow/write/) | Strip AI writing patterns from prose and rewrite it to sound human. Routes to a French or English reference based on the text being edited. Includes a bilingual review mode (FR↔EN parity, typography, faux amis) |
| [`continue`](./workflow/continue/) | Flush durable facts to memory, update `.claude/PLAN.md`, and print a minimal continuation prompt. No handoff document is written — PLAN.md and memory are the authoritative stores |

## Requirements

[Claude Code](https://claude.com/claude-code) with the plugin marketplace feature enabled.

## License

[MIT](./LICENSE.md)
