# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Releases cover the marketplace as a whole; both plugins ship together under the same tag.

## [Unreleased]

### Fixed

- `audit`: `walkthrough` stalled after launching its reviewer, and `blindspot` could compile its report before its audits finished, because both assumed a blocking Agent while interactive Claude Code runs every Agent in the background.
  The walkthrough orchestrator runs in the main context (a subagent cannot prompt the user), and both skills announce the running review and wait for the completion notification before continuing.
  The L1 cross-model check in the Ouroboros bridge waits the same way.
  Batch triage, which waits for the user's overrides, and the Ouroboros bridge also run in the main context.
- `audit`: `blindspot`'s cross-model judge hardcoded `google/gemini-2.5-pro` in its OpenRouter call, so a missed substitution sent the audit to that model instead of the one picked in the menu.
  The assignment now holds an `<EXTERNAL_MODEL>` placeholder, which the existing guard rejects.
- `audit`: the reviewer scan shared by `walkthrough` and `blindspot` returned bare skill names, globbed every `SKILL.md` under a plugin's install path, and dropped distinct skills sharing a name.
  In a monorepo marketplace this credited a skill to a sibling plugin and offered skills from a stale copy.
  It now reads the skills each plugin's marketplace entry declares, whether the entry ships in the install path or only in the marketplace catalog (a `git-subdir` skill bundle), as a string or a list, as the whole set for a marketplace-root `source` and otherwise on top of `skills/*/` and the paths `plugin.json` declares, skips paths outside the install path, names them `plugin:skill` after their directory as Claude Code does, and deduplicates and excludes self-references on that qualified name.
  Plugins set to `false` in `enabledPlugins` (user, project, local or managed settings), and project or local installs belonging to another project, are no longer offered.
  Project skills under `.claude/skills/`, from the working directory up to the repository root, are offered too, and a skill with no frontmatter `name` or a byte order mark is no longer skipped.
  A corrupt or unexpectedly shaped plugin manifest, including wrongly typed install fields, yields an empty candidate list and a warning on stderr instead of a traceback, and JSON files are read as UTF-8.
  Filtering, classification and the description excerpt ignore trigger and exclusion clauses ("Does not auto-trigger", "Do not use", "Not for", with a quoted or parenthesised span kept inside its clause only when it closes in the next sentence fragment) and the words "Claude Code", which made a skill match on words it disclaims, and the skill-tool signals accept plurals ("MCP servers").
  A bare mention of "tutorial" no longer excludes a reviewer; only "interactive tutorial" does.
- `audit`: `blindspot` resolved the reviewer's directory only from a bare name under `audit/` or `~/.claude/skills/`, so a qualified `plugin:skill` name from the scan resolved nothing and the path overlap check fell back to its distributional condition.
  Resolution now takes the matching scan candidate's `path` first, and strips the `plugin:` prefix in the fallback steps.
  The frontmatter reader strips block scalar markers (`|`, `>-`) and surrounding quotes, stops a value at the next unindented line whatever the key's case, and no longer reads an empty `description:` as the following key.
- `audit`: prior calibration for `walkthrough` and `sweep` was read only from the harness memory directory, derived from the target path with only `/` encoded, so a subdirectory target, a path containing `.`, a relocated `autoMemoryDirectory` or a memory store kept outside the per-project directories all ran uncalibrated without notice.
  The shared loader keys the harness directory by repository root with every character other than a letter, digit or `-` encoded, and uses the first of `autoMemoryDirectory`, that directory (redirect stub still followed) and `~/.claude/memory/` that holds `feedback_review_severity*.md`.
  Rules in the project's own `.claude/memory/` are read on top of that directory rather than instead of it.
  `walkthrough` writes new calibration rules to the chosen directory, never to the project store, and `sweep` runs this procedure instead of keeping its own copy.

### Changed

