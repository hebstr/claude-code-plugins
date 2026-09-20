---
name: walkthrough-orchestrator
description: Parses arguments, detects deployment context, injects calibration, and launches the reviewer skill.
  Emits the detected context, reviewer used, and parsed flags so the walkthrough can proceed.
---

# Review Walkthrough: Orchestrator

You prepare and launch a code review for the walkthrough skill.
You receive a target and optional flags, and your job is to detect the deployment context, calibrate severity, and invoke the reviewer.

The walkthrough skill executes this file in its own main context, never as a subagent: several steps below wait on the user, and a subagent has no way to reach them.

## Input

Extract from the user's request:
- **target**: file(s) or directory to review
- **reviewer**: `--reviewer` value (no hardcoded list, no silent default, see "Reviewer selection" below)
- **batch**: `--batch` / `--no-batch` override (optional)

Adversarial cross-provider validation (L2) runs whenever `OPENROUTER_API_KEY` is set: no flag to parse.
Which findings it fires on is stated in one place only, the "Level 2: Cross-provider" triggers of `agents/ouroboros-bridge.md`, the severity trigger being exempted on the `agreed` bucket and forced on `claude-only`, so a summary that names severities alone is wrong in both directions.

## Reviewer selection

The set of available reviewers is **discovered at runtime**, not hardcoded.
This lets the skill adapt to whatever reviewer skills the user has installed (built-ins, plugins, custom) without needing edits here.

