# sweep: Design Notes

## Design decisions

### Disjoint scopes with cross-exclusions

Each agent has explicit Scope and Exclude lists.
No two agents evaluate the same facet.
Convergence (two agents flagging the same issue despite disjoint scopes) is a strong signal, not an artifact of overlapping instructions.
That claim only holds if the overlaps are declared, so the three facets sitting on a file several agents read (dependency manifests, configuration files, CI) are arbitrated in the skill under the agent roster, and content completeness is assigned to Agent C rather than left between B's exclusion and C's silence.
Agent B (`Explore`) is the one most prone to scope creep into docs/tests territory; the current triple-layer defense (exclusion list + strict boundary + scope enforcement checklist) keeps it in line.

### Calibration memory injection

Phase 0 runs the walkthrough orchestrator's shared loader, which globs `feedback_review_severity*.md` in the first candidate memory directory holding any: `autoMemoryDirectory`, the harness memory directory of the repository (following a `Canonical index:`/`Canonical location:` redirect stub), then `~/.claude/memory/`, and adds those of the project's own `.claude/memory/`.
If found, their rules are injected into every agent prompt.
This prevents agents from re-flagging known false positives (e.g., R idioms: lazy eval, copy-on-modify, NAMESPACE imports, Suggests-guarded packages).
The injection carries the exemption the sibling `walkthrough` orchestrator carries (2026-10-10): the suppression stops at security, data integrity, correctness and privacy, where an agent reports the finding anyway and names the rule it considered, so a validated pattern cannot suppress a high-stakes finding at the source and leave no verdict behind.

### Circularity check

Phase 0 also runs the orchestrator's `Circularity check (blindspot suggestion)` section (2026-10-10), with one trigger added for a target that is a project root rather than a file: a `SKILL.md` or a `.claude-plugin/marketplace.json` anywhere under it.
It runs before the calibration step, which is the order the delegated section gives as its own reason for running first, and its response handling is translated rather than inherited: the delegated yes-branch names an orchestrator and a `--reviewer` argument a sweep has neither of, so sweep states both branches itself and sends a yes to `/audit:blindspot [path] --reviewer audit:sweep`.
A sweep detects its own target and launches four agents on it, so a project that is itself a Claude-interpreted artifact is read by Claude's own priors four times over before the user has named any reviewer.
The sibling leaf reviewer (`skill-adversary`) carries no such check by design: its target is one the user has just chosen.

### Skill fallback and transparency chain

Every agent that invokes an external skill (A → `/posit-dev:critical-code-reviewer`, C → `/r-lib:r-testthat` + `/r-lib:r-package-development`, D → `/r-lib:r-cran-extrachecks`) follows a three-layer contract: (1) instruction-level fallback if the skill is absent, (2) Phase 0 reports skill availability before launch, (3) Phase 3 Agents line shows exactly which skills were used vs inline fallback.

### LOC-based scaling

Agent count adapts to project size.
Small projects (< 1500 LOC) get 2 or 3 agents by merging docs/tests into architecture.
When merging C into B, skill invocations (e.g., R-specific skills) carry over into B's prompt, B's two scope-policing paragraphs are dropped (they name the merged facet as someone else's, and the Phase 2 scope filter is told the same), and the merged agent runs as `general-purpose`: the merged facet needs whole-file reading and a `Skill` call, which `Explore` is not for.
The packaging agent (D) is only added when project-type-specific compliance matters.

## Related files

- `../walkthrough/SKILL.md`: interactive walkthrough invoked after consolidation
- `../blindspot/SKILL.md`: circularity-aware orchestrator that wraps sweep
- Optional `feedback_review_severity*.md` in the memory directory resolved by the shared loader (`../walkthrough/agents/orchestrator.md`, "Load target project memories") for reviewer calibration rules (dismissed false positives, idioms not to flag).
  See `SKILL.md` §"Calibration memory (optional)".
  Users without these files run uncalibrated.

**Which path form.** A **reading** pointer takes the relative form used above: it resolves against the skill directory and holds in dev mode and in a non-plugin install.
`${CLAUDE_PLUGIN_ROOT}` is for a path a **shell command** needs, where the plugin loader sets the variable and `../blindspot/SKILL.md` carries the documented fallback for when it does not.
Both resolve here, the marketplace declaring each plugin's `source` as `./`, so the variable is the repository root; what separates them is that only the relative form needs no fallback.

## Backlog

- [ ] Consider adding focus modes (security, performance, CRAN) as an optional parameter
- [ ] Enrich Agent D templates for Rust (clippy), Go (vet/staticcheck) after real-world testing
- [ ] Consider content-readiness pre-check for Quarto/content projects under construction (high DEFERRED ratio pattern)
- [ ] Add Shiny app detection (`app.R` or `ui.R` + `server.R`) as a distinct project type with Agent D focus on structure/config/deploy
