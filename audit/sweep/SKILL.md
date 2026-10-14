---
name: sweep
disable-model-invocation: true
allowed-tools: Read Glob Grep Bash Agent Skill
description: >
  User-invocable ONLY via `/audit:sweep`.
  Does not auto-trigger on mentions of "full review", "audit complet", "review complète", "review this project", "audit this repo", "thorough review", "diagnostic complet", "état des lieux du projet", or any phrasing requesting a multi-angle project assessment.
  Full project review: detects project type and size, spawns specialist background agents with disjoint scopes (architecture, quality, tests, docs), consolidates findings into one deduplicated report sorted by severity, then offers an interactive walkthrough.
  Not for: single-file reviews, PR or diff reviews, or non-code document reviews (papers, resumes, CVs).
---

# Full Review

Orchestrates a comprehensive, multi-angle review of a project by spawning specialist agents with disjoint scopes, then consolidating everything into a single actionable report.

**This skill must be executed by the main model, not delegated to a subagent.**
One exception, by design: `audit:blindspot` spawns its reviewer as an `Agent`, so a sweep run as its reviewer runs inside a subagent.
In that run, skip the Phase 0 circularity check, blindspot having already made and recorded that assessment, which leaves one point waiting on the user: Phase 4 prints its message instead of asking, `AskUserQuestion` being withheld from every subagent.
`audit/blindspot/SKILL.md` owns the rest of that nesting; this clause states only what changes inside the sweep.

## Invocation

```
/audit:sweep [path]
```

`[path]` is optional; defaults to the current working directory.

## Workflow

### Phase 0: Detect project type and size

Resolve the argument once, here: **`<target>`** is `[path]` when the invocation carried one, and the current working directory otherwise.
Every later mention of the target in this skill means that resolved path: the `find` command below, the two delegated procedures, and the `[path]` printed in the Phase 4 message.

Scan `<target>` to determine the project type and size.

#### Project type signals

  | Signal                                               | Project type       |
  | ---------------------------------------------------- | ------------------ |
  | `DESCRIPTION` + `NAMESPACE` + `R/`                   | R package          |
  | `pyproject.toml` or `setup.py` or `setup.cfg`        | Python package     |
  | `_quarto.yml`, or `index.qmd`, or >= 3 `*.qmd` files | Quarto project     |
  | `package.json`                                       | Node/JS project    |
  | `Cargo.toml`                                         | Rust project       |
  | `go.mod`                                             | Go project         |
  | `_typst.yml` or `*.typ` (multiple)                   | Typst project      |
  | None of the above                                    | Generic (fallback) |

If ambiguous (e.g., R package with Quarto vignettes), pick the **primary** type based on what contains the most code.
For monorepos or multi-language projects, note the secondary types in the Phase 0 report; Agent D covers the primary type only; mention uncovered types as a coverage gap in the final report.

If the target directory does not exist, or holds no files at all, report this to the user and stop.
Do not launch agents.
A zero LOC count is **not** that case: the count below is a heuristic over a fixed extension list, and a project in a language that list omits is exactly what the Generic row above is for.
Report the zero, classify the project Small, and launch.

#### Project size (LOC)

Count lines of code in source files (exclude vendored dependencies, lock files, and generated files).
Use a quick heuristic:

```bash
find <target> -type f \( -name '*.R' -o -name '*.Rmd' -o -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.vue' -o -name '*.rs' -o -name '*.go' -o -name '*.qmd' -o -name '*.typ' -o -name '*.sh' -o -name '*.lua' -o -name '*.sql' -o -name '*.c' -o -name '*.h' -o -name '*.cpp' -o -name '*.hpp' -o -name '*.java' -o -name '*.cs' -o -name '*.rb' -o -name '*.php' -o -name '*.swift' \) ! -path '*/node_modules/*' ! -path '*/renv/*' ! -path '*/venv/*' ! -path '*/.venv/*' ! -path '*/vendor/*' ! -path '*/.git/*' -print0 | xargs -0 cat 2>/dev/null | wc -l
```

Classify:
- **Small**: < 1500 LOC
- **Medium**: 1500 to 5000 LOC
- **Large**: > 5000 LOC

#### Circularity check (blindspot suggestion)

This subsection runs before the calibration step below, and not after it, for the reason the delegated section states in its own first sentence: the check comes before any heavy work, memory loading and calibration included.

