# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Releases cover the marketplace as a whole; both plugins ship together under the same tag.

## [Unreleased]

### Changed

- `audit`: `blindspot`'s curated OpenRouter models, unchanged since the first release, are replaced by current releases checked against the OpenRouter catalog on 2026-09-15: `google/gemini-3.1-pro-preview` (default), `google/gemini-3.8-flash`, `openai/gpt-5.6-sol`, `deepseek/deepseek-v4-pro-0813`, `qwen/qwen3.8-max-0902` and `x-ai/grok-4.6`.
  Meta leaves the menu, since it has shipped nothing since Llama 4; any other model stays reachable through the custom option.
  `moonshotai/kimi-k3` was considered and left out: OpenRouter spreads it across about twenty providers, and a three-line prompt took more than 120 seconds on both test calls.
- `audit`: the `walkthrough` orchestrator caps the reviewer report at 25 findings instead of 15, so the automatic batch triage (15 findings or more) can fire on a capped report rather than only at exactly 15.
- `audit`: the Ouroboros bridge's last tested version (`MAX_TESTED`) is 0.54.4 instead of 0.38.2, so an up-to-date install no longer warns on every walkthrough; neither the QA nor the drift threshold is recalibrated against that version.
- `audit`: the reviewer scan has a pytest suite (`audit/walkthrough/scripts/test_scan_reviewers.py`), which CI runs next to ruff, now applied to the whole `scripts/` directory.

### Fixed

- `audit`: `blindspot`'s cross-model judge gave up after 120 seconds, too short for a reasoning model on a skill that ships a script: both Gemini entries of the menu timed out before answering, so the review lost its external half.
  The OpenRouter call now waits up to 580 seconds, and the judge runs it as a single Bash call with a 600-second timeout, which leaves room for curl's error to be reported where the tool's 120-second default would cut the call first.
- `audit`: `walkthrough`'s cross-provider validation (L2) never reached another provider.
  It went through Ouroboros consensus, and the Ouroboros plugin starts its MCP server with `--llm-backend claude_code`, whose adapter replaces every non-Anthropic OpenRouter voter with the default Claude model: the three votes reported as `gpt-4o`, `claude-opus-5` and `gemini-2.5-pro` were all Claude.
  L2 now calls `audit/walkthrough/scripts/openrouter-verdict.py`, which asks one external model through OpenRouter for a `valid`/`invalid` verdict and reports the model that actually answered: `openai/gpt-5.6-sol` by default, `google/gemini-3.1-pro-preview` when blindspot's first phase already used an OpenAI model.
  L2 no longer requires Ouroboros, and the Ouroboros enrichment notice no longer lists L1 or L2 among the mechanisms disabled without it, since L1 is an Agent and L2 an OpenRouter call, and the Step 1 mechanism glossary is shown without Ouroboros too, restricted to the mechanisms available; the final evaluate always passes `trigger_consensus: false`, and the Step 1 status reads `L2 enabled` or `L2 unavailable (no OPENROUTER_API_KEY)` instead of the consensus labels.
- `audit`: `walkthrough`'s L2 call embedded the reviewed code in quoted heredocs, so a reviewed line equal to a heredoc delimiter ended the heredoc and ran the lines after it as shell commands, and a path holding an apostrophe broke the quoting.
  The bridge now writes the claim and the code with the Write tool to scratchpad files and passes only their paths, with apostrophes escaped.
  The block also ended on an `echo` of the script's status, so the Bash call exited 0 even when the script failed; it now exits with the script's status, and a malformed call reports the last stderr line, where argparse puts its error, instead of the first, its usage banner.
- `audit`: `walkthrough`'s L2 severity trigger named only Blocking and Required, the critical-code-reviewer tiers, so a Critical finding from `skill-adversary` or the blindspot judge never reached L2 on severity; it now fires on Blocking, Required or Critical, matched case-insensitively.
- `audit`: `walkthrough`'s blindspot routing skipped L2 on `agreed` findings without saying whether an L1 divergence or failure still escalated, two rules the bridge also states unconditionally; the `agreed` skip now covers the severity trigger only.
- `audit`: `walkthrough`'s L1 Agent received the reviewed code and the finding's claim with no isolation, although it holds a full subagent's tools; its prompt now delimits both as data with randomly suffixed tags, as the L2 script does, and forbids edits and side-effecting commands.
- `audit`: `walkthrough`'s final evaluate built its artifact from `git diff`, which omits a file the walkthrough created while it is untracked; the artifact now includes each created file in full.
- `audit`: `walkthrough`'s drift check seeded its goal from the PR body or the last commit message before the review's own target, so an unrelated commit message dominated the drift score; the review goal now comes first.
  Evaluate and drift also shared the fixed session ID `walkthrough` across runs, and evaluate reconstructs stored state under that ID; each walkthrough now uses its own ID.
- `audit`: `walkthrough`'s main-model detection quoted a runtime announcement format Claude Code does not emit; it now searches the model name and ID for the family token.
- `audit`: `walkthrough`'s circularity nudge told the user to run `/blindspot <target>`, a command name that no longer resolves since the skills are namespaced under the plugin; it now prints `/audit:blindspot`, and `blindspot` and `sweep` name `/audit:blindspot`, `/audit:walkthrough` and `/audit:sweep` in their templates and footers.
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
- `audit`: the calibration loader injected every `feedback_review_severity*.md` of a shared memory store, including the rules of unrelated projects.
  It now keeps only the files whose frontmatter `description` names the target's project, a kind of artifact present in the target, or no project at all, plus every file of the project's own `.claude/memory/`, and the status line names the kept and skipped files.
  In walkthrough-only mode the filter takes the files the findings cite as its target, falling back to the working directory's root only when none exists, so a report about another repository is calibrated for that repository and both modes keep the same files.
  The status line says when the kept rules were not injected into a non-`code` reviewer, and `sweep` writes the no-calibration case as `none (<reason>)` like the shared procedure.
  The project root of a single-file target is resolved from its parent directory, since `git -C` refuses a file and the root fell back to the file's own directory.

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