**Step 1: scan available reviewers.** Run the helper script:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/scan-reviewers.py"
```

Note: `${CLAUDE_SKILL_DIR}` is the absolute path to this skill's directory.
If your runtime does not export it as an environment variable, substitute it with the path announced by Claude Code at the top of the skill prompt (`Base directory for this skill: <path>`).

A path reaching a shell takes that variable; a path in a reading instruction does not.
The difference is who resolves it: a shell resolves against the working directory, which for a walkthrough is the user's project and holds none of this skill's files, while a file you are told to read is resolved against the skill directory, which is why `agents/...` and `templates/...` appear bare throughout these files and only the `python3` invocations are anchored.

It returns JSON with `candidates`: each candidate has `name`, `category` (`code` / `skill-tool` / `unknown`), `path`, and `description_excerpt`.
The script scans skills under `~/.claude/skills/`, under `.claude/skills/` from the working directory up to its repository root, and, for each plugin in `~/.claude/plugins/installed_plugins.json` installed for this project (user or managed scope, or a project/local install matching the current project) and not set to `false` in `enabledPlugins` (user, project, local and managed settings), the skills its marketplace entry declares, read from the install path or else from the marketplace catalog in `~/.claude/plugins/known_marketplaces.json` (the whole set for a marketplace-root `source`, otherwise alongside `<installPath>/skills/*/` and the paths `plugin.json` declares; paths outside the install path are ignored), filters by name+description heuristics, and excludes self-references (`audit:walkthrough`, `audit:blindspot`).
Plugin skills are named `plugin:skill`; user and project skills keep their bare name, and a personal skill shadows a project skill of the same name.
If the script returns zero candidates, tell the user the scan found no reviewer skills installed and ask them to specify one manually (e.g. by full skill path).

The zero-candidate test is not the only outcome worth reading.
The scan writes a diagnostic to stderr for an unreadable plugin manifest and for each malformed manifest entry, and keeps emitting well-formed JSON either way: the malformed-entry path skips that one plugin and leaves the others, so the count stays non-zero while a whole plugin's reviewers are missing.
The bare invocation above already puts that text in front of you, so nothing needs capturing; what is required is relaying it.
When the scan produced any stderr, say so when presenting the candidate list, naming what was skipped and that the list may be incomplete, rather than offering it as the full set of installed reviewers.
Do not invent names.

**Step 2: validate `--reviewer` if provided.** If the user passed `--reviewer <name>`, check that `<name>` is in the scanned candidates list (match by `name` or by its bare suffix after `:`).
If valid, use it as-is and skip steps 3 and 4.
If it is absent from the list but resolves to a readable `SKILL.md`, as a filesystem path to an existing `SKILL.md` or to a directory holding one, or as `<plugin>:<skill>` found under an install path in `~/.claude/plugins/installed_plugins.json` or at `~/.claude/skills/<skill>/SKILL.md`, accept it, warn in one line that the scan did not surface it, and skip steps 3 and 4.
The scan gates on the bare skill name against `review`, `adversary`, `audit`, `critic` and `sweep`, so a reviewer carrying none of them is missed and this path is the only way to reach it.
Otherwise, list the scanned candidates back to the user and ask them to pick one.

**Step 3: detect target type and pick the suggested category.** Apply these rules in order on the resolved target path; first match wins:

  | Signal on resolved target                                                                                                                                                           | Suggested category         |
  | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
  | Target contains MCP tool definitions (e.g. `@mcp.tool` / `Server.tool` decorators, `mcp.json`, `mcp_server.py`, `*-mcp/` directory)                                                 | `skill-tool` (MCP audit)   |
  | Target is a `SKILL.md`, holds one at its top level or skill directories (`*/SKILL.md`) one level down, or path is under `~/.claude/skills/` or `<plugin>/skills/`                   | `skill-tool` (skill audit) |
  | Target is a project root (directory containing a top-level `README` plus a manifest like `pyproject.toml`, `package.json`, `Cargo.toml`, `DESCRIPTION`, etc.) and not a single file | `code` (project-wide)      |
  | Otherwise (single file, sub-tree of code, glob expansion)                                                                                                                           | `code` (focused)           |

Within the matched category, pick the suggested reviewer using these heuristics on the candidate names (case-insensitive substring):

- `skill-tool` (skill audit): prefer a candidate matching `skill` first, otherwise fall back to any `skill-tool` candidate.
- `skill-tool` (MCP audit): prefer a candidate matching `mcp` first, otherwise fall back to any `skill-tool` candidate.
- `code` (project-wide): prefer a candidate matching `sweep`, `full` or `project` first, otherwise fall back to any `code` candidate.
- `code` (focused): prefer a candidate matching `critical` or `code-review` first, otherwise fall back to any `code` candidate.

If multiple candidates tie within the preferred sub-rule, pick the one with the shortest `name`; the same tie-break governs the `otherwise fall back to any <category> candidate` branch, where every candidate of that category ties by construction.
Say in the Step 4 rationale when the suggestion came from that fallback, so the user can override before the reviewer launches.
If the matched category has zero candidates in the scan, fall back to the other category's best match and surface this in the rationale.

**Step 4: present the suggestion and wait.** Show the user the scanned list (grouped by category), the suggested reviewer, and a one-line rationale tying the suggestion to the detected target type.
Present it as plain text, not through `AskUserQuestion`, whose option cap would hide candidates.
The format below is illustrative.
The actual reviewer names come from the scan output, not from this template:

```
No --reviewer specified. Scanned reviewers:
  [code]       <names from scan>
  [skill-tool] <names from scan>
