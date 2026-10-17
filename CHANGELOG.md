# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Releases cover the marketplace as a whole; both plugins ship together under the same tag.

## [Unreleased]

### Added

- `audit`: `walkthrough` takes `--auto`, which adjudicates a long report without an approval turn between every point.
  It still pauses on a closed list of conditions, and everything blocking before the loop keeps blocking.
- `audit`: `walkthrough` takes `--judge <model-id>`, which pins the cross-provider L2 calls of a pass to one OpenRouter model instead of the automatic selection by family, in all three modes and under `--auto`.
  A malformed ID, a Claude-family or router ID, and the external judge of the blindspot report being walked are each refused, with a fallback to the automatic selection and a run-level warning.

### Changed

- `audit`, `workflow`: every skill of the marketplace sets `disable-model-invocation: true`.
  A slash command is the only way to launch one, and they no longer appear in the model's own skill listing, so a symptom described in plain language reaches none of them.
- `audit`: `blindspot` picks its external judge through `AskUserQuestion`, from four curated models, one per family, plus free text for any other OpenRouter ID: `google/gemini-4-argon` (default), `openai/gpt-6.1-sol`, `qwen/qwen3.8-max-prime` and `x-ai/grok-4.7`.
  Claude-family, router and floating-alias IDs are refused.
- `audit`: `blindspot` and `walkthrough` ask which reviewer to run through `AskUserQuestion` instead of a plain-text prompt, the suggested one first.
  The full scanned list is still printed above the menu, and a candidate past the fourth option is reachable through free text.
- `audit`: `walkthrough`'s cross-provider check calls OpenRouter directly, where it went through Ouroboros consensus, whose backend replaced every non-Anthropic voter with Claude.
- `audit`: every OpenRouter call reports its generation ID, checked against OpenRouter's own record.
  An unproven call is reported as unverified and feeds no convergence analysis.
- `audit`: a cross-provider check is forced before the walkthrough discards a finding a non-Claude model raised, where only a `claude-only` finding forced one before an accept.
  Discarding covers closing an Important+ finding as NOTED, not only rejecting it or lowering its severity.
- `audit`: `walkthrough`'s description states what the command writes without asking, fixes to the working tree, `DEFERRED.md` and a lasting calibration rule, and that a missing `OPENROUTER_API_KEY` opens the run on a blocking accept-or-abort prompt, where it narrated its own workflow instead.
- `workflow`: `sync` converts a drifted line-number reference to a name instead of renumbering it, and lists files through `git ls-files` in a git repository, so gitignored build output stays out of the dependency map.

### Removed

- `audit`: `mcp-adversary` is removed, with no replacement.
  Reviewing an MCP server now goes through a general reviewer passed to `walkthrough` or `blindspot` as `--reviewer`; `blindspot` still routes a target holding MCP tool definitions to whichever installed reviewer claims that capability.
- `workflow`: `doc-structure` is removed, with no replacement.
  Documentation layout is no longer audited by a dedicated command.
- `audit`: `walkthrough` no longer depends on the [Ouroboros](https://github.com/Q00/ouroboros) plugin, and no longer offers to install it.
  Four mechanisms go with it, none replaced: the QA second opinion, the lateral-think rescue, the final evaluate and the drift check.
  `jq` and `gh` are no longer required; `python3` and an OpenRouter key are.

### Fixed

- `audit`: `walkthrough`'s deployment-context detection resolved on a path heuristic or a CI signal for every path under the home directory, so the level recorded in memory was never read and the question was never asked; the memory check now runs before both.
- `audit`: `walkthrough` derived the `DEFERRED.md` path from the working directory, so a report about one repository walked from inside another wrote its deferrals into the wrong one.
- `audit`: `walkthrough` split a `DEFERRED.md` row on every `|`, the ones its own sanitization escapes included, so a finding whose text held a pipe shifted every later column of its row on revisit; it also unescaped the whole of CommonMark's punctuation class where it escapes nine characters, corrupting a hand-written cell.
- `audit`: `walkthrough` printed `renv::snapshot()` as the lock command for any R target, wrong for an `rv` project, and carried the manifest table in two copies that had drifted apart on the trigger's scope and on the `uv lock` condition.
- `audit`: `walkthrough` left a backlog row in place when a revisit found its finding already resolved, that outcome carrying no verdict for the rewrite to act on.
- `audit`: `walkthrough`'s Step 4a rewrote `DEFERRED.md` from the rows it had re-judged, so a walkthrough abandoned partway deleted every row it had not reached.
- `audit`: `blindspot` accepted a Claude-family or router ID as its external judge, so a same-family audit was reported as cross-model evidence.
- `audit`: `blindspot`'s judge and `walkthrough`'s L2 call embedded their target in a shell heredoc, so a target line equal to the delimiter ran as a command; both now write a file and pass its path.
- `audit`: `blindspot`'s judge gave up after 120 seconds, too short for a reasoning model, so the review lost its external half.
- `audit`: `walkthrough` and `blindspot` assumed a blocking Agent, so one stalled after launching its reviewer and the other could compile its report before its audits finished.
- `audit`: the reviewer scan credited a skill to a sibling plugin, dropped distinct skills sharing a name, offered skills from disabled plugins and from stale copies, and refused `audit:sweep` outright.
- `audit`: `sweep` named two `r-lib` skills that the installed set does not have, so its R-package agents always fell back to inline review.
- `audit`: `sweep` resolved its `[path]` argument nowhere, so a sweep of another path was calibrated against the working directory.
- `audit`: an exit status the three `python3` scripts did not enumerate, 127 among them, failed with no reason attached; every exit now resolves to a documented branch.
- `audit`: the generation check reported `model_mismatch` on a real call whenever OpenRouter's record expanded a date the requested slug already carried.
- `audit`: `blindspot`'s path-overlap axis duplicated the model-family axis, so every Claude-authored target read "Strong circularity" and "Structural circularity" was unreachable.
- `audit`: prior calibration was read from a single derived path, so a subdirectory target, a relocated memory directory or a store kept outside it all ran uncalibrated without notice, while a shared store injected the rules of unrelated projects.
- `audit`: `walkthrough` launched its reviewer by name, which no skill setting `disable-model-invocation: true` can be loaded by, so `--reviewer` reached none of this marketplace's own reviewers; it now passes the `SKILL.md` path the scan already returns, as `blindspot` does.

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
