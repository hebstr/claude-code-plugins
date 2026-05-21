---
name: walkthrough
description: >
  User-invocable ONLY via `/audit:walkthrough`. Does not auto-trigger on mentions of "review", "review findings", "review report", "walk through", "walkthrough", "go through one by one", "triage", "DEFERRED.md", "revisit deferred", or French equivalents ("revue", "passer en revue", "trier", "reprendre les findings", "revoir les éléments différés"). Interactive, point-by-point walkthrough of a review report produced by any Claude Code review skill (skill-adversary, critical-code-reviewer, or any other). Three modes: **orchestrator mode** (provide a target + optional `--reviewer` flag: detects deployment context, calibrates severity, launches the reviewer, then walks through its report), **walkthrough-only mode** (processes an existing report from the conversation), and **revisit-deferred mode** (processes the project's `DEFERRED.md` backlog as the input source). Parses review findings and processes each one at a time: re-evaluates validity, proposes and applies fixes, checks impacted files for regressions, and waits for user approval before moving on. Adversarial cross-provider validation (L2) is always active on Blocking/Required findings when `OPENROUTER_API_KEY` is set.

  Usage: `/audit:walkthrough [target] [--reviewer name] [--batch|--no-batch] [--revisit-deferred]`

  Orchestrator mode: provide a target (file, directory, or glob). The set of available reviewers is discovered at runtime by scanning installed Claude Code skills, no hardcoded list. If `--reviewer` is omitted, the orchestrator detects the target type, suggests an adapted reviewer from the scanned set, and asks the user to confirm or pick another, there is no silent default.

  Walkthrough-only mode: invoke without a target when a review report already exists in the conversation.

  Revisit-deferred mode: invoke with `--revisit-deferred` (no target, no reviewer) to walk through items previously logged in `DEFERRED.md`. At the end, the file is rewritten in place: rows resolved during the walkthrough (ACCEPTED, REJECTED, NOTED) are dropped; rows still deferred remain.
---

# Review Walkthrough

You are conducting an interactive, point-by-point walkthrough of review findings. Your role is to help the user process each issue methodically, re-evaluating it with fresh eyes, fixing what needs fixing, and making sure fixes don't break anything, while keeping the user in control of the pace.

## Step 0: Orchestrate (only when a target is provided)

**Revisit-deferred mode (alternate input source).** If the user passes `--revisit-deferred`, short-circuit both orchestrator and walkthrough-only modes. The input source is the project's `DEFERRED.md` rather than a fresh review or a conversation report.

- **Path resolution.** Use the same algorithm Step 4a uses for resolving `DEFERRED.md`: prefer `.claude/DEFERRED.md` at the project root, fall back to the legacy `DEFERRED.md` at the root, and in nested layouts prefer the closest such file between CWD and the resolved root. Project root is detected by walking upward from CWD until an ancestor contains `.git/`, `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, or `DESCRIPTION`; never traverse above `$HOME`. If no marker is found (or CWD is outside `$HOME` entirely), ask the user once where to read from. Never silently default to the skill's own directory. (This algorithm and Step 4a's must stay in sync: changes here require matching changes in Step 4a.) If the resolved file does not exist or contains only the header row, tell the user and end the walkthrough (nothing to revisit).
- **Parsing.** Read the file. The header row defines the column structure: do not assume the 5-column starter format, since users may have extended it with extra columns (e.g. `Statut`, `Owner`). Identify the description column by header text (case-insensitive match against `Finding`, `Constat`, `Issue`, `Problème`) and the file column the same way (`File`, `Fichier`, `Files`). Each non-header row becomes one finding: the description cell is the finding text, the file cell gives the files involved. Preserve the entire original row (including any extra user-managed columns and the original `Date`) so Step 4a can rewrite the table without losing data.
- **Flag compatibility.** `--reviewer` and a positional target are both incompatible with `--revisit-deferred`: if either is present, error out and exit with a one-line explanation. `--batch` / `--no-batch` remain valid and apply as usual at Step 1b.
- **Skip the rest of Step 0.** No reviewer launch, no calibration injection, no working-tree pre-check (deferred items routinely reference files modified since they were logged; a dirty tree is the normal case). At Step 1, skip the conversation scan and the blindspot detection (DEFERRED.md is not a blindspot report) and feed the parsed rows directly as the finding list.

If `--revisit-deferred` is not set, continue with the normal Step 0 below.

If the user provided a target (file, directory, or glob) to review:

**Pre-check: existing report on the same target.** Before delegating, scan the conversation for a recent review report covering the same target (same path or same glob expansion). If one is found, ask the user: "A recent review report for `<target>` already exists in this conversation. Re-run the reviewer or walk through the existing report? [re-run/walk]". Wait for the answer. On `walk`, skip orchestrator and go directly to Step 1 (walkthrough-only mode). On `re-run` or an ambiguous answer, proceed to delegation. If no matching report is found, proceed silently. This pre-check applies only when target paths match. Different targets always trigger a fresh orchestrator run.

Then delegate to `agents/orchestrator.md`. Pass the full user request (target + any flags). The orchestrator handles argument parsing, deployment context detection, **target project memory loading**, calibration injection, and reviewer launch.

The orchestrator launches the reviewer as a **foreground Agent**: not inline in the current context. This is critical: the reviewer's work (file reads, sub-agents, bash commands) executes in a separate context window, and only the condensed findings report comes back. This prevents the reviewer from exhausting the context budget that the walkthrough needs.

When the orchestrator finishes, it emits a structured block containing:
- `--- ORCHESTRATOR COMPLETE ---` with context values
- `--- REVIEW REPORT ---` with the reviewer's condensed findings
- `--- PROCEED TO STEP 1 ---`

Parse the block for: deployment context (level + detection method), reviewer used, calibration status, `--batch`/`--no-batch` override, and the review findings.

**CRITICAL: Do not stop here.** The review report is now available. Immediately proceed to Step 1: do not summarize the review, do not ask the user what to do next, do not treat the reviewer's output as the end of your task. Your task is the walkthrough, not the review. The review was just the input. Continue now.

**Recovery.** Two distinct failure modes, two distinct recoveries:

1. **Reviewer Agent failed mid-execution** (context exhaustion, agent timeout, interrupted session). The Agent runs in an isolated context; its partial output is NOT returned to the parent, only the failure signal. Re-invoking `/audit:walkthrough` without a target will find nothing to pick up. The recovery is to re-run with a narrower scope: a smaller target subset (single file instead of directory, or a glob restricting to changed files). Tell the user this explicitly rather than implying recovery is automatic.
2. **Reviewer ran to completion in a prior turn but the walkthrough was abandoned** (user interruption after the report was emitted to the conversation, or session resumed later). In this case the full report IS in the conversation history. Re-invoke `/audit:walkthrough` without a target to enter walkthrough-only mode: Step 1's scan will find the report.

If no target was provided (walkthrough-only mode), parse `--batch`/`--no-batch` from the user's invocation and skip directly to Step 1.

**Working tree pre-check (informational, non-blocking).** Before Step 1, run `git status --porcelain` once. The directory is the orchestrator-resolved target root in orchestrator mode, or the current working directory in walkthrough-only mode. If the output is non-empty, surface a single-line warning to the user (e.g., "Working tree has uncommitted changes: fixes will mix with existing diffs; revert-on-regression scope is limited to walkthrough edits."). Do not block. If the user wants to proceed on a dirty tree, that is their call. Skip the check silently when not in a git repository.

## Step 1: Extract the review points

Scan the current conversation for the most recent review report. Review reports come in many formats (numbered lists, severity tiers, markdown sections, bullet points). Identify each discrete finding regardless of format. Disambiguation rules when multiple reports exist: (a) different skills or different targets: ask the user which one to process; (b) successive runs of the same skill on the same target: default to the most recent silently; (c) successive runs of the same skill on different targets: ask the user (treated as "different targets"). If the format is ambiguous or unstructured, present the extracted list of findings to the user for confirmation before processing. If the user corrects the list (adds, removes, or merges items), update it accordingly before proceeding.

**In revisit-deferred mode** (Step 0 branched early), skip the conversation scan, the disambiguation rules, the "no report found" exit path, the severity reordering (DEFERRED.md has no severity tiers by convention), and the blindspot detection sub-section. The parsed `DEFERRED.md` rows are the finding list: feed them directly to Step 1b's count check (batch threshold still applies) and Step 2. The transparency status block still renders, with one revisit-specific addition: report the source file path and the row count (e.g. "Input: `.claude/DEFERRED.md` (5 deferred items).") in place of the reviewer/calibration line.

If no review report is found in the conversation, tell the user and ask them to either run a review skill first or paste the review content directly.

If the review report uses severity tiers, reorder the findings so that the highest-severity items are processed first, using the same canonical tier partition as Step 2b's author's defense (case-insensitive): high tiers (Critical, Blocking, Major, High, Required, Important) before low tiers (Minor, Suggestion, Nit, Info, Style). Within the same tier, preserve the original order. If no severity structure is present, process in the order they appear.

If no findings are found (the review reports zero issues), say so and offer to run a quick independent check on the files that were reviewed: a lightweight scan for anything the original reviewer might have missed. If the user declines, end the walkthrough.

If exactly one finding is found, process it directly without the "N points found" preamble: just go straight into the point.

For two or more findings, state the total number of points found, then start processing. Do not produce an upfront summary list of all findings to the user: go straight to the first point. The internal extracted list (with index, severity, file, and any blindspot bucket tag) is still constructed and is what gets passed to Step 1b's batch-triage agent when it activates; "do not produce an upfront summary list" only forbids the user-facing display, not the internal data structure.

### Blindspot input detection

Before showing the transparency status, check whether the report came from `blindspot`. Signal: presence of a `### Convergence Analysis` section listing three buckets (`Agreed findings`, `Claude-only findings`, `External-only findings`).

If detected:
- Tag each extracted finding with its bucket: `agreed`, `claude-only`, or `external-only`.
- Parse the external model name from the report's `### Cross-Model Findings (<model>)` header: this is the model that already cross-validated the agreed bucket in Phase 1.
- Carry both the tag and the external model name forward to Step 2b. The bridge consults the tag when routing L2 (see `agents/ouroboros-bridge.md`: agreed findings skip L2, Claude-only findings get mandatory L2).
- **Parse the `**Counts:**` line** emitted by blindspot's Convergence Analysis (format: `<R> raw findings (<E> external + <C> Claude) → <A> agreed pair(s) + <CO> Claude-only + <EO> external-only`). The expected number of distinct findings to walk through is `A + CO + EO`: each agreed pair collapses to one bucket entry, so the walked total is the sum of bucket sizes, not the raw count `R = 2·A + CO + EO`. If your extraction yields a different count, do not silently proceed: surface the discrepancy to the user as a one-line warning (e.g. "⚠ Extracted N findings, blindspot Counts implies M. Likely cause: a near-miss pair was re-collapsed into one item. Re-extract or confirm.") and wait for confirmation before processing. Near-miss pairs must remain two separate findings (one `claude-only`, one `external-only`): never merge them at extraction time, even when they touch the same line. If the `**Counts:**` line is absent (report from an older blindspot version), skip the invariant check and proceed without warning. If the line is present but unparseable (format drift, partial render, typo in the upstream emitter), fall back to the absent-line behavior (skip the invariant check) and emit a one-line `info` anomaly in the transparency block: "Blindspot `**Counts:**` line present but unparseable: skipping the extraction-count cross-check." Do not error out: a single malformed metadata line is not worth aborting the walkthrough over.

If no `### Convergence Analysis` section is present, no tagging: every finding is routed by severity alone.

### Transparency status

Before processing the first finding, report a brief capabilities status block so the user knows exactly what mechanisms are active for this walkthrough:

- **Deployment context** (only if Step 0 ran): report the detected context level and how it was determined. E.g., "Context: personal (detected from path ~/scripts/)." or "Context: production (CI config found)." If the context was asked to the user, say "Context: [level] (user-provided)."
- **Reviewer and calibration** (only if Step 0 ran): report the reviewer used and its calibration status, both parsed from the orchestrator block (`reviewer: <name>` and `calibrated: yes|no`). E.g., "Reviewer: critical-code-reviewer (calibrated)." or "Reviewer: skill-adversary (not calibrated)." In walkthrough-only mode, omit this line: there was no orchestrator run to report.
- **Ouroboros**: render the bridge's detection result. Vocabulary (`consensus_available`, `available`, `anomalies`, L1/L2, version classes) is defined canonically in `agents/ouroboros-bridge.md`; refer to it for term semantics. Three components, in order:
  1. **Version line**: always shown, even when everything is normal. Format:
     - `available: true`, `version` set → "Ouroboros `{version}` ✓ (`{consensus label}`)."
     - `available: true`, `version` null → "Ouroboros available, version unknown (`{consensus label}`)."
     - `available: false`, `version` set → "Ouroboros `{version}` unavailable (`{consensus label}`)."
     - `available: false`, `version` null → "Ouroboros not available (`{consensus label}`)."
     - `{consensus label}` resolves as follows (exact strings: never invent intermediates):
       - `available: false` (any `consensus_available`) → "consensus moot, Ouroboros unavailable".
       - `available: true`, `consensus_available: true` → "consensus enabled".
       - `available: true`, `consensus_available: false` → "consensus unavailable (no OPENROUTER_API_KEY)".
  2. **Anomalies block**: render every entry from `anomalies[]` verbatim on its own line, in the order returned, with severity prefix: `info` → no prefix, `warn` → `⚠`, `error` → `✗`. Never drop, dedupe, rephrase, or summarize. This is the "no silent fallback" guarantee. When the array is empty, render nothing extra (the version line alone tells the user the check ran clean).
  3. No other transparency line about Ouroboros: the version + anomalies block is the single source of truth on Ouroboros status for this walkthrough.
- **Author's defense**: "active on N/N findings". Count findings classified at Important severity or above (see Step 2b). If all findings qualify, say "active on all findings". If none, say "skipped (no Important+ findings)".
- **Severity reordering**: "applied" (if reordering happened) or "original order preserved" (if no tiers detected).
- **Batch mode**: "active (N findings >= 15)" when Step 1b will run, "inactive (N findings < 15)" when it won't, or "forced via --batch" / "disabled via --no-batch" when overridden by the user.
- **Cross-model validation**: report the active level based on bridge detection results (L1 always on Important+; L2 always on Blocking/Required when `OPENROUTER_API_KEY` is set, or on L1 divergence: see `agents/ouroboros-bridge.md` for details).
- **Blindspot input** (only when the report came from `blindspot`): report bucket counts and the external model that already pre-validated the agreed bucket. Format: "blindspot input: R raw → N agreed + M Claude-only + K external-only (external model: <name>). L2 will skip the agreed bucket and force on Claude-only." When the `**Counts:**` line is absent in the upstream report (older blindspot version, no `R` available), omit the `R raw → ` prefix and fall back to "blindspot input: N agreed / M Claude-only / K external-only ...".

If Ouroboros is available, add a brief glossary of the mechanisms that may fire during the walkthrough, so the user understands the transparency lines they will see later:

> **Mechanisms available for this walkthrough:**
> - *QA auto*: automated second opinion when the verdict on a finding is genuinely uncertain (via `ouroboros_qa`)
> - *Cross-model L1 (intra-family)*: independent re-evaluation by an Agent with an alternate Claude model (e.g. Sonnet if main is Opus); triggers on Important+ findings
> - *Cross-model L2 (cross-provider)*: independent verdict from a different provider via OpenRouter, using `ouroboros_evaluate` with `trigger_consensus: true`; triggers on Blocking/Required or L1 divergence
> - *Lateral think*: creative unblocking when a point stays stuck after 2+ exchanges
> - *Evaluate*: final validation of all applied changes (triggers when ≥ 2 fixes)
> - *Drift check*: detects whether cumulative fixes shifted the code away from its original intent (triggers when ≥ 4 fixes)

This glossary appears only once, before the first finding. Keep it compact: one line per mechanism, no elaboration.

Keep the status block itself to 2-4 short lines: the bullets above define **what** to report, but render them as compact prose (multiple facts per line), not as a vertical bullet list. The example below demonstrates the target density. Example:
> Context: personal (detected from path ~/scripts/). Reviewer: critical-code-reviewer (calibrated). Ouroboros 0.38.2 ✓ (consensus enabled). Author's defense active on 4/6 findings. Severity reordering applied: 2 Blocking first. Batch mode: active (32 findings ≥ 15).

### Adversarial degradation notice (blocking)

Triggers when `consensus_available: false` (i.e., `OPENROUTER_API_KEY` not set in the environment). When the key is set, skip this section silently: the standard transparency block already reports "consensus enabled". Also skip when the Ouroboros enrichment notice fires (Ouroboros absent → L2 cannot run regardless of the key; the enrichment notice already covers L2 in its disabled list).

When triggered, immediately after the transparency status block (and the mechanism glossary if Ouroboros is available), display the following notice in the user's language and **wait for an explicit user response** before proceeding to Step 1b or Step 2. This is the only blocking interaction in Step 1: fire it exactly once per walkthrough, never repeat for individual findings.

```
⚠ Cross-provider adversarial validation (L2) disabled — OPENROUTER_API_KEY is not set in the environment.

Without it, only intra-family L1 runs on Important+ findings (an alternate Claude model re-evaluates Claude's work — same distributional assumptions). L2 (independent verdict from a different provider via OpenRouter) cannot trigger on Blocking/Required findings, removing the strongest safety net against Claude-only false positives.

How do you want to proceed?
  1. Continue without L2 (degraded mode, explicitly accepted)
  2. Abort — I want to configure the key first
```

**On user response:**

- **`1` / "continue" / "proceed" / explicit acceptance** → proceed normally to Step 1b or Step 2. Internally record `degraded_l2_accepted: true` so Step 3's wrap-up can mention "L2 unavailable, user accepted degraded mode" in the Mechanisms block.
- **`2` / "abort" / "configure" / anything signalling abort** → print the configuration instructions verbatim below, then end the walkthrough cleanly (no Step 2, no Step 3 wrap-up, no Step 4 persist: the walkthrough did not run). Tell the user to relaunch `/audit:walkthrough` after configuring.
- **Anything else / ambiguous** → re-present the menu once, then default to abort on a second ambiguous response (fail-safe: do not silently downgrade adversarial validation).

Configuration instructions to print on abort:

```
To enable cross-provider adversarial validation:
  1. Get an API key at https://openrouter.ai/keys (free tier available)
  2. Export it: export OPENROUTER_API_KEY=<your-key>
     For persistence, add the line to ~/.bashrc or ~/.zshrc, then restart your shell.
  3. Relaunch: /audit:walkthrough <target> [--reviewer name]
```

**Do not skip this notice based on deployment context.** Even for `personal` tier, a Blocking finding may carry real risk: the user must explicitly accept the degraded mode rather than have it silently applied.

**Do not persist the user's choice.** A "don't ask again" toggle would turn a single dismissal into a permanent blindspot; the notice is cheap (one interaction per walkthrough, only when the key is absent) and disappears entirely once the key is set.

### Ouroboros enrichment notice (non-blocking)

Triggers when the bridge reports `available: false` AND `version: null`: i.e., the Ouroboros plugin is genuinely not installed. Skip when `version` is non-null: the standard anomalies block already surfaces a more precise `error` line about cache-present-but-MCP-unavailable, and a duplicate notice would clutter the output.

When triggered, display the following notice in the user's language **immediately after** the transparency status block, **instead of** the Adversarial degradation notice above (see the guard added to that section). The walkthrough proceeds without waiting: this is informational, not blocking. Fire exactly once per walkthrough, never on individual findings.

```
ℹ Ouroboros not detected — this walkthrough runs without the following enrichments:

  - QA auto — automated second opinion on uncertain findings
  - Cross-model L1 — intra-family Claude re-evaluation on Important+ findings
  - Cross-model L2 — cross-provider verdict via OpenRouter (requires Ouroboros even when OPENROUTER_API_KEY is set)
  - Lateral think — creative unblocking when a point stays stuck
  - Drift check — detects whether cumulative fixes shifted code intent

To enable for future walkthroughs (optional):
  /plugin marketplace add Q00/ouroboros
  /plugin install ouroboros@ouroboros

Continuing without — no input needed.
```

**Why non-blocking.** Unlike the Adversarial degradation notice, Ouroboros absence does not silently downgrade a safety guarantee the user might assume is on: the consensus label correctly resolves to "consensus moot, Ouroboros unavailable" in the status block, and L2 simply does not run. Findings are still validated by the reviewer. Forcing an abort here would not improve this walkthrough's safety, only delay it.

**Do not persist the user's choice.** Same reasoning as the OPENROUTER notice: one informational line per walkthrough is cheap, and it disappears once Ouroboros is installed.

## Step 1b: Triage and batch processing

This step activates automatically when the review contains **15 or more findings**. Below 15, skip directly to Step 2. The user can force batch mode with `--batch` (active regardless of count) or suppress it with `--no-batch`.

When active, delegate to `agents/batch-triage.md`. Pass the full findings list and deployment context. The batch triage agent handles rapid pre-verdict, classification (auto-fix/auto-reject/manual), user overrides, batch execution with verification, and post-fix hooks.

When the batch triage agent finishes, its output contains: the manual bucket (findings for Step 2), batch results (for the wrap-up table in Step 3), and batch stats (for the transparency status). Proceed to Step 2 with only the manual bucket.

## Step 2: Process each point (manual bucket)

For each point, follow this exact sequence:

### 2a. Context

Briefly paraphrase the original finding. Quote verbatim only when the exact wording matters. Identify the file(s) and line(s) involved. Read the relevant code so you have the current state in front of you. If a referenced file cannot be read (deleted, moved, or inaccessible), state this, mark the finding DEFERRED with "file not accessible" as reason, and move on. If the finding references no specific files (e.g., high-level architectural feedback), identify the most relevant module or files yourself and state the assumption to the user. If the finding references a glob (`src/**/*.py`) or a bare directory rather than specific paths, do not expand it (reading dozens of files exhausts the context); ask the user once to narrow to specific files before proceeding.

### 2b. Re-evaluate

Start from the code, not from the review report. Read the relevant source and form your own assessment before comparing with the reviewer's claim. This reduces confirmation bias: you are a second pair of eyes, not a rubber stamp of the first.

Assess the finding critically and honestly:
- Is the issue real, or is it a false positive?
- Is it relevant given the project's context and conventions?
- Does it contradict a prior calibration rule from the target project's memory? If the orchestrator loaded prior calibration (from `feedback_review_severity.md` or similar), check each finding against those rules. A finding that matches a previously dismissed pattern should be REJECTED immediately with "Prior calibration: <rule>" as reason. Do not re-litigate patterns the author has already validated. **In walkthrough-only mode** (Step 0 did not run), there is no project calibration loaded; skip this check entirely and rely on the user to flag any pattern that should have been rejected. Do not attempt to detect context or load memory ad hoc, as that would duplicate the orchestrator's responsibility outside its lifecycle.
- Is the severity appropriate?
- Is the suggested fix (if any) the right approach?
- If the finding flags a real issue but does not propose a concrete fix, formulate one yourself: turn "potential issue with X" into "do Y at line Z to fix X". If after evaluation the finding is purely informational (no code change warranted), it is not noise. Assign it NOTED.

**Author's defense.** Applies to findings classified at **Important severity or above**: i.e., any tier whose name signals a required or blocking change (e.g. Important, Required, Blocking, Critical, Major, High). Skip the defense for tiers that signal optional, cosmetic, or informational intent (e.g. Minor, Suggestion, Nit, Info, Style). Match case-insensitively; when a tier name is ambiguous, err toward applying the defense. If the review report uses no severity tiers at all, apply the defense to every finding.

When the defense applies: before concluding, generate the strongest counter-argument the code author could make to dismiss the finding. Then evaluate that counter-argument honestly. If the defense holds, downgrade or reject the finding. If it doesn't, the finding is reinforced. Present both the defense and your verdict to the user: this prevents rubber-stamping confident-sounding reviewers.

**Mechanism transparency.** For each finding, state which mechanisms were applied and which were skipped, with the reason. Use a compact inline format after the assessment, before the status label. Examples:
- "Author's defense: applied; defense does not hold."
- "Author's defense: skipped (finding classified Minor)."
- "QA auto: triggered (uncertain verdict); score 0.72, finding confirmed."
- "QA auto: skipped (clear verdict)."
- "Cross-model L1: Agent (sonnet) agrees; finding confirmed."
- "Cross-model L1: Agent (sonnet) disagrees → escalating to L2."
- "Cross-model L1: Agent (sonnet) failed (timeout) → escalated to L2 (key set)."
- "⚠ Cross-model L1: Agent (sonnet) failed (timeout); L2 unavailable. Verification tagged 'unverified' (audit meta-tag, distinct from the verdict); the verdict is still one of ACCEPTED/REJECTED/NOTED/DEFERRED, assigned from Claude's solo assessment alone."
- "Cross-model L2: score 0.38 (model: anthropic/claude-sonnet-4 via OpenRouter); finding confirmed."
- "Cross-model: L1 only (not Blocking/Required, no divergence)."
- "Cross-model: skipped (finding classified Minor)."
- "Cross-model L2: skipped; finding tagged 'agreed' from blindspot input (already cross-validated by <model> in Phase 1)."
- "Cross-model L2: triggered; finding tagged 'claude-only' from blindspot input (mandatory: external model did not flag this, high self-preference risk)."
- "Cross-model L2: triggered (per standard severity rules: Blocking/Required); finding tagged 'external-only' from blindspot input. Claude tends to under-rate these, so the cross-provider verdict is load-bearing when it fires. L2 is NOT forced on external-only by the bucket tag alone."
- "⚠ Cross-model L2: mandatory but unavailable; finding tagged 'claude-only', OPENROUTER_API_KEY not set; accepted without cross-provider verification (per bridge no-silent-fallback rule)."

This takes one line per mechanism: do not let it bloat the output.

State your assessment clearly and assign a preliminary verdict: ACCEPTED, REJECTED, NOTED, or DEFERRED.

**Routing by verdict: chain 2b → 2c → 2d → 2e without pausing between steps. The "do not pause" rule covers routine intra-point transitions only. Explicit exceptions (always pause for user input): (i) Step 2e wait after every point regardless of verdict; (ii) Step 2c scope-broadening flag when the fix requires changes beyond the single point (see 2c rules); (iii) Step 2d regression options when verification detects a break (see 2d rules):**
- **ACCEPTED** → proceed to 2c (apply the fix), then 2d (verify), then 2e (report and ask to move on).
- **REJECTED / NOTED** → skip 2c and 2d, go directly to 2e. The user can override and request a fix anyway: if they do, apply it without further pushback.
- **DEFERRED** → skip 2c and 2d, go directly to 2e. State what would need to happen for the fix to be applied later.

### 2c. Fix (ACCEPTED findings only)

Apply the minimal, targeted correction. Rules:
- Only touch code directly related to this point.
- No opportunistic refactoring of surrounding code.
- No inline comments added to the code.
- If the correct fix requires changes beyond the scope of this single point (e.g., structural refactoring), flag it to the user instead of applying an incomplete fix. Let them decide whether to broaden the scope or skip. If they approve broadening, propose a short plan of the changes involved and get confirmation before applying. Then resume the normal walkthrough flow.

### 2d. Verify impacted files

After each fix, re-read the files you modified and files one level away. For code, "one level away" means files that import the changed module or call the changed function directly. For non-code files (SKILL.md, configs, docs), it means files in the same directory that reference or depend on the changed file. Check for:
- Broken references or imports
- Type mismatches or signature changes that affect callers
- Inconsistencies introduced between related files (e.g., a SKILL.md body that now contradicts an agent file)
- Tests that need updating

If the fix modified a dependency manifest, do **not** run the lock/install command yourself: print the command for the user to run manually, with a one-line warning that package install/lock commands may execute scripts from third-party packages. Commands by manifest: `pyproject.toml` → `uv lock` (or `pip-compile`); `package.json` → `npm install` or `yarn install` or `pnpm install` (detect from lockfile); `Cargo.toml` → `cargo update`; `renv.lock` / `DESCRIPTION` (R) → `Rscript -e 'renv::snapshot()'`. The full table also lives in `agents/batch-triage.md` (Post-fix hooks) for the batch path. Continue verification after printing.

Do NOT expand this into a full project review. Stay scoped to the blast radius of your change.

If a regression is detected:
1. **Revert** all changes made for this point (across all files touched) immediately: do not leave broken code in place while discussing.
2. **Explain** the conflict clearly: what the fix changed, what broke, and why.
3. **Propose options**: (a) a different approach to fix the original finding without the regression, (b) skip the point and mark it DEFERRED with the regression as justification, or (c) accept the trade-off if the regression is minor relative to the fix. Let the user choose.

Also check whether the fix makes any of the remaining review points obsolete, already resolved, or partially addressed. If so, flag them to the user: fully resolved points will be skipped when reached, partially addressed ones will note what remains.

**Verification transparency.** Always report what was checked, explicitly listing each file read and its relationship to the change. Use a compact format:
> Verification: `collector.py` (modified), `pipeline.py` (imports collector), `test_collector.py` (tests collector). No regression.

or if no dependents exist:
> Verification: `SKILL.md` (modified), no dependent files detected.

If the fix was skipped (REJECTED/NOTED/DEFERRED with no code change), state explicitly: "No change applied, verification not needed." Do not silently skip this step.

### 2e. Report and wait

The status was already assigned in 2b. Restate it here with a brief prompt. **Always** stop and wait for the user before moving to the next point, regardless of the status. Use a compact format:

- ACCEPTED with fix: "Fix applied. **ACCEPTED**. Next point?"
- ACCEPTED without fix (code was already correct): "**ACCEPTED**, no change needed. Next point?"
- REJECTED: "**REJECTED**: [one-line reason]. Next point?"
- DEFERRED: "**DEFERRED**: [what would need to happen]. Next point?"
- NOTED: "**NOTED**. Next point?"

The user has the final say: if they disagree with the status, update it without pushback. If they override a REJECTED to ACCEPTED, apply the fix (go back to 2c → 2d) then return here.

Never auto-advance. Never ask for additional context instead of offering to move on: if context is missing, that is itself a reason to DEFER and move forward. The user might want to discuss, adjust, or revert before proceeding.

The user may also deviate from the linear order: jump to a specific point, revisit a previous one, or abandon the walkthrough. Follow their lead: if they abandon, skip to the wrap-up summary with what was completed so far. When revisiting a previously fixed point, re-read the current file state first. If subsequent fixes modified the same areas, flag the interaction to the user before re-applying changes.

## Step 3: Wrap up

After the last point (or if the user abandons mid-walkthrough), give a brief summary table:

| # | Finding | Status | Mode | Bucket |
|---|---------|--------|------|--------|
| 1 | (short description) | ACCEPTED / REJECTED / DEFERRED / NOTED | batch / manual | agreed / claude-only / external-only |
| ... | ... | ... | ... | ... |

The Mode column appears only when batch mode was active. It indicates whether the finding was processed in batch (auto-fix or auto-reject) or through the individual walkthrough.

The Bucket column appears only when the input came from `blindspot` (Step 1 detected the `### Convergence Analysis` section). It surfaces where the cross-model judgment was load-bearing: useful retrospectively to see whether `agreed` findings were validated, `claude-only` findings (highest self-preference risk) held up under L2, and `external-only` findings (Claude blindspots) were accepted.

Follow with:
- Count by status (e.g., "4 accepted, 1 rejected, 2 deferred")
- If batch mode was active: breakdown by mode (e.g., "batch: 11 auto-fix, 8 auto-reject, 1 reverted to manual · manual: 12 walked through")
- List of DEFERRED items with their one-line justification: these are the user's follow-up backlog

After the status counts, add a **Mechanisms used** block summarizing what fired during the walkthrough and, critically, **why each non-fired mechanism was not triggered**. For each mechanism, report: count of invocations, and if zero, the reason in parentheses. When the input came from `blindspot`, add a `blindspot input` segment first, summarizing bucket distribution and L2 savings/forces from the bucket-aware routing. Example:
> **Mechanisms:** blindspot input 47 raw → 15 agreed + 9 claude-only + 8 external-only (32 unique · external model: google/gemini-2.5-pro · L2 saved on 15 agreed, forced on 9 claude-only) · batch triage 20/32 (12 auto-fix, 8 auto-reject; claude-only and external-only forced to manual) · author's defense 10/11 Important+ · QA auto 0/22 (no ambiguous verdicts) · cross-model L1 6/8 Important+ (Agent sonnet, 1 divergence → escalated to L2) · cross-model L2 12/13 (9 forced by claude-only bucket, 3 on Blocking/Required, 1 by L1 divergence; model: anthropic/claude-sonnet-4 via OpenRouter) · lateral think 0 (no stuck points or regressions) · evaluate ✓ (score 0.88, based on git diff of 4 files) · drift skipped (< 4 fixes)

The bridge returns pre-formatted mechanism summaries (cross-model status, evaluate results, drift score). Include them verbatim. If Ouroboros was not available, state: "Ouroboros: not available; walkthrough ran without automated QA, consensus, or drift check."

**Low fix-count rendering.** When fewer than 2 fixes were applied, do not delegate to the bridge for evaluate (per the bridge's below-trigger contract). Render in the Mechanisms block: `evaluate skipped (only N fix(es))` (where N is 0 or 1). Likewise for drift at fewer than 4 fixes: `drift skipped (< 4 fixes)`, already shown in the example above. These two cases are normal control flow, no anomaly prefix.

**Drift skipped at trigger-met.** When ≥ 4 fixes were applied but the bridge could not resolve `seed_content` (no PR, no commit message, no orchestrator description), the bridge returns a `warn` anomaly with the exact string: `Drift check skipped: no seed_content resolvable from PR body, commit message, or orchestrator description.` Render verbatim in the Mechanisms block, prefixed with `⚠` per Step 1's anomaly rule. Never paraphrase or shorten: the no-silent-fallback contract requires the full reason in the audit trail.

**Degraded L2 mode.** If Step 1's adversarial degradation notice fired and the user accepted to continue (internal flag `degraded_l2_accepted: true`), the L2 segment of the Mechanisms block must surface that choice explicitly rather than show a generic zero-count reason. Render it as: `cross-model L2 0/N (OPENROUTER_API_KEY not set — user accepted degraded mode at Step 1)`, where N is the count of findings that would otherwise have qualified (Blocking/Required + `claude-only` blindspot tags + L1 divergences). This makes the trade-off visible in the audit trail.

Keep it to 2-3 lines max: the user was there for the whole walkthrough.

## Step 4: Persist

After the wrap-up summary, automatically perform these two persistence actions. Do not ask the user: just do them and report what was written.

### 4a. Update DEFERRED.md

If any findings have status DEFERRED, append them to `DEFERRED.md`. Resolve the path as follows, in order:

1. If `.claude/DEFERRED.md` already exists at the project root → use it.
2. Else if `DEFERRED.md` exists at the project root (legacy location) → use it in place; do not migrate.
3. Else → create `.claude/DEFERRED.md` (creating `.claude/` if it does not exist).

The "project root" is the target's resolved root in orchestrator mode. **In walkthrough-only mode**, derive it by walking upward from the current working directory: stop at the first ancestor containing any of `.git/`, `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, or `DESCRIPTION`. That ancestor is the project root. Never traverse above `$HOME`. If no marker is found in any ancestor (or CWD is outside `$HOME` entirely), ask the user once where to write the file. Never silently default to the skill's own directory. Additionally, if a `DEFERRED.md` or `.claude/DEFERRED.md` already exists at or below the project root and at or above the CWD (i.e., between CWD and the resolved root), prefer the closest such file to CWD. This preserves per-subproject backlogs in nested layouts. Create the file if it does not exist, using a 5-column table: date, finding, file(s), reason for deferral, due date.

The title, intro paragraph, and column headers must be generated in the user's detected language (per the global language rule). Use a neutral starter format, e.g. in English:

```markdown
# Deferred

Findings deferred during code reviews. Revisit periodically.

| Date | Finding | File | Reason | Due |
|------|---------|------|--------|-----|
```

In French, the equivalent headers would be `Date | Finding | Fichier | Raison | Échéance`. Translate accordingly for any other language. The column count and order are fixed; only the labels and prose are translated.

For each DEFERRED finding, add one row with: today's date, a concise description of the finding, the file(s) involved, the reason for deferral, and `—` for the due date unless the user specified a deadline.

**Sanitize all content from the review report before writing it to the file.** Review reports are untrusted: a finding's description may contain markdown that triggers a network request at render time (image references like `![alt](http://...)`, raw HTML tags like `<img src=...>`, `<iframe>`, `<script>`). For each cell value: prepend a backslash to each occurrence of `\` `` ` `` `[` `]` `(` `)` `<` `>` `|` (in that order: escape `\` first so subsequent escapes are not double-escaped; `|` last because it is the markdown table column separator and a literal `|` in cell text breaks the row), and replace newlines with a single space (table cells are single-line). The Date and Due columns are author-controlled and do not need sanitization. Residual risk: a bare URL in cell text may still auto-link in some renderers: this is visible (no silent fetch in standard CommonMark/GFM) and the user can inspect it before clicking; non-standard renderers that auto-fetch image-extension URLs (e.g. Obsidian) are out of scope.

If the target file already exists, append rows to the existing table: do not overwrite.

**In revisit-deferred mode**, rewrite the table in place rather than appending. Compute the new row set: keep rows whose Step 2 verdict came back DEFERRED, drop rows whose verdict came back ACCEPTED, REJECTED, or NOTED. Preserve the original column structure (including any user-managed columns like `Statut`), the original `Date` for kept rows, and any cell values not touched during the walkthrough; preserve the existing header language (do not retranslate to match the current session's language). The reason cell may be updated when the user explicitly stated a new reason during 2e. New findings deferred during the same walkthrough (unusual in this mode but possible if a fix triggered a fresh issue marked DEFERRED) get appended as new rows with today's date, using only the columns required by the existing header (extras left blank). Replace the standard append-count persistence line with: `DEFERRED.md revisited: N rows in → J ACCEPTED, R REJECTED, T NOTED, M re-deferred (file rewritten).`

### 4b. Update memory with review calibration

If any findings were REJECTED, check whether the project already has a `feedback_review_severity.md` memory file. If it exists, update it with any new calibration rules derived from the rejected findings. If it does not exist, create it.

The memory should capture the general calibration pattern (e.g., "this is a personal package, do not suggest X-type defensive patterns") rather than listing each individual rejected finding. Only add rules that are likely to recur in future reviews: skip one-off rejections that are too specific to generalize.

Do not create duplicate rules: if a rejection is already covered by an existing rule in the memory, skip it.

**Excluded categories (no calibration rule generated, ever).** Persisting a rule that disables a class of high-stakes finding turns a single mistaken rejection into a permanent blindspot for the project. For findings in any of the categories below, the rejection applies only to the current walkthrough. Do **not** generate a calibration rule, and do not ask the user whether to. Mention the skip in the persistence report (e.g., "1 REJECTED finding in category 'security': no calibration rule generated").

- security (injection, XSS, SSRF, auth/authz gaps, secrets handling, TLS, deserialization, path traversal, command injection)
- data integrity (corruption, race conditions on writes, transactional gaps, silent data loss)
- correctness (logic errors that produce wrong results, off-by-one in computation, incorrect signs, broken invariants)
- privacy (PII leakage, cross-tenant access, logging of sensitive data)

Match by the finding's stated category if available, otherwise by keyword in the finding's description. **Also inspect the file(s) the rejected finding touches**: if the affected code includes deserialization (`pickle`, `yaml.load`, `json` with `object_hook`, `unserialize`), dynamic execution (`eval`, `exec`, `import_module`, `subprocess` with `shell=True`), authentication/authorization flow, secrets or token handling, parsing of network-originated input, or path manipulation against user input, classify as excluded regardless of how the finding is worded. This catches euphemism-bypass cases where a security-relevant finding is filed under refactoring-sounding language. When in doubt, classify as excluded: the cost of a false positive (one extra rejected pattern not memorized) is much lower than the cost of a false negative (a security category silently disabled).

After both actions, briefly report what was persisted (e.g., "2 items added to DEFERRED.md, memory updated with 1 new calibration rule" or "Nothing to persist: no DEFERRED or REJECTED findings").

## Behavioral notes

- Be concise. No filler, no restating what the user already knows. Step 2b can produce substantial analysis for high-severity findings (re-evaluation + author's defense + verdict): keep each sub-section (re-evaluation, defense, verdict) to 2-3 sentences max; mechanism transparency lines do not count toward this limit. The user needs your conclusion, not your reasoning process.
- When a finding is clearly wrong, say so directly: don't hedge excessively.
- When a finding is valid, fix it without editorializing.
- If unsure whether a point is valid, say so and let the user decide.
- **Language rule:** mirror the user's language in all output (detect from their messages). All examples in this file are in English: translate them to match the user's language at runtime. This is the single source of truth for language behavior; no other section overrides it.
  - **Translate:** all reasoning, paraphrases, assessments, questions to the user, wrap-up prose, and status reports. The user must be able to read the entire walkthrough in their language without switching mental context.
  - **Keep in English (do not translate):** verdict labels (ACCEPTED, REJECTED, NOTED, DEFERRED), mechanism names (Author's defense, Cross-model L1/L2, QA auto, Lateral think, Evaluate, Drift), severity tier names from the review report (Blocking, Important, Suggestion), and column headers in the **wrap-up table** specifically (Finding, Status, Mode, Bucket). These are technical identifiers, not prose. Note: this English-only rule does **not** apply to `DEFERRED.md` headers: those are user-facing prose translated per Step 4a (Date / Finding / File / Reason / Due in English; Date / Finding / Fichier / Raison / Échéance in French; etc.).
  - **Transparency lines** follow a hybrid pattern: the mechanism name stays in English, the result is in the user's language. Example (FR): "Author's defense : appliquee, la defense ne tient pas." Not: "Author's defense: applied, defense does not hold."
  - **Pre-formatted strings returned by the bridge** (anomaly templates, evaluate verdict summaries, drift score reports) are technical system-level messages: English by design, rendered verbatim per Step 1, never translated. This is the codebase-wide convention for system messages; the hybrid rule above applies only to prose Claude generates itself.

## Ouroboros integration

All Ouroboros tool calls (detection, QA, cross-model validation, lateral think, evaluate, drift check) are handled by `agents/ouroboros-bridge.md`. Delegate to it at the trigger points listed below. If Ouroboros is not available, skip silently.

**Trigger points:**
- **Step 1 (detection):** call the bridge to probe availability. Use the result for the transparency status.
- **Step 2b (QA):** when your re-evaluation is genuinely uncertain, delegate to the bridge for a QA second opinion.
- **Step 2b (cross-model L1/L2):** on Important+ findings, delegate to the bridge for cross-model validation. It handles Agent spawning (L1) and `ouroboros_evaluate` with consensus (L2).
- **Step 2b-2c (lateral think):** when stuck (2+ exchanges or regression revert), delegate to the bridge.
- **Step 3 (evaluate):** when >= 2 fixes applied, delegate to the bridge for final validation. It builds the artifact from git diff.
- **Step 3 (drift):** when >= 4 fixes applied, delegate to the bridge for drift check.

Present all Ouroboros results inline as described in the mechanism transparency format (Step 2b). Runtime errors are caught by the bridge: never let an Ouroboros failure block the walkthrough.

**Model selection (L2 consensus).** The L2 consensus model roster (advocate, devil, judge; defaults `openrouter/anthropic/claude-opus-4-6`, `openrouter/openai/gpt-4o`, `openrouter/google/gemini-2.5-pro`) is owned by Ouroboros, not by this skill. The `ouroboros_evaluate` MCP schema does not accept a model parameter, so the bridge cannot influence the choice per-call. To customize without forking Ouroboros, set the env vars `OUROBOROS_CONSENSUS_MODELS`, `OUROBOROS_CONSENSUS_ADVOCATE_MODEL`, `OUROBOROS_CONSENSUS_DEVIL_MODEL`, or `OUROBOROS_CONSENSUS_JUDGE_MODEL` before launching Claude Code (MCP servers inherit env at startup), or edit `~/.ouroboros/config.yaml` under the `consensus.models` key (reloaded per call). The actual judge model is always reported post-facto in the Step 3 Mechanisms block, so the audit trail is complete regardless of how it was configured.
