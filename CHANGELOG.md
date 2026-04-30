# Changelog

## [0.3.0] - 2026-04-30

### `workflow`

#### Added

- `continue`: flush durable facts to memory, update `.claude/PLAN.md`, and print a minimal continuation prompt. No handoff document is written — PLAN.md and memory are the authoritative stores. Explicit-invocation only (`/workflow:continue`).

## [0.2.0] - 2026-04-30

### `workflow`

#### Added

- `write`: strips AI writing patterns and rewrites prose to sound human. Routes to a French or English reference based on the text. Includes a bilingual review mode (FR↔EN parity, typography, faux amis). Explicit-invocation only (`/workflow:write`).

#### Changed

- `sync-files` renamed to `sync`. Cross-repo semantic consistency scan is now the default and only mode; `--deep` flag removed. Invocation: `/workflow:sync`.

## [0.1.0] - 2026-04-26

Initial public release.

### `audit`

#### Added
- `walkthrough`: interactive, point-by-point walkthrough of a review report. Orchestrator mode (target + reviewer) and walkthrough-only mode (existing report). Re-evaluates findings, proposes fixes, checks impacted files for regressions.
- `sweep`: full-coverage project review with parallel specialist agents (architecture, quality, tests, docs), consolidated deduplicated report sorted by severity.
- `blindspot`: circularity-aware orchestrator. Detects when a reviewer shares its target's codebase, prompts, or model family, then injects cross-model judging via OpenRouter and convergence analysis. Explicit-invocation only.
- `skill-adversary`: adversarial critic for Claude Code skills. Reports trigger edge cases, instruction ambiguities, contradictions, cross-file coherence issues, and gaps.
- `mcp-adversary`: adversarial critic for MCP servers. Reports inter-tool discrimination issues, schema anti-patterns, semantic drift, error handling inconsistencies, and undocumented workflow dependencies.

#### Security
- `skill-adversary` and `mcp-adversary`: sub-agents use path-based file access instead of embedded prompts, removing prompt-injection surface.

### `workflow`

#### Added
- `sync-files`: scan files for staleness relative to recent changes and propose targeted updates. `--deep` mode runs cross-repo semantic consistency scan with parallel agents. User-invocable only.

[0.3.0]: https://github.com/hebstr/claude-code-plugins/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/hebstr/claude-code-plugins/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/hebstr/claude-code-plugins/releases/tag/v0.1.0
