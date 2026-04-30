---
name: sweep
description: >
  Full-coverage project review: detects project type and size, spawns specialist background agents with disjoint scopes, consolidates all findings into one deduplicated report sorted by severity, then offers interactive walkthrough.
  Intent: the user wants a comprehensive, multi-facet review of an entire project — not a single file, not a PR diff, not a non-code document.
  Trigger on: "full review", "review complète", "revue complète", "full audit", "audit complet", "lance la review complète", "/sweep",
  "review this project", "audit this repo", "go through everything", "check the whole project", "thorough review",
  "passage complet sur le projet", "tout checker", "état des lieux du projet", "diagnostic complet",
  or any request that asks for a multi-angle assessment of an entire codebase covering architecture, quality, tests, and/or docs.
  EXCLUSIONS OVERRIDE TRIGGERS — do NOT trigger on: single-file reviews (even if phrased as "full review of this file"), PR reviews or diffs, non-code document reviews (papers, resumes, CVs), CI/build commands ("lance tout" meaning "run tests + build"), or when the user explicitly asks for only /walkthrough.
---

# Full Review

Orchestrates a comprehensive, multi-angle review of a project by spawning specialist agents with disjoint scopes, then consolidating everything into a single actionable report.

**This skill must be executed by the main model, not delegated to a subagent.**

## Invocation

```
/sweep [path]
```

`[path]` is optional — defaults to the current working directory.

## Workflow

### Phase 0 — Detect project type and size

Scan the target directory to determine the project type and size.

#### Project type signals

| Signal | Project type |
|--------|-------------|
| `DESCRIPTION` + `NAMESPACE` + `R/` | R package |
| `pyproject.toml` or `setup.py` or `setup.cfg` | Python package |
| `_quarto.yml`, or `index.qmd`, or >= 3 `*.qmd` files | Quarto project |
| `package.json` | Node/JS project |
| `Cargo.toml` | Rust project |
| `go.mod` | Go project |
| `_typst.yml` or `*.typ` (multiple) | Typst project |
| None of the above | Generic (fallback) |

If ambiguous (e.g., R package with Quarto vignettes), pick the **primary** type based on what contains the most code. For monorepos or multi-language projects, note the secondary types in the Phase 0 report — Agent D covers the primary type only; mention uncovered types as a coverage gap in the final report.

If the target directory does not exist or contains zero source files, report this to the user and stop. Do not launch agents.

#### Project size (LOC)

Count lines of code in source files (exclude vendored dependencies, lock files, and generated files). Use a quick heuristic:

```bash
find <path> -type f \( -name '*.R' -o -name '*.Rmd' -o -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.vue' -o -name '*.rs' -o -name '*.go' -o -name '*.qmd' -o -name '*.typ' \) ! -path '*/node_modules/*' ! -path '*/renv/*' ! -path '*/venv/*' ! -path '*/.venv/*' ! -path '*/vendor/*' | xargs wc -l 2>/dev/null | tail -1
```

Classify:
- **Small**: < 1500 LOC
- **Medium**: 1500–5000 LOC
- **Large**: > 5000 LOC

#### Calibration memory (optional)

Search for a `feedback_review_severity.md` file in the current project's memory directory (the `~/.claude/projects/<current-project-hash>/memory/` that corresponds to the working directory). If found, read its content — it contains calibration rules for known false positive patterns (e.g., R idioms not to flag). This content will be injected into every agent prompt as "Known false positive patterns — do not flag these".

#### Report to user

Report the detected type, size category, LOC count, number of agents to launch, whether calibration memory was found, and which skill dependencies are available (check the skill list). Always check `/critical-code-reviewer` (Agent A) and `/walkthrough` (Phase 4). For R package projects, also check `/testing-r-packages`, `/r-package-development` (Agent C), and `/cran-extrachecks` (Agent D). Report availability of each before proceeding.

### Phase 1 — Launch agents

Launch **all agents in a single message**, all in **background mode**.

#### Agent roster

All projects get agents from the following roster. Each agent has a **disjoint scope** — no overlap between agents.

**Agent A — Code Correctness** (subagent_type: `general-purpose`)
This agent must first attempt to invoke the `/critical-code-reviewer` skill via the `Skill` tool. If the skill is not available (not installed or invocation fails), fall back to performing the review itself using the scope below.
Scope: bugs, edge cases, error handling, security issues, data handling correctness, regex validity, type mismatches.
Exclude: naming conventions, project structure, documentation, test quality, packaging/compliance.
Severity mapping: if `/critical-code-reviewer` is used, map its 4 tiers to the 3-tier system — merge "Strong Suggestions" and "Noted" into "Suggestion".
Confidence rule: only report findings you are confident are real issues. If you start analyzing a potential issue and realize it is not a bug or is handled correctly, drop it — do not include withdrawn or uncertain findings in your output.

