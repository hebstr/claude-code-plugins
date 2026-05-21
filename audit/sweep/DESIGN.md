# sweep: Design Notes

## Design decisions

### Disjoint scopes with cross-exclusions
Each agent has explicit Scope and Exclude lists. No two agents evaluate the same facet. Convergence (two agents flagging the same issue despite disjoint scopes) is a strong signal, not an artifact of overlapping instructions. Agent B (Explore/haiku) is the one most prone to scope creep into docs/tests territory; the current triple-layer defense (exclusion list + strict boundary + scope enforcement checklist) keeps it in line.

### Calibration memory injection
Phase 0 searches for `feedback_review_severity.md` in the project memory directory. If found, its rules are injected into every agent prompt. This prevents agents from re-flagging known false positives (e.g., R idioms: lazy eval, copy-on-modify, NAMESPACE imports, Suggests-guarded packages).

### Skill fallback and transparency chain
Every agent that invokes an external skill (A → `/critical-code-reviewer`, C → `/testing-r-packages` + `/r-package-development`, D → `/cran-extrachecks`) follows a three-layer contract: (1) instruction-level fallback if the skill is absent, (2) Phase 0 reports skill availability before launch, (3) Phase 3 Agents line shows exactly which skills were used vs inline fallback.

### LOC-based scaling
Agent count adapts to project size. Small projects (< 1500 LOC) get 2–3 agents by merging docs/tests into architecture. When merging C into B, skill invocations (e.g., R-specific skills) carry over into B's prompt. The packaging agent (D) is only added when project-type-specific compliance matters.

### Ouroboros integration (in walkthrough)
`ouroboros_evaluate` must receive actual code (git diff) or file content as artifact, not a prose summary. Prose summaries produce misleading scores. walkthrough SKILL.md enforces this with explicit fallback flagging.

## Related files

- `${CLAUDE_PLUGIN_ROOT}/audit/walkthrough/SKILL.md`: interactive walkthrough invoked after consolidation
- `${CLAUDE_PLUGIN_ROOT}/audit/blindspot/SKILL.md`: circularity-aware orchestrator that wraps sweep
- `~/.claude/memory/feedback_review_workflow.md`: global feedback memory describing this workflow preference
- `~/.claude/projects/<project-hash>/memory/feedback_review_severity.md`: project-specific calibration rules

## Backlog

- [ ] Consider adding focus modes (security, performance, CRAN) as an optional parameter
- [ ] Enrich Agent D templates for Rust (clippy), Go (vet/staticcheck) after real-world testing
- [ ] Consider content-readiness pre-check for Quarto/content projects under construction (high DEFERRED ratio pattern)
- [ ] Add Shiny app detection (`app.R` or `ui.R` + `server.R`) as a distinct project type with Agent D focus on structure/config/deploy
