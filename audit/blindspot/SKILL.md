---
name: blindspot
disable-model-invocation: true
allowed-tools: Read Glob Grep Bash Agent
description: >
  User-invocable ONLY via `/audit:blindspot`.
  Does not auto-trigger on mentions of "circular review", "review circulaire", "self-review check", "second opinion", "external judge", or any phrasing requesting circularity countermeasures.
  Runtime enforcement via `disable-model-invocation: true`: the Skill tool cannot launch this skill; user invocation is mandatory.
  Use when an audit skill (skill-adversary, mcp-adversary, sweep, critical-code-reviewer) is about to review an artifact that shares its codebase, prompts, or model family.
  Not for: general code review, PR review, a plain skill-adversary/mcp-adversary/sweep run when a second model's opinion and its OpenRouter call are not wanted, or LLM evaluation methodology discussions.
---

# blindspot

Orchestrates circularity-aware auditing.
When an audit skill must review an artifact that shares
its own base (code, prompts, model family), this skill detects the conflict and injects
countermeasures: cross-model judging via OpenRouter, and a transparency block in the final report.

**Orchestration must run in the main model context.** The subagents this skill spawns are the cross-model-judge (for the OpenRouter call) and the audit skill under test (Phase 1).
Do not delegate the orchestration itself to a subagent: it waits on the user at several points, and Claude Code withholds `AskUserQuestion` from every subagent.

**No other skill starts this one on the user's behalf**, neither through the Skill tool nor by spawning an Agent over this file.
A skill that detects circularity prints `/audit:blindspot <target> --reviewer <reviewer>` for the user to type, as `audit/walkthrough`'s circularity check does.
That is a rule and not a consequence: `disable-model-invocation: true` closes the Skill tool alone, `scan-reviewers.py` excludes this skill from reviewer candidates and so covers only the selection path, and Phase 1 below normalises the read-and-execute Agent pattern on other skills, which is exactly the route left open here.

## Invocation

```
/audit:blindspot <target-path> [--reviewer <audit-skill>]
```

- `<target-path>` (positional, required): path to the artifact being reviewed
- `--reviewer <audit-skill>` (flag, optional): the audit skill to run.
  No silent default.
  When omitted, the reviewer is discovered at runtime, suggested based on the target type, and confirmed with the user (see "Reviewer selection" below).
  The set of available reviewers is discovered at runtime, not hardcoded.

This syntax is harmonized with `/audit:walkthrough` so that chaining the two is frictionless: same positional `<target>` first, same `--reviewer` flag, same reviewer-selection procedure (scan + suggest + confirm, no silent default).
The harmonisation stops at the target's shape: walkthrough resolves a glob, blindspot takes one concrete path that must exist, so pass the directory holding the files, or run it once per file.

If invoked without `<target-path>`, ask the user for it.
If `--reviewer` is omitted, run the reviewer-selection procedure described in "Reviewer selection" below.

### Input validation

Before proceeding, validate `<target-path>` and the reviewer.
Step 4 below runs after "Reviewer selection" rather than before it, despite this section appearing earlier in the file: the scan result and the resolved reviewer path are produced once there, then reused here and again in Phase 0.

1. Resolve it to a canonical absolute path with `realpath`, expanding `~` and resolving `..` and every symlink.
   Step 3's containment test is lexical, so without canonicalisation a symlink inside the working directory passes it while pointing outside, and Phase 1 then ships the files it names to OpenRouter.
   Step 4 below already compares reviewer paths this way; the target deserves the same.

2. Verify it exists and contains readable files

3. Reject paths outside `~/.claude/` and the current working directory tree.
   The guard is anchored on the working directory, so it grants the whole filesystem when that directory is `/`; no working-directory-relative rule does better, and that case is accepted rather than special-cased.
   Report the error using this template and stop:

   ```
   <target-path> is outside the allowed scope (~/.claude/ or the current working directory). blindspot refuses to read arbitrary filesystem paths to avoid acting on unintended targets.

   To proceed, either:
     - cd into the project root that contains <target-path>, then relaunch /audit:blindspot <target-path>
     - or pass an absolute path inside ~/.claude/ if you intended to audit an installed skill
   ```

   Substitute `<target-path>` with the resolved absolute path the user passed.

