---
name: walkthrough-ouroboros-bridge
description: Centralizes all Ouroboros integration for the review walkthrough, covering detection, QA on ambiguous findings, cross-model validation (L1 intra-family + L2 cross-provider), lateral thinking on stuck points, final evaluate, and drift check.
---

# Review Walkthrough: Ouroboros Bridge

You handle all Ouroboros tool calls for the walkthrough skill. The parent skill delegates to you at specific trigger points; you invoke the right tool and return the result.

## Detection (called once at Step 1)

Ouroboros tools are MCP tools with prefixed names (e.g. `mcp__plugin_ouroboros_ouroboros__ouroboros_qa`). They may be deferred.

The detection step performs three independent checks (MCP probe, filesystem version scan, OpenRouter key) and synthesizes them into a single status object. Every anomaly is surfaced; never silently downgraded.

### Compatibility constants

```
MIN_OUROBOROS        = "0.38.2"
MAX_TESTED           = "0.38.2"
CACHE_DIR            = "~/.claude/plugins/cache/ouroboros/ouroboros/"
QA_PASS_THRESHOLD    = 0.8     # score ≥ this → QA passes (matches ouroboros_qa default)
DRIFT_WARN_THRESHOLD = 0.3     # drift_score > this → surface as warning
```

The two threshold constants are LLM-produced score interpretations and may drift across model versions. They are calibrated against Ouroboros `MAX_TESTED`. When bumping `MAX_TESTED`, re-validate the thresholds against the new model behaviour and adjust if needed; do not silently inherit the prior values.

Baseline: all walkthrough features require ≥ `MIN_OUROBOROS`. There is no per-feature compatibility table: if the version is below the floor, the bridge reports Ouroboros unavailable in full. When a future Ouroboros release introduces a tool, parameter, or behavior the walkthrough depends on (and the existing version no longer suffices), bump both `MIN_OUROBOROS` and `MAX_TESTED` after verifying the walkthrough end-to-end against it.

### Procedure

1. **MCP probe.** Run `ToolSearch` with query `+ouroboros qa`.
   - No results → `mcp_up: false`, `mcp_error: "tools not discoverable"`.
   - Found → call `ouroboros_session_status` with `session_id: "__walkthrough_probe__"`. Any response, including a "session not found" error returned by the tool itself, confirms the MCP server is reachable → `mcp_up: true`. Only transport-level failure (tool errors out without a structured response, or no response at all) → `mcp_up: false`, `mcp_error: "<error message>"`. Rationale: `session_status` is a metadata lookup with near-zero compute cost, unlike `ouroboros_qa` which triggers a full evaluation cycle (5-dimension scoring) and is indistinguishable from a real billed QA call.

2. **Active version resolution.** The authoritative version is whichever Claude Code's plugin loader resolved, not the highest in the cache. Resolve in this order:

   **2a. Plugin manifest (preferred).** Read `~/.claude/plugins/installed_plugins.json`:

```bash
ACTIVE=$(jq -r '.plugins."ouroboros@ouroboros"[0].version // empty' ~/.claude/plugins/installed_plugins.json 2>/dev/null)
```

   - `$ACTIVE` non-empty → `fs_version: "$ACTIVE"`, `fs_versions: ["$ACTIVE"]`, classification proceeds on this value. Done.
   - `$ACTIVE` empty (manifest missing, key absent, jq unavailable, parse error) → fall through to 2b.

   **2b. Cache scan fallback** (capturing stderr separately so `fs_error` is reportable):

```bash
CACHE_DIR="$HOME/.claude/plugins/cache/ouroboros/ouroboros/"
ERR_FILE=$(mktemp) && trap 'rm -f "$ERR_FILE"' EXIT
OUT=$(ls -d "$CACHE_DIR"*/ 2>"$ERR_FILE" | xargs -r -n1 basename | sort -V)
ERR=$(cat "$ERR_FILE")
```

   The shell `CACHE_DIR` value must match the compatibility constant declared at the top of this file (current value: `~/.claude/plugins/cache/ouroboros/ouroboros/`). When the constant changes, update both sites: a single grep-check on `cache/ouroboros/ouroboros/` should return only these two lines. Interpret:
   - `$ERR` non-empty → `fs_versions: []`, `fs_error: "$ERR"` (first line if multi-line).
   - `$ERR` empty AND `$OUT` empty → `fs_versions: []` (no anomaly: Ouroboros simply not installed).
   - `$ERR` empty AND `$OUT` non-empty → `fs_versions` = list of installed versions in ascending order. Take the last (highest) as `fs_version`, AND append an `info` anomaly: `"Plugin manifest unreadable; using highest cached version {fs_version} as best-effort. Actual loaded version may differ if Claude Code resolved a non-highest install."` This anomaly is mandatory when the manifest fallback fires; do not skip.

   Rationale: the cache holds every version ever installed; only the manifest reflects the active resolution. Redirecting stderr to `/dev/null` in 2b would discard the very message the spec requires for `fs_error`; capturing it to a temp file preserves the no-silent-fallback contract.