- `audit`: the `walkthrough` orchestrator caps the reviewer report at 25 findings instead of 15, so the automatic batch triage (15 findings or more) can fire on a capped report rather than only at exactly 15.
- `audit`: the reviewer scan has a pytest suite (`audit/walkthrough/scripts/test_scan_reviewers.py`), which CI runs next to ruff, now applied to the whole `scripts/` directory.

## [0.1.1] - 2026-06-03

### Fixed

- `audit`: the calibration-memory redirect stub was matched only as `Canonical index:`, so a memory store reached through a `Canonical location:` stub never resolved and `sweep`/`walkthrough` reviews silently ran uncalibrated.
  Both labels now match (case-insensitive), and the extracted path is normalized (surrounding backticks and whitespace stripped, trailing punctuation removed, leading `~` expanded).

### Changed

- `audit`: calibration loading globs scoped `feedback_review_severity*.md` variants (e.g. `_personal`) instead of a single fixed filename, reading every match.
- `audit`: `walkthrough`-only mode now loads prior calibration once before the finding loop, deriving the project root by upward walk; previously only orchestrator mode loaded calibration.

## [0.1.0] - 2026-05-28

Initial release of the `hebstr` marketplace: two plugins (`audit`, `workflow`) covering 10 skills.
Every skill is explicit-invocation only: invoked by typing its slash command, never auto-triggered from natural language.

### `audit`

- `walkthrough`: interactive, point-by-point walkthrough of any review report.
  Orchestrator mode (target + reviewer), walkthrough-only mode (existing report), and revisit-deferred mode (processes `.claude/DEFERRED.md` backlog).
  Re-evaluates findings, proposes fixes, checks impacted files for regressions.
- `sweep`: full-coverage project review with parallel specialist agents (architecture, quality, tests, docs), consolidated into a single deduplicated report sorted by severity.
- `blindspot`: circularity-aware orchestrator.
  Detects when a reviewer shares its target's codebase, prompts, or model family, then injects cross-model judging via OpenRouter and convergence analysis.
  Reviewer is discovered at runtime via the sibling walkthrough `scan-reviewers.py` script and confirmed with the user.
- `skill-adversary`: adversarial critic for Claude Code skills.
  Reports trigger edge cases, instruction ambiguities, contradictions, cross-file coherence issues, and gaps.
- `mcp-adversary`: adversarial critic for MCP servers.
  Reports tool-selection ambiguity, schema anti-patterns, semantic drift between description and behavior, error handling inconsistencies, and undocumented workflow dependencies.

### `workflow`

- `sync`: scan files for staleness relative to recent changes and propose targeted updates.
  Always runs a cross-repo semantic consistency scan with parallel agents.
- `write`: strip AI writing patterns and rewrite prose to sound human.
  Routes to a French or English reference based on the text.
  Includes a bilingual review mode (FR↔EN parity, typography, faux amis).
- `continue`: flush durable facts to memory, update `.claude/PLAN.md`, and print a minimal continuation prompt.
  No handoff document is written; PLAN.md and memory are the authoritative stores.
- `reco`: deep-mode recommendation backed by external sources.
  Spawns two parallel agents (official documentation via WebFetch, community practice via WebSearch), then synthesizes a structured recommendation with verified citations.
  URLs are verified before citing; source disagreement is surfaced, not papered over.
- `doc-structure`: audit project documentation layout (CLAUDE.md vs README.md), propose verbatim migrations of misplaced prose, and update the CLAUDE.md index.
  5-phase workflow (Discovery, Audit, Migration, Index updates, Verification).
  Pre-bundle reference check flags broken intra-file anchors, relative paths, and image references.

### Security

- `skill-adversary` and `mcp-adversary`: sub-agents use path-based file access instead of embedded prompts, removing prompt-injection surface.

[Unreleased]: https://github.com/hebstr/claude-code-plugins/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/hebstr/claude-code-plugins/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/hebstr/claude-code-plugins/releases/tag/v0.1.0