**Agent B — Architecture & Structure** (subagent_type: `Explore`)
Scope: project layout, file organization, dependency management, configuration coherence, naming conventions, API surface consistency.
Exclude: individual code correctness, bugs, test content, test coverage, documentation prose, documentation coverage, content completeness, placeholder detection, packaging/compliance. **Strict boundary**: if a finding is about whether tests exist, whether docs are complete, whether content is placeholder/missing, or what tests/docs contain, it belongs to Agent C — do not report it.
**Scope enforcement**: before including a finding, check: does this describe a bug, edge case, or incorrect behavior? If yes, drop it (Agent A). Does this describe test quality, test coverage, or documentation? If yes, drop it (Agent C). Only report findings about project layout, file organization, dependency management, config coherence, naming, and API surface.

**Agent C — Documentation & Tests** (subagent_type: `general-purpose`)
For R package projects: this agent must first invoke the `/testing-r-packages` skill via the `Skill` tool to review test quality, then invoke the `/r-package-development` skill via the `Skill` tool to check roxygen2 documentation conventions and devtools workflow compliance, then continue with its full scope below. If either skill is not available, fall back to reviewing the corresponding facet using the scope below only.
Scope: documentation coverage and quality, test coverage and quality, README/vignettes, examples, reproducibility (renv, lock files, CI).
Exclude: code correctness, architecture decisions, naming conventions, packaging/compliance.

**Agent D — Packaging & Compliance** (subagent_type: varies by project type)
This agent adapts to the project type:

| Project type | Skill / focus | Agent type |
|-------------|--------------|------------|
| R package | `/cran-extrachecks` — CRAN submission readiness | `general-purpose` |
| Python package | pyproject.toml correctness, packaging best practices, typing/linting config | `general-purpose` |
| Rust | Cargo.toml, clippy-level checks, edition compliance | `general-purpose` |
| Node/JS | package.json, bundler config, ESLint/Prettier coherence | `general-purpose` |
| Quarto / Typst | `_quarto.yml` / `_typst.yml` config, output format coherence, extension usage. **Also check configs in individual `.qmd` files** (listing options, feed, navbar, sidebar) — not just top-level YAML. | `general-purpose` |
| Go | go.mod, module hygiene, vet/staticcheck-level checks | `general-purpose` |
| Generic | Skip this agent entirely | — |

When the "Skill / focus" column references a skill name (prefixed with `/`), the agent prompt must explicitly instruct the agent to invoke that skill via the `Skill` tool. If the skill is not available (not installed or invocation fails), the agent must fall back to performing the review itself using the focus areas described in the column (e.g., for R packages: CRAN submission readiness checks without `/cran-extrachecks`). For all other rows, the column describes the focus areas to include directly in the agent prompt.

#### Scaling by project size

| Size | Agents launched | Adaptation |
|------|----------------|------------|
| **Small** (< 1500 LOC) | 2–3 | Merge Agent C into Agent B: add C's scope items to B's scope and remove them from B's exclusions. Also carry over Agent C's skill invocations (e.g., `/testing-r-packages` and `/r-package-development` for R packages) into Agent B's prompt. Skip Agent D unless project-type-specific compliance is critical (e.g., R → CRAN). |
| **Medium** (1500–5000 LOC) | 3–4 | All 4 agents, but skip Agent D for Generic projects. |
| **Large** (> 5000 LOC) | 4 | All 4 agents. |

#### Agent prompt requirements

Each agent prompt must include:
- The project path
- Its specific **scope** (what to look at) and **exclusions** (what to ignore)
- Calibration memory content if found in Phase 0 (as "Known false positive patterns — do not flag these: ...")
- Instruction to output findings as a numbered list with: file path, line number, description, suggested fix, severity (Blocking / Required / Suggestion). For project-wide findings with no specific file, use "Project-wide" as file path and omit line number.
- Instruction to be specific and actionable — no vague "could be improved" without saying how
- Instruction: "Only report findings you are confident about. If you investigate a potential issue and determine it is not a real problem, discard it silently — do not include it in your output."
- A cap of **7 findings maximum** — prioritize Blocking and Required over Suggestions. The cap is a prompt instruction; if an agent exceeds it, keep all returned findings during consolidation.

### Phase 1b — Wait for agents

