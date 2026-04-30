# audit

Code, skill, and MCP review workflows: orchestrated walkthroughs, full-project audits, adversarial critique, and circularity-aware cross-model review.

## Install

```bash
claude plugin install audit@hebstr
```

## Skills

| Skill | Invocation | Purpose |
|---|---|---|
| [`walkthrough`](./walkthrough/) | `/walkthrough [target] [--reviewer name] [--adversarial]` | Interactive, point-by-point walkthrough of a review report. Orchestrator mode launches a reviewer first; walkthrough-only mode processes an existing report. Re-evaluates each finding, proposes fixes, checks impacted files for regressions, waits for approval before moving on. |
| [`sweep`](./sweep/) | `/sweep` | Full-coverage project review: detects project type and size, spawns specialist background agents with disjoint scopes (architecture, quality, tests, docs), consolidates findings into one deduplicated report sorted by severity, then offers interactive walkthrough. |
| [`blindspot`](./blindspot/) | `/blindspot` | Circularity-aware orchestrator. Detects when an audit skill is about to review an artifact that shares its codebase, prompts, or model family, then injects cross-model judging via OpenRouter and convergence analysis. Explicit-invocation only. |
| [`skill-adversary`](./skill-adversary/) | natural language ("audit this skill", "find flaws in `<skill>`") | Adversarial critic for Claude Code skills. Reviews a skill's full directory and reports trigger edge cases (false positives and negatives), instruction ambiguities, contradictions, cross-file coherence issues, and gaps. |
| [`mcp-adversary`](./mcp-adversary/) | natural language ("review my MCP server", "audit these tool descriptions") | Adversarial critic for MCP servers. Reviews tool descriptions, parameter schemas, and implementation code for inter-tool discrimination issues, schema anti-patterns, semantic drift between description and behavior, and undocumented workflow dependencies. |

## How the skills compose

```
┌──────────────────────┐
│   skill-adversary    │ ─┐
│   mcp-adversary      │  │  produce reports
│   sweep        │  ├─►  consumed by
│   critical-code-…    │ ─┘
└──────────────────────┘             │
                                     ▼
                          ┌──────────────────────┐
                          │  walkthrough  │  ◄──  orchestrator mode runs the reviewer first
                          └──────────────────────┘
                                     ▲
                                     │  optional wrapper when reviewer
                                     │  shares codebase/model with target
                          ┌──────────────────────┐
                          │   blindspot   │  ──► adds cross-model judge via OpenRouter
                          └──────────────────────┘
```

- `walkthrough` is the consumer: every other skill in this plugin produces reports it can process.
- `sweep` is the broad-spectrum entry point for whole-project audits; `skill-adversary` and `mcp-adversary` are narrow specialists for their respective artifact types.
- `blindspot` wraps any of the above when there's a credible self-preference risk (Claude reviewing Claude-authored skills, sister skills in the same marketplace, etc.).

## Requirements

- [Claude Code](https://claude.com/claude-code) with plugin marketplaces enabled.
- `blindspot` additionally requires an [OpenRouter](https://openrouter.ai) API key (`OPENROUTER_API_KEY`) for cross-model judging.
