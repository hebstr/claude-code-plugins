# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Releases cover the marketplace as a whole; both plugins ship together under the same tag.

## [Unreleased]

## [0.1.0] - 2026-05-21

Initial release of the `hebstr` marketplace: two plugins (`audit`, `workflow`) covering 10 skills.

### `audit`

- `walkthrough`: interactive, point-by-point walkthrough of any review report. Orchestrator mode (target + reviewer) and walkthrough-only mode (existing report). Re-evaluates findings, proposes fixes, checks impacted files for regressions.
- `sweep`: full-coverage project review with parallel specialist agents (architecture, quality, tests, docs), consolidated into a single deduplicated report sorted by severity.
- `blindspot`: circularity-aware orchestrator. Detects when a reviewer shares its target's codebase, prompts, or model family, then injects cross-model judging via OpenRouter and convergence analysis. Reviewer is discovered at runtime via the sibling walkthrough `scan-reviewers.py` script and confirmed with the user. Explicit-invocation only.
- `skill-adversary`: adversarial critic for Claude Code skills. Reports trigger edge cases, instruction ambiguities, contradictions, cross-file coherence issues, and gaps.
- `mcp-adversary`: adversarial critic for MCP servers. Reports inter-tool discrimination issues, schema anti-patterns, semantic drift, error handling inconsistencies, and undocumented workflow dependencies.

### `workflow`

- `sync`: scan files for staleness relative to recent changes and propose targeted updates. Always runs a cross-repo semantic consistency scan with parallel agents. Explicit-invocation only.
- `write`: strip AI writing patterns and rewrite prose to sound human. Routes to a French or English reference based on the text. Includes a bilingual review mode (FR↔EN parity, typography, faux amis). Explicit-invocation only.
- `continue`: flush durable facts to memory, update `.claude/PLAN.md`, and print a minimal continuation prompt. No handoff document is written; PLAN.md and memory are the authoritative stores. Explicit-invocation only.
- `reco`: deep-mode recommendation backed by external sources. Spawns two parallel agents (official documentation via WebFetch, community practice via WebSearch), then synthesizes a structured recommendation with verified citations. URLs are verified before citing; source disagreement is surfaced, not papered over. Explicit-invocation only.
- `doc-structure`: audit project documentation layout (CLAUDE.md vs README.md), propose verbatim migrations of misplaced prose, and update the CLAUDE.md index. 5-phase workflow (Discovery, Audit, Migration, Index updates, Verification). Pre-bundle reference check flags broken intra-file anchors, relative paths, and image references. Explicit-invocation only.

### Security

- `skill-adversary` and `mcp-adversary`: sub-agents use path-based file access instead of embedded prompts, removing prompt-injection surface.

[Unreleased]: https://github.com/hebstr/claude-code-plugins/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/hebstr/claude-code-plugins/releases/tag/v0.1.0