3. **Version classification.** Apply only when `fs_version` is set; otherwise `version_class: "unknown"`.
   - SemVer regex `^[0-9]+\.[0-9]+\.[0-9]+$` does not match → `version_class: "unparsable"`.
   - Otherwise compare against `MIN_OUROBOROS` and `MAX_TESTED` using `printf '%s\n%s\n' "$a" "$b" | sort -V`:
     - `fs_version < MIN_OUROBOROS` → `version_class: "below_min"`.
     - `MIN_OUROBOROS <= fs_version <= MAX_TESTED` → `version_class: "supported"`.
     - `fs_version > MAX_TESTED` → `version_class: "above_tested"`.

4. **OpenRouter key.** Check `$OPENROUTER_API_KEY`. Report `consensus_available: true/false`. Independent from version and MCP state.

5. **Synthesize.** Apply this decision table (first row matching wins). Anomalies are accumulated, not replaced: multiple may apply per row.

| `mcp_up` | `fs_versions` | `version_class` | `available` | `version` | Anomalies |
|---|---|---|---|---|---|
| true | empty, no `fs_error` | — | true | null | `warn`: "Ouroboros cache not found under `CACHE_DIR`. Version unknown, compatibility unverified." |
| true | empty, with `fs_error` | — | true | null | `warn`: "Failed to read Ouroboros cache: `{fs_error}`. Version unverified." |
| true | non-empty | `unparsable` | true | `{fs_version}` | `warn`: "Ouroboros version `{fs_version}` is not parsable as SemVer. Compatibility unknown, proceeding without guarantee." |
| true | non-empty | `below_min` | false | `{fs_version}` | `error`: "Ouroboros `{fs_version}` < minimum required `{MIN_OUROBOROS}`. Update the plugin or run `/walkthrough` without Ouroboros." |
| true | non-empty | `above_tested` | true | `{fs_version}` | `warn`: "Ouroboros `{fs_version}` > last tested `{MAX_TESTED}`. Proceeding, behavior may diverge." |
| true | non-empty | `supported` | true | `{fs_version}` | — |
| false | non-empty | any | false | `{fs_version}` | `error`: "Ouroboros cache present (`{fs_version}`) but MCP server unavailable (`{mcp_error}`). Check the installation or restart Claude Code." |
| false | empty | — | false | null | — (Ouroboros simply not installed — standard case, no anomaly.) |

In addition to the row's anomalies, if `fs_versions` has length ≥ 2, append an `info` anomaly: "Ouroboros versions installed: `{list}`. Using `{fs_version}` (highest)."

### Return shape

```yaml
{
  available: bool,
  version: "X.Y.Z" | null,
  consensus_available: bool,
  anomalies: [
    { severity: "info" | "warn" | "error", message: "..." },
    ...
  ]
}
```

The parent skill renders the version line plus every anomaly verbatim, in the order specified below. No deduplication, no rephrasing, no silent skip: that is the "no silent fallback" contract.

**Anomaly ordering** (deterministic, applied by the bridge before returning):
1. By severity: all `error` first, then all `warn`, then all `info`.
2. Within each severity, by source step in detection order: (a) Active version resolution (step 2; includes the manifest-fallback info from 2b), (b) Version classification row anomaly (step 3 / decision table), (c) Length-≥-2 info (step 5, appended after row resolution), (d) Per-finding anomalies emitted later during Step 2b (L1 failure, claude-only-without-key). These belong to the per-finding render path, not the detection block, but follow the same severity-first/source-order rule when accumulated.

Render rules for the parent (also restated in SKILL.md):
- Consensus label resolves on the pair (`available`, `consensus_available`):
  - `available: false` (any consensus state) → "consensus moot, Ouroboros unavailable".
  - `available: true`, `consensus_available: true` → "consensus enabled".
  - `available: true`, `consensus_available: false` → "consensus unavailable (no OPENROUTER_API_KEY)".
  Exactly these three labels: never invent intermediates.
- Anomaly severity prefix: `info` → no prefix, `warn` → `⚠`, `error` → `✗`.

## QA: second opinion on ambiguous findings (Step 2b)

**Trigger:** the parent's re-evaluation is genuinely uncertain (cannot confidently call valid or invalid). Not for clear verdicts.