4. Reject self-invocation: would create infinite recursion.
   When `--reviewer` is omitted, run this check on the reviewer locked in by "Reviewer selection" Step 4, before Phase 0.
   Resolve `--reviewer` to a concrete `SKILL.md` path using the same runtime resolution procedure as Phase 0 Path overlap (scan match → env shortcut → installed_plugins.json → `~/.claude/skills/`).
   If the resolved path's directory matches blindspot's own directory (compare via `realpath` on both sides), reject the invocation regardless of how the user spelled the argument (literal `blindspot`, absolute path, relative path, or symlink).
   Report the error and suggest using a different audit skill (e.g., `--reviewer audit:skill-adversary`).
   Also reject if `--reviewer` resolves to a wrapper skill that, by its own SKILL.md content, would re-invoke blindspot internally (best-effort check: grep the resolved SKILL.md case-insensitively for `audit:blindspot` invocations; if found, refuse and require the user to pass the wrapper's underlying audit skill directly).
   Match on `audit:blindspot` alone, never on a bare `/blindspot`, which the command's own spelling does not contain and which matches only a path segment: `audit/walkthrough/SKILL.md` carries one, in a documentation reference to a table, and the bare pattern refuses that skill over it.
   Step 2 of "Reviewer selection" accepts a reviewer the scan never surfaced, so a skill excluded from the candidate list still reaches this check.
   A wrapper that builds the command from a variable, by concatenation, or by calling a second wrapper does not match: report that as a known residual gap rather than as a clean pass, as the Path overlap check below does for a runtime-built path.

## Reviewer selection

When `--reviewer` is omitted, the reviewer is discovered at runtime, suggested based on the target type, and confirmed with the user.
Never silently default.

This procedure mirrors `/audit:walkthrough`'s orchestrator (see `audit/walkthrough/agents/orchestrator.md` §"Reviewer selection") and reuses its scanning script directly.
Steps 1 and 2 (scanning, validation) carry two intentional divergences, the script path, which blindspot resolves in a sibling skill, and the `Do not auto-correct` rule of Step 2; any other should be treated as a bug.
The Step 3 target-type table is intentionally extended in blindspot to cover Claude-interpreted artifacts (CLAUDE.md, agent definitions, paths under `~/.claude/`) that walkthrough does not gate on.
Inserting those rows also left the shared `SKILL.md` row ahead of the shared MCP row, which the orchestrator orders the other way.
No priority was decided for a target matching both, and none matches both on any tree checked so far, the one candidate holding its `SKILL.md` files two levels below the directory that carries the MCP server.
Settle that tie-break before relying on either order.

**Step 1, scan available reviewers.** Run the helper script from the sibling walkthrough skill.

Read this before the block: when `$CLAUDE_PLUGIN_ROOT` is unset (dev mode, non-plugin install) the harness leaves it unsubstituted, and the block would then run against a root-anchored path.
Take instead the path announced at the top of the skill prompt (`Base directory for this skill: <path>`) and append `../walkthrough/scripts/scan-reviewers.py`, which keeps a dev checkout on its own copy of the script rather than the installed one.
Failing that, resolve it via the same fallback procedure as Phase 0 "Resolution procedure": read `~/.claude/plugins/installed_plugins.json` for the audit plugin install path and append `audit/walkthrough/scripts/scan-reviewers.py`.
If neither resolution succeeds, report the failure to the user and ask them to pass `--reviewer <name>` manually.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/audit/walkthrough/scripts/scan-reviewers.py"
```

Do not invent reviewer names.

The script returns JSON with `candidates`: each candidate has `name`, `category` (`code` / `skill-tool` / `unknown`), `path`, and `description_excerpt`.
Plugin skills are named `plugin:skill`, user and project skills keep their bare name, a personal skill shadows a project skill of the same name, and self-references (`audit:walkthrough`, `audit:blindspot`) are excluded.
If the script returns zero candidates, tell the user the scan found no reviewer skills installed and ask them to specify one manually (e.g. by full skill path).

**Step 2, validate `--reviewer` if provided.** If the user passed `--reviewer <name>`, check that `<name>` is in the scanned candidates list (match by `name` or by its bare suffix after `:`).
If valid, use it as-is and skip steps 3 and 4.
A bare suffix matching several candidates names none of them: list those candidates alone, ask for the choice again by full `plugin:skill` name, and do not skip steps 3 and 4 on a guess.
Two plugins each shipping a skill directory of the same basename is all it takes, the scan deduplicating on the full name and never on the suffix.
Phase 0's resolution procedure declines to guess on the same input, but declining there only defers the choice to its manifest walk, which matches the bare suffix at any depth under every install path and so answers with whichever plugin was installed first.
That path then feeds the self-invocation guard of "Input validation" step 4, the overlap check, and the reviewer the Agent is told to run.
If it is absent from the list but resolves to a readable `SKILL.md`, as a filesystem path to an existing `SKILL.md` or to a directory holding one, or as `<plugin>:<skill>` found under an install path in `~/.claude/plugins/installed_plugins.json` or at `~/.claude/skills/<skill>/SKILL.md`, accept it, warn in one line that the scan did not surface it, and skip steps 3 and 4.
The scan gates on the bare skill name against `review`, `adversary`, `audit`, `critic` and `sweep`, so a reviewer carrying none of them is missed and this path is the only way to reach it.
Otherwise, list the scanned candidates back to the user and ask them to pick one.
Do not auto-correct.

**Step 3, detect target type and pick the suggested category.** Apply these rules in order on the resolved target path; first match wins:

  | Signal on resolved target                                                                                                                                                           | Suggested category                             |
  | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
  | Filename is `CLAUDE.md` or matches `*.claude.md`                                                                                                                                    | `skill-tool` (Claude-interpreted instructions) |
  | Target is a `SKILL.md`, holds one at its top level or skill directories (`*/SKILL.md`) one level down, or path is under `~/.claude/skills/` or `<plugin>/skills/`                   | `skill-tool` (skill audit)                     |
  | Target is an `*.md` file under any `agents/` directory at any depth                                                                                                                 | `skill-tool` (agent definition)                |
  | Target contains MCP tool definitions (e.g. `@mcp.tool` / `Server.tool` decorators, `mcp.json`, `mcp_server.py`, `*-mcp/` directory)                                                 | `skill-tool` (MCP audit)                       |
  | Target's resolved absolute path is inside `~/.claude/` or any plugin install directory (cache or marketplace)                                                                       | `skill-tool` (Claude-interpreted artifact)     |
  | Target is a project root (directory containing a top-level `README` plus a manifest like `pyproject.toml`, `package.json`, `Cargo.toml`, `DESCRIPTION`, etc.) and not a single file | `code` (project-wide)                          |
  | Otherwise (single file, or a sub-tree of code)                                                                                                                                      | `code` (focused)                               |

Within the matched category, pick the suggested reviewer using these heuristics on the candidate names (case-insensitive substring):

- `skill-tool` (instructions / skill audit / agent definition / Claude-interpreted artifact): prefer a candidate matching `skill` first, otherwise fall back to any `skill-tool` candidate.
- `skill-tool` (MCP audit): prefer a candidate matching `mcp` first, otherwise fall back to any `skill-tool` candidate.
- `code` (project-wide): prefer a candidate matching `sweep`, `full` or `project` first, otherwise fall back to any `code` candidate.
- `code` (focused): prefer a candidate matching `critical` or `code-review` first, otherwise fall back to any `code` candidate.

If multiple candidates tie within the preferred sub-rule, pick the one with the shortest `name`; the same tie-break governs the `otherwise fall back to any <category> candidate` branch, where every candidate of that category ties by construction.
Say in the Step 4 rationale when the suggestion came from that fallback, so the user can override before the reviewer launches.
If the matched category has zero candidates in the scan, fall back to the other category's best match and surface this in the rationale.
A candidate the scan classified `unknown` is never auto-suggested, since nothing establishes that it reviews this target type, but it is listed under its own `[unknown]` group in Step 4 and can be chosen.
When every candidate is `unknown`, present them all with no suggestion and ask the user to pick, rather than promoting one into a slot no rule selected.

**Step 4, present the suggestion and wait.** Show the user the scanned list (grouped by category), the suggested reviewer, and a one-line rationale tying the suggestion to the detected target type.
Present it as plain text, not through `AskUserQuestion`, whose option cap would hide candidates.
The format below is illustrative: the actual reviewer names come from the scan output, not from this template:

```
No --reviewer specified. Scanned reviewers:
  [code]       <names from scan>
  [skill-tool] <names from scan>
  [unknown]    <names from scan, listed but never suggested>
Suggested: <chosen name> (<one-line rationale>).
Pick a reviewer or reply `ok` to accept the suggestion.
```

On the user's response: empty input or explicit confirmation → use the suggested reviewer; a candidate name from the scanned list (full, or a bare suffix matching exactly one) → use that one; a bare suffix matching several → re-prompt with those candidates alone, as in step 2; anything else → re-prompt with the same options.
Once the choice is locked in, the reviewer's own `category` is not carried any further.
The walkthrough orchestrator carries it to gate calibration injection, which blindspot does not perform, and Phase 1 derives `ARTIFACT_TYPE` from Step 3's target-type detection instead, a property of the target rather than of the reviewer.

## Phase 0: Circularity Detection

Determine whether the audit is circular.
A review is circular when reviewer and target share
any of these properties.

### Path overlap

Check if `<target-path>` is within or overlaps with the audit skill's own directory.
The audit skill's location must be resolved at runtime.
Do not rely on a single static env var, because `${CLAUDE_PLUGIN_ROOT}` is only set when the host plugin is invoked through the normal plugin loader and is undefined in dev mode (skill executed from a checked-out repo) or non-plugin installs (`~/.claude/skills/<name>/`).

**Resolution procedure**, in order.
First match wins.
In steps 2 to 4, `<reviewer>` stands for the skill name after any `plugin:` prefix (`audit:skill-adversary` → `skill-adversary`).

1. **Scan match.** Run the reviewer scan from "Reviewer selection" Step 1 if it has not run yet; if the scan script itself cannot be located, skip to step 2.
   If exactly one candidate matches `--reviewer` by `name` or by its bare suffix after `:`, use that candidate's `path`.
   If several candidates share the bare suffix, fall through to step 2 rather than guessing.
   "Reviewer selection" step 2 rejects such a suffix before this procedure ever sees it, so this is a backstop against a caller that resolves a reviewer without passing through that step, not a live branch.
2. **`${CLAUDE_PLUGIN_ROOT}` shortcut.** If `$CLAUDE_PLUGIN_ROOT` is non-empty AND `$CLAUDE_PLUGIN_ROOT/audit/<reviewer>/SKILL.md` exists, use that path.
   This is the fast path for the standard plugin install.
3. **Plugin manifest scan.** Read `~/.claude/plugins/installed_plugins.json`, walk each install path, look for a `<reviewer>/SKILL.md` at any depth under it, since only this plugin groups its skills under an `audit/` segment.
   If found, use that path.
4. **Global skill scan.** Look for `~/.claude/skills/<reviewer>/SKILL.md`.
   If found, use that path.
5. **No path resolvable.** The reviewer's install location cannot be determined.
   Skip both conditions of the overlap check below, report path overlap as `No (reviewer path not resolved)`, and append an `info` line in the report: `Reviewer <name> path not resolved, directory overlap check skipped.`
   The distributional signal does not depend on this check: Model family overlap carries it.

Path overlap is circular if **either** of these conditions is true (OR logic):

1. Target path is inside the resolved audit skill directory (direct self-review).
   Applies only when resolution succeeded.

2. The audit skill depends on a file inside the target path: one of its own files names a path resolving inside the target, or it runs a script located there.
   Applies only when resolution succeeded.
   This is a dependency and never a mention, so the reviewer naming the target's skill in prose, as a description listing sibling reviewers does, is not overlap.
   Check it literally, searching the reviewer's own files for path segments of the resolved target.
   A path the reviewer builds at runtime from a variable or by concatenation will not match: report that as a known residual gap rather than as a No.

Path overlap measures filesystem overlap only.
A Claude-authored target reviewed by a Claude Code skill shares distributional assumptions with it even without that overlap, which is what Model family overlap below records.

### Model family overlap

The reviewing model and the model that generated the target share the same family if either condition holds (OR):
- The target was generated by Claude (any version) AND the reviewer is Claude.
In Claude Code the reviewer is always Claude, so this reduces to "target was generated by Claude", a property of the target, not a constant.
- The target contains prompt text, SKILL.md instructions, or agent definitions authored for Claude; these were optimized for Claude's distribution and will be judged leniently by Claude.

Both conditions are False only when the target is human-written code or code generated by a non-Claude model with no Claude-targeted prompt content.
In that case, model-family overlap = No.
When the target has no Claude-targeted content and its provenance cannot be established from it, report `Yes (provenance unknown)`: No requires the user to state that the target is human-written or non-Claude-generated, since a guessed No skips the cross-model judge the invocation asked for.
Nothing asks them for it: the statement counts when it arrives unprompted, in the invocation or in the conversation around it, and is never solicited.
A closed question would put the cheaper answer in the user's mouth on the one countermeasure the invocation exists to buy.
The population it could serve is narrow anyway, the two `code` rows of Step 3 alone, since the other rows satisfy the second condition on sight, and that population already has a shorter documented route in the `Not for:` clause, which is to run the reviewer without blindspot at all.
The `No circularity` row of the table below is therefore rare by design rather than by oversight.

### Circularity verdict

  | Path overlap | Model family overlap | Verdict                                                            |
  | ------------ | -------------------- | ------------------------------------------------------------------ |
  | Yes          | Yes                  | **Strong circularity** (both structural and distributional bias)   |
  | No           | Yes                  | **Model circularity** (distributional bias only, most common case) |
  | Yes          | No                   | **Structural circularity** (unlikely in practice)                  |
  | No           | No                   | **No circularity** (proceed normally)                              |

If **no circularity** (rare: typically human-written codebase being audited by Claude): inform the
user that blindspot's countermeasures are not load-bearing here, but proceed anyway, since the user
explicitly invoked `/audit:blindspot`, so honor that.
Skip the cross-model judge to avoid wasting an
OpenRouter call, run the original audit skill directly as an Agent (wait for its completion notification as described under "Waiting for the Agents"), and report with the fallback-mode template of Phase 2, with four substitutions: `**Verdict:** No circularity`, `**Countermeasures applied:** Skipped (no circularity detected)`, the entire `### Circularity Warning` section replaced by one line stating why the cross-model layer was skipped, its heading, its paragraph, the `**Known bias risks:**` list and the `**Manual countermeasures recommended:**` list all going, and the Transparency `Residual bias risk` line reading `Low, reviewer and target share no model family` instead of the `HIGH` wording.
The template's other warnings describe a circular review that did not happen, and its `OPENROUTER_API_KEY not set` wording would be false here.

If circularity detected: report the verdict and proceed to Phase 1.

### Report to user

```
## Circularity Detection

**Audit skill:** <skill-name>
**Target:** <target-path>
**Path overlap:** Yes/No, <explanation>
**Model family overlap:** Yes/No, <explanation>
**Verdict:** <Strong circularity / Model circularity / Structural circularity / No circularity>

Proceeding with countermeasures.
```

On the `No circularity` verdict, replace the last line with `No countermeasures needed; running the audit skill directly.`

## Phase 1: Cross-Model Routing

The primary countermeasure is routing part of the audit to a model from a different family
via OpenRouter.

### Detect OpenRouter availability

```bash
test -n "$OPENROUTER_API_KEY" && echo "openrouter:available" || echo "openrouter:missing"
```

### If OpenRouter available: Pick external model

Before spawning the cross-model judge, present the model menu to the user and wait for their choice.
The curated entries were checked against the OpenRouter catalog on 2026-09-15; an entry that OpenRouter rejects as unknown has been retired and the list is due for review.
Their IDs come from the table in `agents/cross-model-judge.md`, which is authoritative: change one there first, then re-render this menu from it.
Display as plain text, not through `AskUserQuestion`, whose option cap would hide entries.
Translate the prose into the user's language, keeping the model IDs, the option numbers and the entry order as written:

```
External model for cross-model judge. The audit is being run by Claude, so the goal is a second opinion from a non-Claude family.

  1. google/gemini-3.1-pro-preview : default. Google's frontier reasoning model, far from Claude's training distribution. Preview release.
  2. google/gemini-3.8-flash       : same family as 1, cheaper and faster. Use for large targets where cost matters.
  3. openai/gpt-5.6-sol            : OpenAI's GPT-5.6 flagship reasoning model. Different family from 1, useful if you've already audited with Gemini.
  4. deepseek/deepseek-v4-pro-0813 : DeepSeek's large MoE reasoning model. Low cost, alternative distribution.
  5. qwen/qwen3.8-max-0902         : Alibaba's large MoE model, alternative distribution. Pick when other models converge and you want a wildcard.
  6. x-ai/grok-4.6                 : xAI's reasoning model. One more family for a third pass.
  7. Custom                        : type any OpenRouter model ID. A cost notice is shown before launch.

Quick rule: for a one-shot audit, pick 1. For a second pass after Gemini, pick 3 or 4 (different family). For speed on a large artifact, pick 2.

Your choice [1-7, or `default` for 1]:
```

**On user response:**

- **`1`-`6`** → map to the corresponding curated entry (see `agents/cross-model-judge.md` for the canonical mapping).
  Use that model ID as `EXTERNAL_MODEL`.
- **Empty / `default` / "1"** → use `google/gemini-3.1-pro-preview`.
- **Full model ID matching one of the curated entries** (e.g., `openai/gpt-5.6-sol`) → accept and use it.
- **`7` / `custom`** → trigger the custom flow described below.
- **Anything else / ambiguous** → re-present the menu once with a one-line clarification ("Pick a number 1-7, or reply `default` for 1."), then default to `1` on a second ambiguous response.

**Custom model flow (option 7):**

1. Prompt: `OpenRouter model ID (e.g., provider/model-name):` and wait for input.

2. Validate the input format with regex `^[A-Za-z0-9_-]+/[A-Za-z0-9._-]+(:[A-Za-z0-9._-]+)?$` (letters, digits, dashes/dots/underscores; case-insensitive; exactly one slash; an optional `:variant` suffix, which 96 of the 447 catalog IDs carry, `:free` and `:batch` among them; no spaces).
   If invalid, re-prompt once showing the expected pattern.
   On second invalid input, abort the custom flow and default to `1`.
   Refuse, then re-prompt, an ID whose provider segment is `anthropic` or whose model segment contains `claude` (case-insensitive): a same-family judge would pass "Verify the external call" and be reported as cross-model evidence.
   Refuse a router ID (`openrouter/auto` and the other `openrouter/` entries) the same way: it names no concrete model, so the generation record returns whichever model answered and the check reports `model_mismatch`, leaving the whole audit unverified.
   The format regex already refuses the catalog's floating aliases (`~<provider>/<model>-latest`, 18 entries) for that same reason.

3. On valid format, display the cost notice and wait for confirmation:

   ```
   ⚠ Custom model: <model-id>

   This model is not in the curated list. OpenRouter pricing varies by orders of magnitude across providers and tiers; frontier reasoning models can be 50-100× the cost per call of smaller mid-tier models.

   Verify current pricing at https://openrouter.ai/<model-id> before continuing.

   Proceed with <model-id>? [y/N]:
   ```

4. On `y` / `yes` → use the custom ID as `EXTERNAL_MODEL`.
   On `N` / empty / anything else → return to the main model menu (re-display from the top).

**No silent interpolation.** Beside the Claude-family and router refusals, the format regex is the only validation done by the skill; it rejects shell-suspicious characters (spaces, `;`, `|`, `$`, `` ` ``, backticks, etc.) before the value ever reaches the agent.
The agent passes that ID through `jq --arg` (see `agents/cross-model-judge.md`), which is injection-safe regardless, but the skill-level regex prevents accidental typos from triggering OpenRouter API errors that would consume a billing call.
The target content is covered by a different mechanism: the agent writes the audit prompt to a file and passes it with `--rawfile`, so it never enters the shell source.

**Do not persist the user's choice.** Same reasoning as walkthrough's notices: a "remember my pick" toggle would silently lock the audit into one model family across future invocations, defeating the purpose of cross-model judging.
The menu is cheap (one reply for default) and the right model can depend on what the user already audited.

### Launch cross-model judge

First run `date +%s` and write its output to `judge-since.txt` in the session scratchpad directory: "Verify the external call" below rejects a generation created before it, which is how a real ID replayed from an earlier audit is caught.
The value is captured here and consumed after a turn boundary this skill imposes on itself, so neither a shell variable nor the transcript carries it reliably across a long agent run or a compaction.

Then check `EXTERNAL_MODEL` against the live catalogue, before either Agent is spawned.
The judge reads the whole target and builds its prompt before OpenRouter ever sees the ID, so a retired curated entry or a mistyped custom one from option 7, whose only other gate is the format regex, costs a full reviewer run alongside it.
The endpoint needs no key, so nothing here touches `OPENROUTER_API_KEY`.

```bash
MODELS=$(curl -sS -m 30 https://openrouter.ai/api/v1/models)
if [ -z "$MODELS" ]; then
  echo "check:unavailable"
elif printf '%s' "$MODELS" | jq -e --arg m '<EXTERNAL_MODEL>' '[.data[].id] | index($m)' >/dev/null; then
  echo "model:ok"
else
  echo "model:absent"
fi
```

`model:ok` proceeds.
`model:absent` names the model, states that the catalogue does not carry it, and re-presents the menu; a curated entry landing here has been retired, so say that the list is due for review.
`check:unavailable` proceeds anyway and says so in one line, the lookup having failed rather than the model, since an API refusal still surfaces through the judge's error branch.

Spawn the **cross-model-judge** agent (see agents/cross-model-judge.md) with these inputs.
It needs `Write`, for the prompt file it passes to `--rawfile`, and gets it from its own Agent grant rather than from this skill's `allowed-tools`, which covers the orchestrator alone and deliberately carries no `Write`: the orchestrator's one file write is a Bash redirection.

- `TARGET_PATH`: the resolved `<target-path>` from invocation
- `ARTIFACT_TYPE`: derived from the target-type detection in "Reviewer selection" Step 3.
  When `--reviewer` made Step 2 skip Steps 3 and 4, still run Step 3's target-type detection to obtain this value.
  Map the suggested category back to the agent's expected value:
  - `skill-tool` (skill audit) → `"skill"`
  - `skill-tool` (MCP audit) → `"mcp-server"`
  - `skill-tool` (Claude-interpreted instructions, agent definition, or Claude-interpreted artifact) → `"other"`
  - `code` (project-wide or focused) → `"codebase"`
- `AUDIT_FOCUS`: derive from the resolved reviewer's `SKILL.md`.
  Read its `description:` frontmatter field, and the body when that field names no dimension, identify the audit dimensions it claims to check: verbs like "review", "audit", "find", followed by their objects (e.g. "trigger edge cases, instruction ambiguities, contradictions, cross-file coherence, gaps" for skill-adversary; "tool-selection ambiguity, discoverability gaps, schema anti-patterns, semantic drift, error handling" for mcp-adversary; "code quality, security, architecture, test coverage" for critical-code-reviewer), and join them as `"<dim1>, <dim2>, ..."`.
  Take them from what the reviewer claims to audit, never from the clauses that scope it out (`Does not auto-trigger on ...`, `Not for: ...`), whose objects read as dimensions too.
  If the reviewer surfaces no concrete dimensions, fall back to the generic `"code quality, security, correctness, completeness"`.
  Never pass an empty or literal `"undefined"` value; the external model would receive `AUDIT FOCUS: ` with no focus and produce a less targeted audit.
- `EXTERNAL_MODEL`: the model ID selected at the previous step

Then spawn the original audit skill as a **second Agent** (not via the Skill tool, since the Skill tool would run the audit inline in the main context and exhaust the budget; the walkthrough orchestrator follows the same convention for the same reason).
The Agent's prompt instructs it to read the target audit skill's `SKILL.md` and execute its procedure on `<target-path>`.
Reading a `SKILL.md` is not the same as the harness loading it, and the reviewer is whatever the scan surfaced rather than a known skill, so two properties of that prompt are load-bearing.
Pass `<target-path>` already resolved to an absolute path, which keeps the reviewer on its path-first branch and away from any name-resolution step fed by `!`-expanded blocks, which stay literal text when a file is read.
State that the Agent cannot reach the user, so a step that would ask a question proceeds on a stated assumption and reports it rather than blocking: `AskUserQuestion` is withheld from every subagent, and a reviewer built around an interactive walkthrough, `posit-dev:critical-code-reviewer` among the scanned candidates, is where that bites.

**Canonical parallel pattern.** Emit both Agent tool calls in a single message: two `Agent` blocks side by side.
Never use the Skill tool for either: it would run the audit inline in the main context and block until it finishes.

**Waiting for the Agents.** In an interactive session Claude Code runs every Agent in the background, so both calls return before either audit is done and each result arrives as a completion notification in a later turn.
Tell the user in one line that both audits are running and end the turn there; the notifications resume it, and Phase 2 starts once both have arrived.
Waiting is that, and nothing else: do not poll with `TaskOutput`, do not ask the user anything, and do not compile a partial report when the first one lands.
A failed Agent still notifies; its source counts as errored under Phase 2's convergence rule.
If the Agents ran in the foreground instead (results already in the tool results), continue the same way.

### Verify the external call

The judge's report comes from a subagent whose tool calls the user does not see, so nothing in it proves the OpenRouter call happened.
OpenRouter's generation record does: it exists only for an ID OpenRouter issued, and it names the model that served the call.
Run this in the main context once the judge has notified, before Phase 2, unless the judge reported `Failed` (its source already counts as errored, and it is reported with the "If the external call is unverified" template, `<status>` being `failed` and `<reason>` the judge's error).

Take `GEN_ID` from the judge's `**Generation ID:**` line, as the bare `gen-...` token and never a `GENERATION_ID:` label copied along with it, which the script rejects as malformed; `MODEL` is `EXTERNAL_MODEL`, never the judge's `**Served model:**` line, since checking the record against the judge's own claim would only test the judge against itself; `<JUDGE_SINCE>` is the value in `judge-since.txt`, deleted right after it is read so that a later invocation in the same session cannot inherit a bound from this one and check a fresh generation against a stale one.
When that file is missing, the source is unverified, `<status>` is `no-bound` and `<reason>` is `the audit's start bound was not preserved`.
Never re-derive the bound with a fresh `date +%s`: it would sit after every genuine record and return `stale` on a real call, reporting a success as unproven.
When the ID line reads `none`, skip the script: the external source is unverified, `<status>` is `no-id` and `<reason>` is `the judge reported no generation ID`.
The script sits in the walkthrough skill, resolved as for `scan-reviewers.py` in "Reviewer selection" (the same fallback applies when `$CLAUDE_PLUGIN_ROOT` is unset).
Run it as one Bash call with `timeout: 600000`: OpenRouter publishes a record about two minutes after the call (measured 2026-09-19), and the script retries a missing one every 15 s for up to 300 s.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/audit/walkthrough/scripts/openrouter-generation.py" --since '<JUDGE_SINCE>' --check '<GEN_ID>' '<MODEL>'
```

stdout holds a one-entry JSON array: `status`, plus what OpenRouter declares for the ID (`model`, `provider`, `total_cost`, `created_at`).
Exit 2 means a malformed invocation (a mistyped or placeholder ID fails the pattern check): the source is unverified, `<status>` is `malformed` and `<reason>` is the script's last stderr line, verbatim.
- `verified`: the external source stands.
Phase 2 reports the declared model, provider and cost.
- Any other status (`model_mismatch`, `stale`, `not_found`, `error`): the external source is unverified, `<status>` is that status verbatim, and `<reason>` quotes the script's own output for it, its `error` string, the `model` the record names against the one requested, or its `created_at`.

Across the four branches `<status>` is a single token and `<reason>` is verbatim from whatever produced the failure, the judge's error, the script's stderr, or the script's JSON, never a paraphrase: paraphrasing `stale` drops the `created_at` that says how stale.
`unverified` is the verdict on the external source and never a value of `<status>`.

An `unverified` source counts as errored under Phase 2's convergence rule, so no convergence analysis is built on it; report with the "If the external call is unverified" template below.
Never drop its findings silently and never present them as cross-model evidence.

### If OpenRouter not available: Fallback mode

Do NOT silently skip.
Instead:

1. Warn the user that no cross-model countermeasure is available
2. Spawn the audit skill as an **Agent** (same pattern as the cross-model-judge path above; never via the Skill tool, to keep the orchestrator's context budget intact), then wait for its completion notification as described under "Waiting for the Agents"
3. Append a **fallback transparency block** to the report (see Phase 2)

## Phase 2: Transparent Report

After collecting results, compile the final report.

A source whose Agent failed outright has no findings to place, so its section states that failure and its reason verbatim in place of them, in whichever template applies.
That covers both `### Same-Model Findings (Claude)` instances, `### Unverified External Findings` and the fallback's `### Audit Findings`: a template is never rendered with an empty findings section and no explanation.

### If cross-model judge was used

Use this template only when "Verify the external call" returned `verified`; otherwise use "If the external call is unverified" below.
`<model-id>` is the model OpenRouter declared in the generation record, and `<generation-id>`, `<provider>` and `<cost>` come from the same record.

```
## Blindspot Review: <target>

### Circularity Assessment

**Audit skill:** <skill-name>
**Verdict:** <Strong circularity / Model circularity / Structural circularity>
**Countermeasures applied:** Cross-model judge via OpenRouter (<model-id>, generation <generation-id> verified)

### Cross-Model Findings (<model-id>)

<Findings from the external model, formatted as a numbered list with severity>

### Same-Model Findings (Claude)

<Findings from the original audit skill>

### Convergence Analysis

To build this section, compare the two finding sets using semantic matching. Wording will differ; match on substance, not phrasing.

**Matching procedure.** For each external finding, scan all Claude findings for a match. Two findings match when **at least 2 of these 3 signals align**:

1. **Same scope**: same file or same logical section (e.g. same agent, same Phase block, same function). Cross-file findings match when they target the same conceptual unit.
2. **Same root cause**: same underlying defect class (e.g. "stale documentation vs implementation", "missing error path", "ambiguous instruction", "unreachable branch"). Symptom phrasing differs; defect class doesn't.
3. **Same fix mechanism**: the corrective action would touch the same surface (same lines, same instruction, same conditional). If both findings would be resolved by the same edit, they match.

Pairing is one-to-one: a finding already paired is no longer available on the other side.
When several findings match the same one, pair the closest and leave each remaining finding unpaired, in its own bucket and counted once, which keeps the identity below satisfiable.
When only 1 signal aligns, treat as a near-miss: classify both findings separately (one Claude-only, one external-only) and add a brief note in the Convergence Analysis that they may target related issues. When 0 signals align, the findings are independent.

Then: for each Claude finding, check whether it was already matched to an external finding. Classify every finding into exactly one bucket: agreed, Claude-only, or external-only.

Zero findings is a valid input, not a missing source: with an empty source every finding of the other one lands in its own bucket, which is the clearest blindspot signal the skill produces, and the identity below still holds with `A = 0`.
Skip the convergence analysis only when a source errored out; then omit the `### Convergence Analysis` heading entirely, since walkthrough keys its bucket routing on that heading, and note which source is missing.

**Structural single-bucket note.** The two sources do not answer in the same shape: an audit skill can report a class of finding the judge's prompt never asks for, trigger-boundary false positives and negatives being the usual case, and those land in a single bucket by construction rather than by divergence.
Label them as such in the bucket list and in the Transparency block, so that a bucket built on a structural gap is not read as a blindspot signal.

**Meta-bias note.** This matching step is performed by Claude, the same model whose self-preference is being audited. Self-preference can bias the classification in two directions: (a) over-matching (declaring "agreed" to suppress an external-only finding Claude missed), (b) under-matching (declaring "Claude-only" when Claude agreed but used different wording, inflating own-findings novelty). Boundary cases between agreed and Claude-only deserve the most skepticism. This caveat is also surfaced in the Transparency block.

**Counts (mandatory whenever the Convergence Analysis section is rendered: verbatim, never omitted).** Before listing the buckets, emit a single line of the form:

    **Counts:** <R> raw findings (<E> external + <C> Claude) → <A> agreed pair(s) + <CO> Claude-only + <EO> external-only

Where: `R = E + C` (total raw count across both sources before convergence), `E` counting the external findings the report actually lists, so a trailing `N additional minor findings omitted for brevity` line never enters it; `C` counting the reviewer's enumerated findings on the same terms, its own summary total never standing in for them, since the two disagree whenever the reviewer folds one finding into another, which counts once, and the report then states the discrepancy in a parenthetical under the Counts line instead of picking a number in silence; `A` = number of agreed pairs (each pair counts once here); `CO` = items in the Claude-only bucket; `EO` = items in the External-only bucket. The identity `2·A + CO + EO = R` must hold; if it does not, the bucketing has dropped or duplicated a finding and must be redone before continuing. Near-miss items count as **two separate findings** (one Claude-only, one external-only) per the matching-procedure rule above; never collapse a near-miss into a single line in the counts or in the bucket lists.

**Atomicity.** Both counts rest on one item per distinct root cause, and nothing else in this section fixes that unit.
Findings differing in root cause stay separate items, before matching and in the bucket lists alike: the near-miss rule above is the only sanctioned way to carry two related findings, and grouping outside it moves `R`, `CO` and the apparent convergence rate together.
The identity does not catch that, balancing the same whether two findings were merged or one was split, because it checks the bucketing against `E` and `C` and never `E` and `C` against the sources.
It guards the classification pass, not the enumeration feeding it, which is why the counting rules above are stated rather than left to the matcher.

**Agreed findings** (flagged by both models):
<List: these are high-confidence findings>

**Claude-only findings** (not flagged by external model):
<List: these may reflect self-preference bias or genuine issues the external model missed>

**External-only findings** (not flagged by Claude):
<List: these are the blindspot candidates, issues Claude may have systematically overlooked>

### Transparency

- **Circularity type:** <verdict>
- **External model used:** <model-id> via OpenRouter
- **External call:** generation <generation-id>, served by <provider>, <cost> USD, verified against OpenRouter's generation record (also listed on the Activity page of the OpenRouter account)
- **Audit focus sent:** the `AUDIT_FOCUS` string verbatim, or `generic fallback` when the derivation surfaced no dimension; it is read off the reviewer's prose rather than parsed, so two runs on the same reviewer can word it differently, and without it a reader cannot tell a difference between two reports from a difference in the rubric the judge was given
- **External coverage:** the judge's `**Truncated:**` line verbatim; when files were dropped, an external-only gap on them reflects content the external model never saw
- **External completeness:** the judge's `N additional minor findings omitted for brevity` line verbatim, or "none"; when the external model omitted findings its set is partial, and an empty external-only bucket then says less than it appears to
- **Selection asymmetry:** <files only one source's selection step included, naming which source read them, or "none">; the judge reads `evals/` and a reviewer may exclude it, so an external-only finding on such a file records a scope gap rather than a Claude blindspot and is excluded from the recommendation below
- **Single-bucket by construction:** <list of findings the other source was never asked for, or "none">, whose bucket records a gap in the two prompts rather than a divergence between the models
- **Residual bias risk:** Cross-model judging reduces but does not eliminate bias.
  The external model has its own biases. Convergent findings are highest confidence.
  Divergent findings warrant human attention.
- **Convergence matching done by Claude:** the agreed/Claude-only/external-only classification
  was assigned by Claude, the same model being audited for self-preference. Treat boundary
  cases between agreed and Claude-only with extra skepticism; Claude may have over-matched
  to suppress findings it missed, or under-matched to inflate its own findings' novelty.
- **Recommendation:** Review "External-only findings" with particular care:
  these represent potential blindspots in Claude's self-evaluation.

### Next step

Run `/audit:walkthrough` (no arguments) to process these findings interactively. The walkthrough auto-detects this report's `### Convergence Analysis` section, tags each finding by bucket (agreed / claude-only / external-only), and routes L2 cross-model verification accordingly: severity trigger skipped on agreed (an L1 divergence or failure still escalates), forced on claude-only, standard severity rules on external-only (the bucket tag alone does not force L2; the parent surfaces a "Claude tends to under-rate these" warning).
```

When the `### Convergence Analysis` heading was omitted because a source errored, replace that paragraph: there are no buckets to detect, so the walkthrough applies its standard L2 check, on Blocking/Required/Critical findings and on L1 divergences or failures, and the sentence above would promise a routing the report cannot support.

### If the external call is unverified

When "Verify the external call" did not return `verified`, the external findings cannot count as a second model's opinion.
Report them apart, with no Convergence Analysis, so `/audit:walkthrough` does not route L2 on buckets built from them:

```
## Blindspot Review: <target>

### Circularity Assessment

**Audit skill:** <skill-name>
**Verdict:** <Strong circularity / Model circularity / Structural circularity>
**Countermeasures applied:** None verified (external call unverified: <status>, <reason>)

### Same-Model Findings (Claude)

<Findings from the original audit skill>

### Unverified External Findings (reported as <EXTERNAL_MODEL>)

<Findings from the judge's report, unmodified. No OpenRouter generation record confirms that an external model produced them.>

### Transparency

- **Circularity type:** <verdict>
- **External model used:** unverified. Generation ID <generation-id or "none">, check status <status>: <reason>
- **Residual bias risk:** HIGH, the cross-family mitigation could not be proven to have run.
  Treat every finding as a same-model finding.

### Next step

Re-run `/audit:blindspot <target-path>` to retry the external call. `/audit:walkthrough` on this report applies the standard L2 check (no bucket routing).
```

### If fallback mode (no OpenRouter key)

Once the audit skill Agent launched in the Phase 1 fallback, or by the Phase 0 `No circularity` path, has delivered its report (it runs once, never a second time here), append:

```
## Blindspot Review: <target>

### Circularity Assessment

**Audit skill:** <skill-name>
**Verdict:** <Strong circularity / Model circularity / Structural circularity / No circularity>
**Countermeasures applied:** None (OPENROUTER_API_KEY not set)

### Audit Findings

<Findings from the original audit skill>

### Circularity Warning

This audit was performed by Claude on an artifact sharing its model family: Claude authored it, or it was written for Claude to interpret, or its provenance could not be established.
No cross-model countermeasure was available.

**Known bias risks:**
- Self-preference bias: Claude systematically rates its own outputs higher
  (Panickssery et al., 2024)
- Shared RLHF distribution: reviewer and target share the same notion of "good output"
- Sycophantic agreement: tendency to validate presented content rather than critique it

**Manual countermeasures recommended:**
1. Set OPENROUTER_API_KEY to enable automatic cross-model judging:
   - Get a key at https://openrouter.ai/keys (free tier available)
   - `export OPENROUTER_API_KEY=<your-key>` in your shell (and add the line to `~/.bashrc` / `~/.zshrc` for persistence)
   - Restart Claude Code so the new env is inherited by the MCP servers and Bash subshells
   - Re-run `/audit:blindspot <target-path> [--reviewer <audit-skill>]`; the cross-model judging path will activate automatically
2. Ask a human reviewer to specifically check for findings that seem surprisingly lenient
3. Challenge any "no issues found" conclusions; absence of findings is itself a red flag
   in a circular review
4. Compare severity ratings against similar non-circular reviews for calibration

### Transparency

- **Circularity type:** <verdict>
- **External model used:** None
- **Residual bias risk:** HIGH, no cross-family mitigation applied.
  All findings should be treated with additional skepticism.

### Next step

Run `/audit:walkthrough` (no arguments) to process these findings interactively. Without cross-model convergence data, findings go through the walkthrough's standard L2 cross-provider check, on Blocking/Required/Critical findings and L1 divergences or failures (no bucket routing, since no external model contributed).
```

## Important constraints

- **Orchestrator only.** This skill never performs the audit itself.
  It detects circularity,
  routes to an external model when possible, and wraps the results in transparency.
- **Does not block audits.** If circularity is detected but no countermeasure is available,
  the audit still runs, with warnings.
- **No duplicate work.** The original audit skill runs exactly once.
  The cross-model judge
  runs independently.
  Results are compared, not merged.
- **Transparency is mandatory.** Every report includes the circularity assessment and
  countermeasures applied (or not applied), regardless of findings.
- **An external call counts only once proven.** The judge's generation ID is checked against OpenRouter's generation record in the main context; without a `verified` status, its findings are reported as unverified and never feed the convergence analysis.
- **Model selection.** The external model is picked interactively at invocation via the menu in Phase 1 (default on `default` or `1`: `google/gemini-3.1-pro-preview`, strong reasoning, non-Claude family).
  Six curated options are surfaced; option 7 accepts any non-Claude, non-router OpenRouter model ID after format validation and an explicit cost-warning confirmation.
  Whichever is chosen is then checked against OpenRouter's live catalogue before either Agent is spawned, so a retired or mistyped ID costs a one-second lookup rather than a reviewer run.
  Both the skill and the agent re-validate against the format regex `^[A-Za-z0-9_-]+/[A-Za-z0-9._-]+(:[A-Za-z0-9._-]+)?$` (defense in depth), and the agent passes the ID with `jq --arg` and the audit prompt with `--rawfile` from a file for the actual API call.
- **No credentials in prompts.** The OPENROUTER_API_KEY is read from the environment.
  Never log, echo, or include it in any output.