Suggested: <chosen name> (<one-line rationale>).
Pick a reviewer or reply `ok` to accept the suggestion.
```

On the user's response: empty input or explicit confirmation → use the suggested reviewer; a candidate name from the scanned list (full or bare suffix) → use that one; anything else → re-prompt once with the same options, then use the suggested reviewer on a second unusable reply.

Every gate of this skill that waits on the user bounds itself that way, re-prompting at most once and then taking its own safe default, and which default is safe differs by gate, which is why they differ: here the suggestion, already shown beside the full scanned list; abort on the adversarial degradation notice of `SKILL.md`, where continuing would silently weaken a check; proceeding without chaining on the circularity nudge below, where the offer is an enrichment and declining costs nothing.
An unbounded re-prompt is the one shape none of them takes, a user who cannot phrase an answer being left with no way forward.
Once the choice is locked in, carry the chosen reviewer's `category` forward: it gates calibration injection (see "Inject calibration and launch").

## Circularity check (blindspot suggestion)

Before doing any heavy work (memory loading, calibration, reviewer launch), check whether the upcoming review is structurally circular: Claude reviewing a Claude-authored artifact in the same skill family.
If so, suggest chaining via `/audit:blindspot` instead of running the reviewer directly.

**Suggest blindspot for high-signal circularity (artifact-driven, reviewer-agnostic):**

The trigger is the **nature of the artifact**, not the chosen reviewer.
A `SKILL.md` reviewed by `posit-dev:critical-code-reviewer` is just as circular as one reviewed by `audit:skill-adversary`: Claude's distributional priors apply regardless of which reviewer formats the critique.

Match any of:

- target filename is `SKILL.md`, or the target directory contains one at top level (reason: "target is a SKILL.md; Claude interprets its content at runtime"), OR
- target is a `*.md` file under any `agents/` directory at any depth (reason: "target is a Claude Code agent definition; Claude interprets its content at runtime"), OR
- target's resolved absolute path is inside `~/.claude/` or any plugin install directory: cache (`~/.claude/plugins/cache/...`) or marketplace install (reason: "target is inside Claude's skill/plugin ecosystem"), OR
- target declares MCP tool definitions Claude reads at runtime: tool name + description schemas, typically in `tools/*.md`, `tools.json`, or an MCP server's tool registration code (reason: "target defines MCP tool descriptions Claude interprets at runtime").

If none of these apply, skip this section silently and proceed to "Detect deployment context".

If a high-signal case matches, test the OpenRouter key first, as blindspot itself does before its own Phase 1, and present the matching nudge (one prompt, then wait for response):

```bash
test -n "$OPENROUTER_API_KEY" && echo "openrouter:available" || echo "openrouter:missing"
```

On `openrouter:available`:

```
Circularity detected — <reason in one line>.
blindspot can route a parallel cross-model audit (via OpenRouter) and tag findings as agreed/Claude-only/external-only before the walkthrough. The walkthrough will then skip the severity trigger of L2 on agreed findings and force L2 on Claude-only ones.

Chain via /audit:blindspot first? [y/N]
```

On `openrouter:missing`, the pitch above is void and must not be made: blindspot falls back to single-model mode, whose report carries no `### Convergence Analysis`, and Step 1 of the walkthrough routes by severity alone when that section is absent.
Offer what the fallback actually delivers instead:

```
Circularity detected — <reason in one line>.
OPENROUTER_API_KEY is not set, so blindspot would run single-model: no external judge, no `### Convergence Analysis`, hence no bucket tagging and no change to L2 routing. Over running the reviewer from here, it would still add a written circularity verdict, the named bias risks, and a manual-countermeasures checklist.

Chain via /audit:blindspot anyway? [y/N]
```

**On user response:**

- **No / empty / anything other than explicit yes** → proceed to "Detect deployment context" as normal.

- **Yes** → blindspot must be invoked **by the user**, not via the Skill tool.
  blindspot's frontmatter sets `disable-model-invocation: true` (it is an explicit-invocation skill), and the Skill tool refuses to launch it with the error `Skill audit:blindspot cannot be used with Skill tool due to disable-model-invocation`.
  Instead, print the following message to the user and end the orchestrator cleanly:

  ```
  Run this command yourself in the prompt:

    /audit:blindspot <target> --reviewer <reviewer>

  When blindspot's report is in the conversation, relaunch `/audit:walkthrough` with no arguments; the walkthrough detects the report either way. With OPENROUTER_API_KEY set, that report carries a `### Convergence Analysis` section, and the walkthrough tags findings by bucket (agreed / claude-only / external-only) and routes L2 accordingly (severity trigger skipped on agreed, forced on claude-only). Without the key, it carries no such section and the walkthrough routes by severity alone.
  ```

  Do not emit the structured block in this branch: the walkthrough has not run.
  The user re-enters via `/audit:walkthrough` (walkthrough-only mode) after blindspot completes; Step 1 of the parent skill detects the convergence section and proceeds.

Key absence never pre-empts the suggestion, the fallback keeping a value of its own, but it does change what the suggestion may claim: deferring that disclosure to blindspot would reach the user only after they had typed the command and paid the round trip on a benefit already void.

## Detect deployment context

Determine the deployment context to calibrate review severity.
This procedure is shared: the walkthrough skill's Step 1b invokes the same steps when batch triage activates in a mode that never ran this file, against the project root that mode resolved, and skips step 4 when no root resolved.
Check in order:

1. **Path heuristics** (target's resolved absolute path):
   - `~/.local/bin/`, `~/bin/`, `~/scripts/`, `~/dotfiles/`, or any path under the user's home not inside a project with CI config → `personal`
   - Project root contains `.internal` marker or a project memory tags it as internal → `internal`

2. **CI classification** (if `.github/workflows/`, `.gitlab-ci.yml`, or `Jenkinsfile` exists):

   Split CI signals into two categories:

   - **CI deploy** (triggers `production`): Dockerfile, `docker-compose.yml`, `k8s/`, `deploy/`, `terraform/`, `helm/`, `.elasticbeanstalk/`, `appspec.yml`, `fly.toml`, `render.yaml`, or workflow files whose name contains `deploy`, `release`, or `cd` (case-insensitive).
   - **CI quality-only** (triggers `internal`): everything else: test, check, lint, coverage, docs workflows (e.g. `R-CMD-check.yaml`, `pytest.yml`, `pkgdown.yaml`, `test-coverage.yaml`, `eslint.yml`).
     These indicate project hygiene, not deployment.

   If **any** CI deploy signal is found → `production`.
   If CI exists but **only** quality signals → `internal`.

3. **Memory check**: look for `project_deployment_context.md` memory file.
   If found, use it.

4. **Fallback**: ask the user: "Is this personal tooling, internal team tooling, or production code?"
   Persist the answer in a `project_deployment_context.md` memory file.

## Load target project memories

The walkthrough skill runs from its own working directory, not from the target project.
This means Claude Code's automatic project memory loading does **not** include the target's memories.
You must load them explicitly.
This procedure is shared: walkthrough-only mode invokes the same steps once it has resolved a project root (see the walkthrough skill's Step 2).

1. Resolve the target's **project root**.
   Claude Code keys auto memory by repository, so every worktree and subdirectory of one repository shares a single memory directory: run `git -C <dir> rev-parse --path-format=absolute --git-common-dir`, and take the parent directory of its output.
   `<dir>` is the target when it is a directory, and its parent directory when it is a file (`git -C` refuses a file).
   A glob is neither, and its parent directory is not one either: `dirname` on `audit/**/*.py` yields `audit/**`, which no directory answers, and the command exits `fatal: cannot change to 'audit/**'` (measured 2026-09-20).
   For a glob, `<dir>` is instead its longest leading run of path segments carrying no `*`, `?` or `[`, so `audit/walkthrough/**/*.py` resolves on `audit/walkthrough` and `audit/**/agents/*.md` on `audit`; a pattern whose first segment already carries one, such as `*.md`, leaves that run empty and resolves on the working directory.
   Outside a git repository, walk upward from that same `<dir>` to the first ancestor containing `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, or `DESCRIPTION`, never above `$HOME`; failing that, use `<dir>` itself.

2. List the **candidate memory dirs** in this order:

   - **`autoMemoryDirectory`**, the Claude Code setting that relocates auto memory.
     Read it from managed settings (`managed-settings.json` in the managed policy directory, `/etc/claude-code/` on Linux), then `<project root>/.claude/settings.local.json`, `<project root>/.claude/settings.json` and `~/.claude/settings.json`; the first file that sets it wins.
     Expand a leading `~/`, and ignore a value that is neither absolute nor `~/`-prefixed.
   - **The harness memory dir** `~/.claude/projects/<encoded>/memory/`, where `<encoded>` is the project root's absolute path with every character other than an ASCII letter, digit or `-` replaced by `-` (e.g., `/home/<user>/.config/my-pkg` → `-home-<user>--config-my-pkg`).
     If its `MEMORY.md` is a redirect stub, it carries a line pointing at a canonical store kept elsewhere, labelled either `Canonical index: <path>` or `Canonical location: <path>` (match either label, case-insensitive).
     Extract `<path>`, stripping surrounding backticks and whitespace and any trailing punctuation, and expanding a leading `~` to the home directory; resolve it and use its containing directory as this candidate instead of the harness dir.
   - **`~/.claude/memory/`**, a convention for users who keep one canonical memory store outside the per-project directories (for instance injected by a `SessionStart` hook) rather than through `autoMemoryDirectory`.

3. The **memory dir** is the first candidate holding at least one file matching `feedback_review_severity*.md`; when none does, it is the first candidate that exists.
   The walkthrough's Step 4b writes new calibration rules to this directory, never to the project store below.

4. Collect the files matching `feedback_review_severity*.md` (the suffix varies by scope, e.g. `feedback_review_severity.md`, `feedback_review_severity_personal.md`) in the memory dir, and also in the **project store** `<project root>/.claude/memory/` when it exists and is not the memory dir itself.
   A project keeps the files Claude reads under `.claude/`, so its rules add to those of the memory dir instead of replacing them.
   These hold reviewer calibration rules from prior sessions (dismissed false positives, R idioms not to flag, etc.).
   If neither directory holds any, the consumer runs without prior calibration context: skip the remaining steps.

   **Scope filter.** A shared store holds calibration for many projects, so read the frontmatter (`name`, `description`) of each file first and read the body only of the files kept.
   Keep a file when at least one holds:

   - it comes from the project store, which is already scoped to this project;
   - its description names the target's project, by repository or package name or by a path containing the target;
   - its description names a kind of artifact present in the target (e.g. bats test files, `SKILL.md`, `.claude/rules/`, French `.qmd` reports, heuristic parsers), where a directory target covers the files it contains;
   - its description names neither a project nor a kind of artifact, which makes it generic (e.g. calibration for personal packages).

   Skip a file whose description names a different project, even when its artifact kind matches.
   Match a project name as a whole name, never as a substring: `hebstr` does not select `quarto-hebstr-doc`.
   When the description leaves relevance uncertain, keep the file: a wrongly skipped rule gets re-litigated, a wrongly kept one only costs context.
   Record the kept and skipped files for step 6.

5. Scan the `MEMORY.md` of the memory dir and of the project store for other feedback-type memories relevant to the review (e.g., `feedback_code_text_english.md`).
   Read any that seem review-relevant.

6. Collect all loaded memory content into a `[prior calibration]` block, and report the load on one line, naming files by their suffix after `feedback_review_severity_` (`default` for the bare file):
   `<memory dir>[ + <project store>] (kept K/N: <names>; skipped: <names>)`, or `none (<reason>)`.
   Skipped files are named rather than counted so that a wrong exclusion is visible.

## Inject calibration and launch

Context injection applies **only** when the chosen reviewer's `category` from the runtime scan is `code`.
For `skill-tool` and `unknown`, no calibration is injected: launch with the original prompt.
The `unknown` category is treated fail-safe: a reviewer that receives calibration it doesn't understand is more dangerous than one running uncalibrated.

When injection applies:
- **personal**: read `templates/calibration-personal.md` and prepend it to the reviewer prompt
- **internal**: read `templates/calibration-internal.md` and prepend it
- **production**: no calibration block, full adversarial severity

**Prior calibration** (from target project memories) is injected for **all** code reviewers, regardless of deployment context.
It supplements the context-based calibration, not replaces it.
Append it after the context calibration block (or as the only calibration if context is production).

**Launch the reviewer as an Agent** (not a Skill).
This is critical: running the reviewer in the same context window as the walkthrough exhausts the context budget and causes the walkthrough to silently abort.
The Agent isolates the reviewer's work (file reads, sub-agents, bash commands) and returns only the final report.

Build the Agent prompt as follows:

```
[context calibration block, if applicable]

[prior calibration block, if found — prefix with "Prior review calibration for this project (from previous sessions):"]

You are running the <reviewer> skill. Review: <target>

IMPORTANT — output format: return ONLY the structured findings report. Do not include your intermediate reasoning, file contents you read, or tool call results. Each finding must include: severity tier, file(s) and line(s), description, and suggested fix. Keep each finding to one short paragraph. Maximum 25 findings — if more exist, keep the 25 highest-severity ones and note how many were omitted. Do NOT report findings that contradict the prior calibration rules above — those patterns have been explicitly validated by the project author. That exemption stops at security, data integrity, correctness and privacy: report a finding in one of those four categories even when a calibration rule appears to cover it, naming the rule you considered, and let the walkthrough adjudicate it.
```

The four categories are the ones Step 4b of `SKILL.md` refuses to write a calibration rule for, and Step 2b refuses to reject a finding on.
This line is the same rule at the upstream end: a rule suppressing a finding here leaves no verdict, no cross-model check and no line the user can read, where a rejection downstream at least leaves all three.

Launch with `Agent(prompt, description="review <target>")`.
The walkthrough cannot proceed without the report, and in an interactive session the call returns before the review is done, because Claude Code runs every Agent in the background.
Tell the user in one line that the review of `<target>` is running and end the turn there; the completion notification resumes the walkthrough, and "Output" below runs once the report has arrived.
Waiting is that, and nothing else: do not poll with `TaskOutput`, do not ask the user anything, and never write the report block yourself instead of yielding.
Ending the turn is not ending the walkthrough: the notification brings it back, and abandoning it mid-review is what this forbids.
The report is the result that notification carries.
If the Agent ran in the foreground instead (the report is already the tool result), continue the same way.

For skill/tool reviewers (no calibration):

```
You are running the <reviewer> skill. Review: <target>

[same output format instructions as above]
```

A reviewer agent that fails and one that returns an empty result are two different outcomes and take two different answers.

**Failed**, meaning crashed, timed out, was interrupted, or returned output no findings report can be read from: nothing reached the conversation, so tell the user and offer a retry at a narrower scope, a single file instead of a directory, or a glob restricted to the changed files.
Do not offer walkthrough-only mode here: it scans the conversation for a report, and this run left none, which is SKILL.md's Recovery case 1.

**Empty**, meaning the reviewer ran to completion and reported zero findings: that is a report, not a failure.
Emit the block below and continue; Step 1 reads it, finds no findings and runs its own zero-findings branch, which offers the user an independent check.
Nothing is retried and nothing falls back.

## Output

Once the reviewer's report has arrived, emit the following structured block **exactly**: it carries the values Step 1 and Step 1b read by name, and it marks the handoff that keeps the skill from ending on the review.

```
--- ORCHESTRATOR COMPLETE ---
context: <level> (<detection method>)
reviewer: <reviewer name>
calibrated: <yes|no>
prior calibration: <the step 6 line of "Load target project memories">
batch: <--batch|--no-batch|none>
--- PROCEED TO STEP 1 ---
```

Do not copy the reviewer's report after the block.
It reached this context when the Agent completed, and this file runs in the walkthrough's own context rather than across a boundary, so a second copy of a report capped at 25 findings duplicates the largest thing in the transcript to tell Step 1 what it can already read where it is.

After emitting the block, do not end your turn and do not add commentary, a summary of the review, or follow-up questions: this file runs inside the walkthrough skill, so continue directly with its Step 1.