Call `ouroboros_qa` with: `artifact` (code section verbatim), `quality_bar` (finding's claim as quality criterion), `artifact_type` ("code").

Score ≥ `QA_PASS_THRESHOLD` → code passes (finding likely false positive). Below threshold → finding likely valid. Return the score (not just the verdict) so the user can judge marginal cases.

**Important:** `ouroboros_qa` does NOT support `trigger_consensus`. Never pass it.

## Cross-model validation (Step 2b)

Two levels replacing the former Advocate/Devil's Advocate pattern.

**Level 1: Intra-family Agent.** Triggers on findings classified Important+ (Important, Required, Blocking, Critical).

**Main-model detection.** The bridge reads its own model from the runtime announcement in the system prompt (Claude Code injects `You are powered by the model named <model> (claude-<family>-X-Y...)` at session start). Match case-insensitively on the family token (`opus`, `sonnet`, `haiku`).

**Alternate model selection** (priority order: pick the first viable):

| Main model family | Alternate to spawn | Rationale |
|-------------------|-------------------|-----------|
| Opus | `sonnet` | Different size, same family |
| Sonnet | `opus` | Different size, same family |
| Haiku | `sonnet` | Step up to a more capable evaluator |
| Anything else / unparseable | `sonnet` (default) + emit `warn` anomaly: `L1 main-model family not in {opus, sonnet, haiku}; spawning sonnet as default — cross-model independence weaker than usual.` | Future-proofing; user sees the degradation |

Spawn the Agent with the resolved alternate model. The Agent receives the code section and finding's claim, re-evaluates independently, returns verdict (valid/invalid + one-line rationale). Both agree → clear verdict. Disagree → flag divergence, escalate to L2 if available.

**L1 failure handling.** Three failure modes: apply the same rule to all:
- Timeout / no response from the Agent
- Agent refuses to evaluate ("I can't judge this")
- Output cannot be parsed as a `valid`/`invalid` verdict

In every case:
- L2 available (key set) → escalate to L2 unconditionally, even if the finding's severity rules wouldn't normally trigger L2. Surface this as `info`: `L1 failed (<mode>) — escalated to L2`.
- L2 unavailable (key not set) → mark the finding `unverified` and emit a per-finding `warn` anomaly: `Cross-model verification incomplete: L1 <mode>, L2 unavailable. Only main-model opinion available.` Surface this verbatim alongside the verdict. Do not silently accept the finding under the general "report and skip" error policy.

**Level 2: Cross-provider.** Triggers when: (a) finding is Blocking/Required, (b) L1 divergence on any severity, or (c) the finding carries a `claude-only` blindspot tag (mandatory regardless of severity, see "Blindspot input routing" below). Requires `OPENROUTER_API_KEY`. Call `ouroboros_evaluate` (not `ouroboros_qa`) with `trigger_consensus: true`, `session_id: "walkthrough"` (same session_id as Step 3 evaluate, so drift check sees both Step 2b L2 calls and the Step 3 final evaluate as a single logical session), `artifact` (code section), `acceptance_criterion` (finding's claim as pass/fail), `artifact_type` ("code"), `working_dir` (project root). Return the cross-provider verdict and model name (extract from response, e.g. "anthropic/claude-sonnet-4 via OpenRouter").

**Model transparency:** always report the alternate model identity (the one spawned, not the main). L1: `Agent (<alternate>)` where `<alternate>` is the family token from the selection table (`sonnet`, `opus`, or `sonnet` for the default branch; Haiku never appears as an alternate). L2: model name from response, or "unknown, not returned by evaluate".

If `OPENROUTER_API_KEY` not set, L2 unavailable. L1 divergences flagged but not escalated.

**No-silent-fallback rule for `claude-only` without key.** When a finding tagged `claude-only` would force L2 (per the routing table below) but `OPENROUTER_API_KEY` is absent, do NOT silently accept. Emit a per-finding `warn` anomaly to the parent skill: `L2 mandatory but unavailable: claude-only finding accepted without cross-provider verification`. The parent renders this anomaly verbatim alongside the finding's verdict: the SKILL.md Step 1 degradation accept/abort gate is a global signal, not a per-finding audit trail, and does not substitute for this anomaly.

### Blindspot input routing

When the report came from `blindspot` (Step 1 detected a `### Convergence Analysis` section), each finding carries a bucket tag. Apply this routing on top of the standard severity rules:

| Bucket tag | L1 | L2 | Rationale |
|------------|----|----|-----------|
| `agreed` | run normally on Important+ | **skip**, record "already cross-validated by <external-model> in Phase 1" | Avoid re-firing OpenRouter on findings the external judge already confirmed. |
| `claude-only` | run normally on Important+ | **force on** regardless of severity. If `OPENROUTER_API_KEY` is not set, emit a per-finding `warn` anomaly (see no-silent-fallback rule above); never silently accept. | These were not flagged by the external model in Phase 1; high self-preference risk requires a second cross-provider check before accepting. |
| `external-only` | run normally on Important+ | follow standard severity rules | Standard routing: the parent skill (SKILL.md Step 2b mechanism transparency) is responsible for surfacing the "Claude tends to under-rate these" warning to the user; this table only sets the L1/L2 routing. |

If no bucket tag is present (non-blindspot input), ignore this table and apply the standard severity rules only.

## Lateral think (Step 2b-2c)

**Trigger:** walkthrough stuck: 2+ user exchanges on same finding without resolution, or fix introduces regression (Step 2d revert). Not for simple mechanical disagreements.

Call `ouroboros_lateral_think` with: `problem_context` (what the finding asks and why it's contentious), `current_approach` (failed fix approach), `persona` (see selection rule below).

**Persona selection.** Pick by trigger first, then descend the priority list until a persona's bias matches the situation. Always pick a single persona: never compose.

| Trigger | Priority order |
|---------|----------------|
| Stuck (2+ exchanges without resolution) | `contrarian` → `researcher` → `simplifier` → `architect` → `hacker` |
| Regression revert (Step 2d) | `architect` → `simplifier` → `hacker` → `contrarian` → `researcher` |

Rationale per persona, in invocation order: `contrarian` (the shared assumption is wrong), `researcher` (missing context blocks judgment), `simplifier` (the approach is over-engineered), `architect` (structural mismatch, fix scope was wrong), `hacker` (last resort: pragmatic workaround acceptable).

Return the lateral angle as a third option.

## Evaluate: final validation (Step 3)

**Trigger:** >= 2 fixes applied during walkthrough.

**Below-trigger contract.** The parent skill is expected to gate on this trigger and not delegate when < 2 fixes were applied. If the parent does delegate with < 2 fixes (e.g. defensive call, future contract change), the bridge returns immediately without invoking `ouroboros_evaluate`: `{ evaluate: "skipped", reason: "insufficient_fix_count", fix_count: N }`. The parent renders this in the Mechanisms block as: `evaluate skipped (only N fix(es))`. No anomaly is required: this is a normal control-flow case, not a degradation.

Build `artifact` from actual content, not prose:
- **Code files:** `git diff` output on touched files. Prefix: "Evaluate ONLY the changes shown in this diff." If the diff exceeds ~4000 lines, drop entire per-file diffs (whole `diff --git` blocks) starting from the largest per-file diff, until under the limit; never truncate mid-file. After dropping, append a short note listing the omitted files and their line counts. Rationale: per-file size is the only signal reliably derivable from `git diff` alone; severity-based dropping is not implementable because the bridge has no contract with the parent for a `finding → file → severity` mapping. Trade-off accepted: a single very large fix may be dropped even if Critical; this is preferable to an unimplementable rule that silently degrades to arbitrary truncation. **When dropping occurs, the bridge MUST also append a `warn` anomaly to the evaluate result**: `"evaluate ran on truncated diff — dropped {N} file(s) from largest: {filename1} ({lines1}), {filename2} ({lines2}), … . Verdict reflects only the retained portion; review dropped files manually if any are load-bearing."` The parent renders this verbatim in Step 3's Mechanisms block (prefixed with `⚠`) so the audit trail surfaces the limitation rather than hiding it inside the artifact.
- **Non-code files:** final state of modified sections with context.
- **Mixed:** combine both. `artifact_type` "code" if majority code, "document" otherwise.
- **Fallback (prose):** only if content cannot be extracted. Flag explicitly.

Parameters: `session_id` ("walkthrough"), `acceptance_criterion` (original review goal + " Changes introduced during this review walkthrough only; pre-existing issues are out of scope."), `trigger_consensus` (see truth table below), `working_dir` (project root).

`trigger_consensus` truth table (always pass the parameter, never omit):

| `OPENROUTER_API_KEY` set | Any fix reverted during walkthrough | `trigger_consensus` |
|---|---|---|
| no | — | `false` |
| yes | yes | `true` |
| yes | no | `false` |

**Post-filter:** cross-reference flagged issues against diff. Discard issues on unmodified lines. Report: "N pre-existing issues filtered."

The post-filter assumes cross-cutting impacts (e.g. a signature change in one file that breaks a caller in another, unmodified-line) are caught upstream by Step 2d's per-fix "one level away" verification, or by Mechanical Verification (build/test) inside the evaluate call. If either is disabled (Step 2d skipped by the parent, or Mechanical Verification reported as `skipped (no command configured)`), the unconditional discard can silently drop cross-cutting findings on unmodified lines. Surface this as a `warn` anomaly to the user when both upstream layers are missing.

## Drift check (Step 3)

**Trigger:** >= 4 fixes applied during walkthrough.

Call `ouroboros_measure_drift` with: `session_id` ("walkthrough"), `current_output` (codebase state summary after fixes), `seed_content` (resolved free-text wrapped as Seed YAML: see resolution and wrap below).

**Free-text resolution**, in order. Each step must tolerate its own failure modes and fall through to the next; only the bridge's calling code decides "no content available", never the shell.

1. **PR body**: try `gh pr view --json body --jq .body 2>/dev/null`. Falls through to step 2 on any of: `gh: command not found`, auth failure (exit 4), no PR for current branch (exit 1 with "no pull requests found"), not a git repository, empty body. Capture only the structured non-empty body; do not retry.
2. **Latest commit message**: try `git log -1 --pretty=%B 2>/dev/null`. Falls through to step 3 on any of: not a git repository, no commits on branch, empty output.
3. **Orchestrator target description**: if Step 0 emitted a target description (the user's invocation of the skill, available in walkthrough-only mode as the current working context), use that. Falls through to step 4 if no description was carried forward.
4. **No content available**: skip the drift check (do NOT call `ouroboros_measure_drift`) AND emit a `warn` anomaly: `Drift check skipped: no seed_content resolvable from PR body, commit message, or orchestrator description.` This anomaly is mandatory; "drift skipped" without it would silently violate the no-silent-fallback contract (drift is a real degradation guard on ≥4-fix walkthroughs).

**Wrap as Seed YAML.** `ouroboros_measure_drift` parses `seed_content` as YAML and validates it against the Ouroboros `Seed` pydantic model (required fields: `goal`, `ontology_schema`, `metadata`). Passing raw free-text fails with `Seed validation failed: Input should be a valid dictionary`. Wrap the resolved free-text into a minimal valid Seed before the call:

```yaml
goal: |
  <resolved free-text from steps 1-3, indented under the block scalar>
ontology_schema:
  name: walkthrough
  description: Code review walkthrough drift check
metadata: {}
```

The free-text becomes the `goal` field (the dimension drift measurement weights at 50%); `ontology_schema` and `metadata` are placeholders the validator requires but the drift computation tolerates as minimal. Escape only what YAML requires: a block scalar (`|`) with proper indentation handles arbitrary content including colons, quotes, and backticks without escaping. Never pass an empty string or the unwrapped free-text to `seed_content`.

Drift score > `DRIFT_WARN_THRESHOLD` → warning in wrap-up. Return score and analysis.

## Error handling

The default policy is "report inline and continue": Ouroboros failures never abort the walkthrough. But silent acceptance of high-stakes failures violates the no-silent-fallback contract that the rest of this file enforces. Apply per-step rules:

| Failing step | Stakes | Policy on failure |
|--------------|--------|-------------------|
| QA auto (Step 2b) | Low — second opinion on an already-ambiguous verdict | Report inline `"QA auto: error — <one-line reason>. Skipped."`, no anomaly. |
| Lateral think (Step 2b-2c) | Low — creative unblocking is best-effort | Report inline `"Lateral think: error — <one-line reason>. Skipped."`, no anomaly. |
| Cross-model L1 (Step 2b) | Depends on severity — see L1 failure handling above (this section formalizes the same rule) | Important+ findings: escalate to L2 if key set; else mark finding `unverified` + per-finding `warn` anomaly. Below Important+: report and skip silently is acceptable. |
| Cross-model L2 (Step 2b) | High on Blocking/Required and `claude-only` findings — the entire point of the call is unverified | Mark the finding `unverified` and emit a per-finding `warn` anomaly: `Cross-provider verification failed: L2 errored (<reason>). Finding accepted without consensus.` |
| Final Evaluate (Step 3) | High — post-fix codebase was never validated | Report in the Mechanisms block with `⚠` prefix: `⚠ evaluate failed (<one-line reason>) — post-fix codebase not validated.` Do not render a success-style "evaluate ✓" line. |
| Drift check (Step 3) | Medium — drift on ≥ 4 fixes is a real degradation guard | Report in the Mechanisms block with `⚠` prefix: `⚠ drift check failed (<one-line reason>) — cumulative drift unverified.` |

The walkthrough still completes in all cases; the user sees the precise degradation rather than a generic "Skipped".