Run the **Circularity check (blindspot suggestion)** section of the sibling `walkthrough` skill (`../walkthrough/agents/orchestrator.md` from this skill's base directory) against the resolved target, with its key test and its two nudges unchanged, and with one trigger added: a sweep target is a project root rather than a file, so a `SKILL.md` or a `.claude-plugin/marketplace.json` anywhere under it matches, where that section's own triggers reach only a target that is a `SKILL.md` or holds one at its top level.
A match inside a tree the sweep does not review does not count: the prune paths of the LOC command above (`node_modules/`, `renv/`, `venv/`, `.venv/`, `vendor/`), and any installed or cached copy of a plugin, such as one under a `plugins/cache/` directory.
Without that, a sweep of a directory holding one plugin repository among many unrelated projects fires the nudge on all of them.
It applies here for the same reason it applies there, and for one this skill adds: a sweep detects its own target and launches four agents on it, so a project that is itself a Claude-interpreted artifact (a skill or plugin repository, anything under `~/.claude/`) is reviewed by Claude's own priors four times over before the user has named any reviewer.
A sibling reviewer invoked directly, `audit:skill-adversary`, carries no such check by design: its target is one the user has just chosen.

Its response handling is translated here rather than inherited: the delegated yes-branch ends "the orchestrator", prints a `--reviewer <reviewer>` argument a sweep has no value for, and sends the user back to `/audit:walkthrough`, none of which has a referent in a sweep.

- **No, empty, or anything other than an explicit yes**: proceed to the calibration step below.
- **Yes**: launch no agent, print the message below and end the sweep cleanly.
  `audit:blindspot` sets `disable-model-invocation: true`, so the `Skill` tool refuses to launch it and the user has to type the command, exactly as Phase 4 states for `audit:walkthrough`.

```
Run this command yourself in the prompt:

  /audit:blindspot [path] --reviewer audit:sweep

It runs this same sweep under a cross-model judge, then tags every finding agreed / claude-only / external-only before any walkthrough.
```

#### Calibration memory (optional)

Run the **Load target project memories** procedure of the sibling `walkthrough` skill (`../walkthrough/agents/orchestrator.md` from this skill's base directory), down to and including its scope filter over the `feedback_review_severity*.md` files; skip its step that scans `MEMORY.md` for other review-relevant memories, and emit the one-line load status its last step defines.
Its steps are cited by what they do rather than by their number, which a refactor of that file would silently renumber.
Run it with `<target>` as the target, never the working directory: that loader resolves a project root from the target it is given, so a sweep run on another path would otherwise inject the working directory's calibration into every agent prompt as "do not flag these" and suppress findings in the project actually under review.
It resolves the memory directory from `autoMemoryDirectory`, the harness memory directory of the repository (following a redirect stub), then `~/.claude/memory/`, and reads the `feedback_review_severity*.md` there and in the project's own `.claude/memory/` that its scope filter keeps for this project; they contain calibration rules for known false positive patterns (e.g., R idioms not to flag).
This content will be injected into every agent prompt as "Known false positive patterns, do not flag these", followed by the exemption the sibling `walkthrough` orchestrator carries: the suppression stops at security, data integrity, correctness and privacy, where an agent reports the finding anyway, naming the calibration rule it considered.

#### Report to user

Report the detected type, size category, LOC count, number of agents to launch, whether calibration memory was found, and which skill dependencies are available (check the skill list).
Always check `/posit-dev:critical-code-reviewer` (Agent A).
The skill list is **not** the test for `/audit:walkthrough`: it carries `disable-model-invocation: true`, so it never appears there and its absence proves nothing.
Report it as available; the user is the one who invokes it in Phase 4.
For R package projects, also check `/r-lib:r-testthat`, `/r-lib:r-package-development` (Agent C), and `/r-lib:r-cran-extrachecks` (Agent D).
Report availability of each before proceeding.

### Phase 1: Launch agents

Launch **all agents in a single message**, all in **background mode**.

#### Agent roster

All projects get agents from the following roster.
Each agent has a **disjoint scope**: no overlap between agents.

Three facets sit on files more than one agent reads, and the overlap is arbitrated here rather than left to each agent's reading: Phase 2 step 2 reads a convergence between two agents as evidence, which an undeclared overlap would fabricate.

- **Dependency manifests** (`DESCRIPTION`, `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`): Agent B owns where dependencies are declared and whether that declaration matches the layout; Agent C owns whether the lock file pins a rebuildable state; Agent D owns the manifest's packaging correctness and its published metadata.
- **Configuration files**: Agent B owns coherence between configs; Agent D owns the correctness of the project-type config named in its own row.
- **CI**: Agent C owns whether CI reproduces the project's own checks; Agent D owns release and packaging workflows.

**Content completeness and placeholder detection are Agent C's**, documentation or not: Agent B's Strict boundary hands them over, and C's scope below names them so they are not left between the two.

**Agent A, Code Correctness** (subagent_type: `general-purpose`)
This agent must first attempt to invoke the `/posit-dev:critical-code-reviewer` skill via the `Skill` tool.
If the skill is not available (not installed or invocation fails), fall back to performing the review itself using the scope below.
Scope: bugs, edge cases, error handling, security issues, data handling correctness, regex validity, type mismatches.
Exclude: naming conventions, project structure, documentation, test quality, packaging/compliance.
Severity mapping: if `/posit-dev:critical-code-reviewer` is used, map its 4 tiers to the 3-tier system: merge "Strong Suggestions" and "Noted" into "Suggestion".
Confidence rule: only report findings you are confident are real issues.
If you start analyzing a potential issue and realize it is not a bug or is handled correctly, drop it.
Do not include withdrawn or uncertain findings in your output.

**Agent B, Architecture & Structure** (subagent_type: `Explore`)
Scope: project layout, file organization, dependency management, configuration coherence, naming conventions, API surface consistency.
Exclude: individual code correctness, bugs, test content, test coverage, documentation prose, documentation coverage, content completeness, placeholder detection, packaging/compliance.
**Strict boundary**: if a finding is about whether tests exist, whether docs are complete, whether content is placeholder/missing, or what tests/docs contain, it belongs to Agent C; do not report it.
**Scope enforcement**: before including a finding, check: does this describe a bug, edge case, or incorrect behavior?
If yes, drop it (Agent A).
Does this describe test quality, test coverage, or documentation?
If yes, drop it (Agent C).
Only report findings about project layout, file organization, dependency management, config coherence, naming, and API surface.

**Agent C, Documentation & Tests** (subagent_type: `general-purpose`)
For R package projects: this agent must first invoke the `/r-lib:r-testthat` skill via the `Skill` tool to review test quality, then invoke the `/r-lib:r-package-development` skill via the `Skill` tool to check roxygen2 documentation conventions and devtools workflow compliance, then continue with its full scope below.
If either skill is not available, fall back to reviewing the corresponding facet using the scope below only.
Scope: documentation coverage and quality, test coverage and quality, README/vignettes, examples, content completeness and placeholder detection (documentation or not), reproducibility (lock file currency, CI reproducing the project's own checks).
Exclude: code correctness, architecture decisions, naming conventions, packaging/compliance.

**Agent D, Packaging & Compliance** (subagent_type: varies by project type)
This agent adapts to the project type:

  | Project type   | Skill / focus                                                                                                                                                                                                  | Agent type        |
  | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------           | ----------------- |
  | R package      | `/r-lib:r-cran-extrachecks` — CRAN submission readiness                                                                                                                                                        | `general-purpose` |
  | Python package | pyproject.toml correctness, packaging best practices, typing/linting config                                                                                                                                    | `general-purpose` |
  | Rust           | Cargo.toml, clippy-level checks, edition compliance                                                                                                                                                            | `general-purpose` |
  | Node/JS        | package.json, bundler config, ESLint/Prettier coherence                                                                                                                                                        | `general-purpose` |
  | Quarto         | `_quarto.yml` config, output format coherence, extension usage. **Also the per-document YAML of every `.qmd` found under `<target>`** (listing options, feed, navbar, sidebar), not just the top-level file.   | `general-purpose` |
  | Typst          | `_typst.yml` config, output format coherence, template and package usage.                                                                                                                                      | `general-purpose` |
  | Go             | go.mod, module hygiene, vet/staticcheck-level checks                                                                                                                                                           | `general-purpose` |
  | Generic        | Skip this agent entirely                                                                                                                                                                                       | —                 |

When the "Skill / focus" column references a skill name (prefixed with `/`), the agent prompt must explicitly instruct the agent to invoke that skill via the `Skill` tool.
If the skill is not available (not installed or invocation fails), the agent must fall back to performing the review itself using the focus areas described in the column (e.g., for R packages: CRAN submission readiness checks without `/r-lib:r-cran-extrachecks`).
For all other rows, the column describes the focus areas to include directly in the agent prompt.

#### Scaling by project size

  | Size                       | Agents launched | Adaptation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
  | -------------------------- | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
  | **Small** (< 1500 LOC)     | 2–3             | Merge Agent C into Agent B: add C's scope items to B's scope, remove them from B's exclusions, and drop B's **Strict boundary** and **Scope enforcement** paragraphs for that run, both of which name the merged facet as someone else's. Also carry over Agent C's skill invocations (e.g., `/r-lib:r-testthat` and `/r-lib:r-package-development` for R packages) into Agent B's prompt, and **launch the merged agent as `general-purpose` rather than `Explore`**: the merged facet needs whole-file reading and a `Skill` invocation, which the `Explore` type is not for. Skip Agent D unless the project is about to face an external compliance gate (e.g., R → CRAN), which is what makes the third agent worth its cost on a project this size.                                                                                                                                           |
  | **Medium** (1500–5000 LOC) | 3–4             | All 4 agents, but skip Agent D for Generic projects.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
  | **Large** (> 5000 LOC)     | 3–4             | All 4 agents, but skip Agent D for Generic projects, as at Medium: the Agent D table skips Generic at every size, so a flat 4 here would contradict it.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |

#### Agent prompt requirements

Each agent prompt must include:
- The project path
- Its specific **scope** (what to look at) and **exclusions** (what to ignore)
- Calibration memory content if found in Phase 0 (as "Known false positive patterns, do not flag these: ..."), closed by its exemption: "That exemption stops at security, data integrity, correctness and privacy: report a finding in one of those four categories even when a calibration rule appears to cover it, naming the rule you considered."
- Instruction to output findings as a numbered list with: file path, line number, description, suggested fix, severity (Blocking / Required / Suggestion).
For project-wide findings with no specific file, use "Project-wide" as file path and omit line number.
- Instruction to be specific and actionable: no vague "could be improved" without saying how
- Instruction: "Only report findings you are confident about.
If you investigate a potential issue and determine it is not a real problem, discard it silently.
Do not include it in your output."
- A cap of **7 findings maximum**, which **Blocking and Required findings are exempt from**: report every one of those, and let them push the total past 7 when there are more.
The cap bites on Suggestions alone, and the agent states what it dropped on a final line, `N suggestions omitted for brevity.`, so the omission leaves a trace instead of none.
The cap is a prompt instruction; if an agent exceeds it, keep all returned findings during consolidation.

### Phase 1b: Wait for agents

After launching all agents in background, **wait for their completion notifications**.
Do not poll with TaskOutput; the system notifies you automatically when each agent completes.
While waiting, do not perform other work.
When all agents have completed (or failed/timed out), move to Phase 2.

### Phase 2: Consolidate

**This phase is a lightweight merge, not a deep re-evaluation.** Do not verify individual findings (no Bash commands, no file reads beyond what agents already reported).
Finding verification happens later in the walkthrough (Step 2b).
The only exception: if a finding contains an obvious factual error visible from the agent's own output (e.g., agent says "file X doesn't exist" but another agent read that file), flag it as dubious.

Steps:

1. Collect findings from each agent's output.
2. **Deduplicate**: if the same issue (same file + same problem) appears in multiple reports, keep the most detailed version.
   When merging a duplicate, note which agents independently flagged it; convergence from agents with disjoint scopes is a strong signal.
3. **Scope filter**: for each Agent B finding, verify it falls within Agent B's scope **as this run defined it**.
   On a Small run where Agent C was merged into Agent B, Agent C's scope is Agent B's scope: test against Agent A's only.
   Against the roster's unmerged scopes this step would drop the entire facet the merge exists to preserve.
   If the finding overlaps with Agent A's scope (bugs, correctness, security), or with Agent C's scope (tests, docs) when Agent C ran as its own agent, drop it.
   If the same issue was also reported by Agent A or Agent C, keep their version **and the convergence note step 2 attached to it**: that note is the one thing the dropped copy carried, and it records two disjoint scopes reaching the same finding.
4. **Merge** into a single numbered list sorted by severity:
   - **Blocking** first
   - **Required** next
   - **Suggestion** last
5. Within each tier, group by file or topic.

### Phase 3: Report

Display the consolidated report using this **exact template**: follow the format strictly, do not restructure it as prose or free-form markdown:

```
## Full Review Report: [project name] ([project type], [LOC] LOC)

**Agents:** Agent A (correctness via critical-code-reviewer) ✓ · Agent B (architecture) ✓ · Agent C (docs/tests) ✓ · Agent D (r-cran-extrachecks) ✓
**Calibration:** <memory dir>[ + <project store>] (kept K/N: <names>; skipped: <names>)
**Summary:** X blocking · Y required · Z suggestions (from N agents, M duplicates removed, O omitted for brevity)

### Blocking

1. **[file:line]**: Description of the issue.
   → Suggested fix.
   _Flagged by: Agent A_

### Required

...

### Suggestions

...

---
Run `/audit:walkthrough` to process these findings one by one interactively.
```

**Mandatory elements:**
- The **Agents** line with status markers (✓ completed, ✗ failed, ⏱ timed out)
- The template's four-agent line is the **format**, not a required agent count: a run that launched fewer lists only the agents that ran.
A Small merge shows `Agent B (architecture + docs/tests)` and no Agent C entry; a skipped Agent D is omitted rather than marked failed, the markers above being for an agent that was launched
- The detected **project type** and **LOC** in the header
- The **Calibration** line: the one-line load status of the shared procedure (kept and skipped files), with its optional ` + <project store>` segment when the project carries its own `.claude/memory/`; or `none (<reason>)`, where `<reason>` is one of `no identifiable project root`, `no memory directory` or `no severity file kept`
- A finding Phase 2 flagged as dubious keeps its tier and its place, carries `(dubious: <the agent output it contradicts>)` after its description, and counts in the Summary like any other: the flag qualifies the finding, it does not withdraw it
- **Duplicate count** in the summary line
- `_Flagged by:_` names **every** agent that independently flagged the finding, `_Flagged by: Agent A, Agent B_`, which is what Phase 2 step 2 records and step 3 preserves.
The template's single-agent line is the common case, not the only form
- The `---` separator and `/audit:walkthrough` footer
- If an agent failed or timed out, note the coverage gap at the bottom
- If Agent A used the inline fallback instead of `/posit-dev:critical-code-reviewer`, show `Agent A (correctness, inline fallback)` instead of `Agent A (correctness via critical-code-reviewer)` in the Agents line
- For R package projects, Agent C must report which R-specific skills were successfully invoked: `Agent C (docs/tests via r-testthat + r-package-development)` when both worked, `Agent C (docs/tests via r-testthat)` or `Agent C (docs/tests via r-package-development)` when only one was available, or `Agent C (docs/tests, no r-lib skills)` when neither was available.
For non-R projects, always show `Agent C (docs/tests)`.
- When Agent D invokes a skill (e.g., `/r-lib:r-cran-extrachecks`), show the skill name: `Agent D (r-cran-extrachecks) ✓`.
If the skill was unavailable and the agent fell back to inline review, show `Agent D ([focus], inline fallback)` (e.g., `Agent D (CRAN readiness, inline fallback)`).
For project types where Agent D uses no skill, show the focus directly: `Agent D (pyproject.toml) ✓`.

### Phase 4: Offer walkthrough

After presenting the report, ask the user if they want to run `/audit:walkthrough`.
Do not auto-trigger it.

If the user accepts, the walkthrough must be invoked **by the user**, not via the `Skill` tool.
`audit:walkthrough`'s frontmatter sets `disable-model-invocation: true` (it is an explicit-invocation skill), and the `Skill` tool refuses to launch it with the error `Skill audit:walkthrough cannot be used with Skill tool due to disable-model-invocation`.
Instead, print the following message and end the sweep cleanly:

```
Run this command yourself in the prompt:

  /audit:walkthrough

The report above stays in the conversation, so walkthrough-only mode picks it up with no target.
Once its fixes are applied, verify with: <test command>
```

When the resolved target is not the current working directory, add this line to the message: `Run it from <target>: with no target of its own, the walkthrough resolves its project root by walking up from the working directory, and would write its deferred findings into the wrong repository.`
That mode takes no path argument, so telling the user where to run it is the only handle the sweep has on it.

Substitute `<test command>` with the project's own (`devtools::document()` then `devtools::test()` for an R package, `uv run pytest` for a Python project, and so on).
If no test suite is detected, replace that last line with "No test suite detected, so no post-walkthrough verification is available."
The sweep ends here: it cannot run that verification itself, because the walkthrough now happens in a turn the sweep no longer owns.

## Important constraints

- **Max 4 agents total.** Scale down for small projects (see scaling table).
  Do not exceed 4.
- **All agents run in background mode.**
- **Read-only review.** No agent modifies any files.
  Modifications happen only during the walkthrough phase.
- **Disjoint scopes.** Each agent's scope and exclusions are explicitly defined.
  No two agents evaluate the same facet; where two agents read the same file, the arbitration at the head of the agent roster says which facet is whose.
- **Adapt, don't force.** If the project has no tests, no docs, or no CI, adapt the agent prompts accordingly.
  Do not report absence of optional infrastructure as a finding unless it materially affects the project.
- **Report in conversation.** No file output unless the user asks to save it.