After launching all agents in background, **wait for their completion notifications**. Do not poll with TaskOutput — the system notifies you automatically when each agent completes. While waiting, do not perform other work. When all agents have completed (or failed/timed out), move to Phase 2.

### Phase 2 — Consolidate

**This phase is a lightweight merge, not a deep re-evaluation.** Do not verify individual findings (no Bash commands, no file reads beyond what agents already reported). Finding verification happens later in the walkthrough (Step 2b). The only exception: if a finding contains an obvious factual error visible from the agent's own output (e.g., agent says "file X doesn't exist" but another agent read that file), flag it as dubious.

Steps:

1. Collect findings from each agent's output.
2. **Deduplicate**: if the same issue (same file + same problem) appears in multiple reports, keep the most detailed version. When merging a duplicate, note which agents independently flagged it — convergence from agents with disjoint scopes is a strong signal.
3. **Scope filter**: for each Agent B finding, verify it falls within Agent B's scope. If it overlaps with Agent A's scope (bugs, correctness, security) or Agent C's scope (tests, docs), drop it. If the same issue was also reported by Agent A or Agent C, keep their version.
4. **Merge** into a single numbered list sorted by severity:
   - **Blocking** first
   - **Required** next
   - **Suggestion** last
5. Within each tier, group by file or topic.

### Phase 3 — Report

Display the consolidated report using this **exact template** — follow the format strictly, do not restructure it as prose or free-form markdown:

```
## Full Review Report — [project name] ([project type], [LOC] LOC)

**Agents:** Agent A (correctness via critical-code-reviewer) ✓ · Agent B (architecture) ✓ · Agent C (docs/tests) ✓ · Agent D (cran-extrachecks) ✓
**Calibration:** [loaded N rules / none found]
**Summary:** X blocking · Y required · Z suggestions (from N agents, M duplicates removed)

### Blocking

1. **[file:line]** — Description of the issue.
   → Suggested fix.
   _Flagged by: Agent A_

### Required

...

### Suggestions

...

---
Run `/walkthrough` to process these findings one by one interactively.
```

**Mandatory elements:**
- The **Agents** line with status markers (✓ completed, ✗ failed, ⏱ timed out)
- The detected **project type** and **LOC** in the header
- The **Calibration** line (whether memory was loaded or not)
- **Duplicate count** in the summary line
- The `---` separator and `/walkthrough` footer
- If an agent failed or timed out, note the coverage gap at the bottom
- If Agent A used the inline fallback instead of `/critical-code-reviewer`, show `Agent A (correctness, inline fallback)` instead of `Agent A (correctness via critical-code-reviewer)` in the Agents line
- For R package projects, Agent C must report which R-specific skills were successfully invoked: `Agent C (docs/tests via testing-r-packages + r-package-development)` when both worked, `Agent C (docs/tests via testing-r-packages)` or `Agent C (docs/tests via r-package-development)` when only one was available, or `Agent C (docs/tests, no r-lib skills)` when neither was available. For non-R projects, always show `Agent C (docs/tests)`.
- When Agent D invokes a skill (e.g., `/cran-extrachecks`), show the skill name: `Agent D (cran-extrachecks) ✓`. If the skill was unavailable and the agent fell back to inline review, show `Agent D ([focus], inline fallback)` (e.g., `Agent D (CRAN readiness, inline fallback)`). For project types where Agent D uses no skill, show the focus directly: `Agent D (pyproject.toml) ✓`.

### Phase 4 — Offer walkthrough

After presenting the report, ask the user if they want to run `/walkthrough`. Do not auto-trigger it.

If the user accepts, invoke the walkthrough skill. After the walkthrough completes and fixes have been applied, run the project's test suite automatically (do not ask). Truncate test output to the summary line (pass/fail count) — only display full output if tests fail. For R packages: run `devtools::document()` before `devtools::test()`. If no test suite is detected, skip this step and note "No test suite detected — skipping post-walkthrough verification."

## Important constraints

- **Max 4 agents total.** Scale down for small projects (see scaling table). Do not exceed 4.
- **All agents run in background mode.**
- **Read-only review.** No agent modifies any files. Modifications happen only during the walkthrough phase.
- **Disjoint scopes.** Each agent's scope and exclusions are explicitly defined. No two agents evaluate the same facet.
- **Adapt, don't force.** If the project has no tests, no docs, or no CI — adapt the agent prompts accordingly. Do not report absence of optional infrastructure as a finding unless it materially affects the project.
- **Report in conversation.** No file output unless the user asks to save it.
