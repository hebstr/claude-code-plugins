# Changelog

## [Unreleased]

### `review`

#### Changed
- `full-review` — pre-launch availability report now also checks `/review-walkthrough` (Phase 4 dependency), in addition to `/critical-code-reviewer` and the R-package skills.
- `skill-adversary` — `output-fuzzer` sub-agent deferred to V2; context doc updated to reflect the two-agent layout (`trigger-attacker`, `instruction-critic`) and point to `doc/v2.md` for the third axis.

#### Removed
- `litrev` plugin reverted to standalone repo (`github.com:hebstr/claude-code-litrev`). Migration into the `hebstr` marketplace was never validated runtime; rolled back to keep stacks (markdown skills vs Python MCP) and audiences (Claude Code devs vs medical researchers) separated.

### `workflow`

#### Added
- `write` — strips AI writing patterns from prose and rewrites it to sound human. Routes between French and English references based on the text being edited (`references/write-fr.md` ~900 lines, `references/write-en.md`). Includes a bilingual review mode (FR↔EN typography, faux amis, calques, allowlist of preserved technical anglicisms). Migrated from a personal fork of `waza/write` after substantial divergence (FR reference, bilingual mode, custom allowlist).

#### Changed
- `sync-files` renamed to `sync`. Cross-repo semantic consistency scan with parallel agents (formerly opt-in via `--deep`) is now the default and only mode; `--deep` flag removed. Invocation is now `/sync`.

## [0.1.0] - 2026-04-26

Initial public release.

### `review` 0.1.0

#### Added
- Plugin scaffolding with 5 skills bundled.
- `review-walkthrough` — interactive, point-by-point walkthrough of a review report. Orchestrator mode (target + reviewer) and walkthrough-only mode (existing report). Re-evaluates findings, proposes fixes, checks impacted files for regressions.
- `full-review` — full-coverage project review with parallel specialist agents (architecture, quality, tests, docs), consolidated deduplicated report sorted by severity.
- `blindspot-review` — circularity-aware orchestrator. Detects when a reviewer shares its target's codebase, prompts, or model family, then injects cross-model judging via OpenRouter and convergence analysis. Explicit-invocation only.
- `skill-adversary` — adversarial critic for Claude Code skills. Reports trigger edge cases, instruction ambiguities, contradictions, cross-file coherence issues, and gaps.
- `mcp-adversary` — adversarial critic for MCP servers. Reports inter-tool discrimination issues, schema anti-patterns, semantic drift, error handling inconsistencies, and undocumented workflow dependencies.

#### Security
- `skill-adversary` and `mcp-adversary` switched from content-embedded sub-agent prompts to a path-based contract: sub-agents receive absolute paths and `Read` files themselves. Removes prompt-injection surface via closing tags (`</skill>`, `</server>`) and context-bleed via prompt negation. Validated cross-model on 2026-04-25.

### `workflow` 0.1.0

#### Added
- Plugin scaffolding with 1 skill bundled.
- `sync-files` — scan files for staleness relative to recent changes and propose targeted updates. `--deep` mode runs cross-repo semantic consistency scan with parallel agents. User-invocable only.

[0.1.0]: https://github.com/hebstr/claude-code-plugins/releases/tag/v0.1.0
