---
name: review-walkthrough-orchestrator
description: Parses arguments, detects deployment context, injects calibration, and launches the reviewer skill. Returns the detected context, reviewer used, and parsed flags so the walkthrough can proceed.
---

# Review Walkthrough — Orchestrator

You prepare and launch a code review for the review-walkthrough skill. You receive a target and optional flags, and your job is to detect the deployment context, calibrate severity, and invoke the reviewer.

## Input

Extract from the user's request:
- **target**: file(s) or directory to review
- **reviewer**: `--reviewer` value (no hardcoded list, no silent default — see "Reviewer selection" below)
- **adversarial**: `--adversarial` flag (boolean, default false)
- **batch**: `--batch` / `--no-batch` override (optional)

`--adversarial` can also appear in walkthrough-only mode (no target) — parse it in that case too.

## Reviewer selection

The set of available reviewers is **discovered at runtime**, not hardcoded. This lets the skill adapt to whatever reviewer skills the user has installed (built-ins, plugins, custom) without needing edits here.

**Step 1 — scan available reviewers.** Run the helper script:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/scan-reviewers.py"
```

Note: `${CLAUDE_SKILL_DIR}` is the absolute path to this skill's directory. If your runtime does not export it as an environment variable, substitute it with the path announced by Claude Code at the top of the skill prompt (`Base directory for this skill: <path>`).

It returns JSON with `candidates`: each candidate has `name`, `category` (`code` / `skill-tool` / `unknown`), `path`, and `description_excerpt`. The script scans active skills under `~/.claude/skills/` and the install paths listed in `~/.claude/plugins/installed_plugins.json`, filters by name+description heuristics, and excludes self-references (`review-walkthrough`, `blindspot-review`, etc.). If the script returns zero candidates, tell the user the scan found no reviewer skills installed and ask them to specify one manually (e.g. by full skill path) — do not invent names.

**Step 2 — validate `--reviewer` if provided.** If the user passed `--reviewer <name>`, check that `<name>` is in the scanned candidates list (match by `name` or by its bare suffix after `:`). If valid, use it as-is and skip steps 3–4. If invalid, list the scanned candidates back to the user and ask them to pick one.

**Step 3 — detect target type and pick the suggested category.** Apply these rules in order on the resolved target path; first match wins:

| Signal on resolved target | Suggested category |
|---|---|
| Target is or contains a `SKILL.md`, or path is under `~/.claude/skills/` or `<plugin>/skills/` | `skill-tool` (skill audit) |
| Target contains MCP tool definitions (e.g. `@mcp.tool` / `Server.tool` decorators, `mcp.json`, `mcp_server.py`, `*-mcp/` directory) | `skill-tool` (MCP audit) |
| Target is a project root (directory containing a top-level `README` plus a manifest like `pyproject.toml`, `package.json`, `Cargo.toml`, `DESCRIPTION`, etc.) and not a single file | `code` (project-wide) |
| Otherwise (single file, sub-tree of code, glob expansion) | `code` (focused) |

Within the matched category, pick the suggested reviewer using these heuristics on the candidate names (case-insensitive substring):

- `skill-tool` (skill audit): prefer a candidate matching `skill` first, otherwise fall back to any `skill-tool` candidate.
- `skill-tool` (MCP audit): prefer a candidate matching `mcp` first, otherwise fall back to any `skill-tool` candidate.
- `code` (project-wide): prefer a candidate matching `full` or `project` first, otherwise fall back to any `code` candidate.
- `code` (focused): prefer a candidate matching `critical` or `code-review` first, otherwise fall back to any `code` candidate.

If multiple candidates tie within the preferred sub-rule, pick the one with the shortest `name`. If the matched category has zero candidates in the scan, fall back to the other category's best match and surface this in the rationale.

**Step 4 — present the suggestion and wait.** Show the user the scanned list (grouped by category), the suggested reviewer, and a one-line rationale tying the suggestion to the detected target type. The format below is illustrative — the actual reviewer names come from the scan output, not from this template:

```
No --reviewer specified. Scanned reviewers:
  [code]       <names from scan>
  [skill-tool] <names from scan>
Suggested: <chosen name> (<one-line rationale>).
Pick a reviewer or press Enter to accept the suggestion.
```

On the user's response: empty input or explicit confirmation → use the suggested reviewer; a candidate name from the scanned list (full or bare suffix) → use that one; anything else → re-prompt with the same options. Once the choice is locked in, carry the chosen reviewer's `category` forward — it gates calibration injection (see "Inject calibration and launch").

## Circularity check (blindspot suggestion)

Before doing any heavy work (memory loading, calibration, reviewer launch), check whether the upcoming review is structurally circular — Claude reviewing a Claude-authored artifact in the same skill family. If so, suggest chaining via `/blindspot-review` instead of running the reviewer directly.

**High-signal circularity (suggest blindspot):**
- chosen reviewer's `category` from the scan is `skill-tool` AND target contains a `SKILL.md` or MCP tool definitions (the artifact was authored for Claude, by Claude, and is now reviewed by Claude with shared distributional assumptions), OR
- target's resolved absolute path is inside `~/.claude/skills/` or any plugin's skills directory (any reviewer — the artifact is part of Claude's own skill ecosystem).

If none of these apply, skip this section silently — proceed to "Detect deployment context".

If a high-signal case matches, present this nudge to the user (one prompt, then wait for response):

```
Circularity detected — <reason in one line>.
blindspot-review can route a parallel cross-model audit (via OpenRouter) and tag findings as agreed/Claude-only/external-only before the walkthrough. The walkthrough will then skip L2 on agreed findings and force L2 on Claude-only ones.

Chain via /blindspot-review first? [y/N]
```

**On user response:**

- **No / empty / anything other than explicit yes** → proceed to "Detect deployment context" as normal.
- **Yes** → delegate to `blindspot-review` via the Skill tool, passing `<target> --reviewer <reviewer>` (harmonized syntax — same positional + flag convention as walkthrough). When it completes, its report (containing the `### Convergence Analysis` section) is now in the conversation. Skip the rest of the orchestrator's work — no calibration, no separate reviewer launch — and emit the structured block below with `reviewer: blindspot-review+<original-reviewer>`, `context: <not-detected>` (deployment context detection is moot here — the walkthrough's Step 1 will read the blindspot report directly), `calibrated: no`, and the blindspot report verbatim in the `--- REVIEW REPORT ---` section. The walkthrough's Step 1 will detect the convergence section and tag findings accordingly.

If `OPENROUTER_API_KEY` is not set, blindspot-review will fall back to single-model mode and append a warning. That is still useful — do not pre-empt the suggestion based on key absence; let blindspot-review handle it transparently.

## Detect deployment context

Determine the deployment context to calibrate review severity. Check in order:

1. **Path heuristics** (target's resolved absolute path):
   - `~/.local/bin/`, `~/bin/`, `~/scripts/`, `~/dotfiles/`, or any path under the user's home not inside a project with CI config → `personal`
   - Project root contains `.internal` marker or a project memory tags it as internal → `internal`

2. **CI classification** (if `.github/workflows/`, `.gitlab-ci.yml`, or `Jenkinsfile` exists):

   Split CI signals into two categories:

   - **CI deploy** (triggers `production`): Dockerfile, `docker-compose.yml`, `k8s/`, `deploy/`, `terraform/`, `helm/`, `.elasticbeanstalk/`, `appspec.yml`, `fly.toml`, `render.yaml`, or workflow files whose name contains `deploy`, `release`, or `cd` (case-insensitive).
   - **CI quality-only** (triggers `internal`): everything else — test, check, lint, coverage, docs workflows (e.g. `R-CMD-check.yaml`, `pytest.yml`, `pkgdown.yaml`, `test-coverage.yaml`, `eslint.yml`). These indicate project hygiene, not deployment.

   If **any** CI deploy signal is found → `production`. If CI exists but **only** quality signals → `internal`.

3. **Memory check**: look for `project_deployment_context.md` memory file. If found, use it.

4. **Fallback**: ask the user — "Is this personal tooling, internal team tooling, or production code?" Persist the answer in a `project_deployment_context.md` memory file.

## Load target project memories

The review-walkthrough skill runs from its own working directory, not from the target project. This means Claude Code's automatic project memory loading does **not** include the target's memories. You must load them explicitly.

1. Resolve the target's absolute path (e.g., `/home/julien/Documents/pro/r_pkg/pkg_edstr`).
2. Derive the Claude Code project memory directory: `~/.claude/projects/<encoded-path>/memory/`, where `<encoded-path>` is the absolute path with `/` replaced by `-` and leading `-` preserved (e.g., `/home/julien/Documents/pro/r_pkg/pkg_edstr` → `-home-julien-Documents-pro-r-pkg-pkg-edstr`).
3. Check if `feedback_review_severity.md` exists in that directory. If it does, read it — this contains reviewer calibration rules from prior sessions (dismissed false positives, R idioms not to flag, etc.).
4. Check if `MEMORY.md` exists in that directory. If it does, scan it for other feedback-type memories that might be relevant to the review (e.g., `feedback_code_text_english.md`). Read any that seem review-relevant.
5. Collect all loaded memory content into a `[prior calibration]` block.

If no target project memories exist, skip this step — the reviewer runs without prior calibration context.

## Inject calibration and launch

Context injection applies **only** when the chosen reviewer's `category` from the runtime scan is `code`. For `skill-tool` and `unknown`, no calibration is injected — launch with the original prompt. The `unknown` category is treated fail-safe: a reviewer that receives calibration it doesn't understand is more dangerous than one running uncalibrated.

When injection applies:
- **personal**: read `templates/calibration-personal.md` and prepend it to the reviewer prompt
- **internal**: read `templates/calibration-internal.md` and prepend it
- **production**: no calibration block — full adversarial severity

**Prior calibration** (from target project memories) is injected for **all** code reviewers, regardless of deployment context. It supplements the context-based calibration, not replaces it. Append it after the context calibration block (or as the only calibration if context is production).

**Launch the reviewer as a foreground Agent** (not a Skill). This is critical — running the reviewer in the same context window as the walkthrough exhausts the context budget and causes the walkthrough to silently abort. The Agent isolates the reviewer's work (file reads, sub-agents, bash commands) and returns only the final report.

Build the Agent prompt as follows:

```
[context calibration block, if applicable]

[prior calibration block, if found — prefix with "Prior review calibration for this project (from previous sessions):"]

You are running the <reviewer> skill. Review: <target>

IMPORTANT — output format: return ONLY the structured findings report. Do not include your intermediate reasoning, file contents you read, or tool call results. Each finding must include: severity tier, file(s) and line(s), description, and suggested fix. Keep each finding to one short paragraph. Maximum 15 findings — if more exist, keep the 15 highest-severity ones and note how many were omitted. Do NOT report findings that contradict the prior calibration rules above — those patterns have been explicitly validated by the project author.
```

Launch with `Agent(prompt, description="review <target>")` in **foreground** mode — the walkthrough cannot proceed without the report.

For skill/tool reviewers (no calibration):
```
You are running the <reviewer> skill. Review: <target>

[same output format instructions as above]
```

If the reviewer agent fails or returns an empty result, tell the user and offer to retry or fall back to walkthrough-only mode.

## Output

After the reviewer Agent returns its report, emit the following structured block **exactly** (the parent skill parses it), followed by the Agent's report verbatim:

```
--- ORCHESTRATOR COMPLETE ---
context: <level> (<detection method>)
reviewer: <reviewer name>
calibrated: <yes|no>
adversarial: <true|false>
batch: <--batch|--no-batch|none>
--- REVIEW REPORT ---
<paste the Agent's returned report here, unmodified>
--- PROCEED TO STEP 1 ---
```

Do not stop after this block. Do not summarize the review. Do not ask the user what to do next. The parent skill takes over immediately.
