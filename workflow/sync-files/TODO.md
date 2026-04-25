# TODO — sync-files

## Phase 1 — Field validation

- [ ] Test on an R package with modified files (R functions, man pages, NAMESPACE)
- [ ] Test on a Quarto project with modified .qmd files
- [ ] Test on a Python project (src + tests)
- [ ] Verify __NO_GIT__ fallback on a directory outside a git repo
- [ ] Note false positives (files flagged stale incorrectly)
- [ ] Note false negatives (dependencies missed by heuristics)
- [ ] Verify edits are truly minimal (no parasitic refactoring)

## Phase 2 — Post-field corrections

- [ ] Adjust dependency heuristics based on Phase 1 results
- [ ] Tune staleness detection (too noisy? too quiet?)
- [ ] Fix bugs encountered

## Phase 3 — Evals with skill-creator

- [ ] Formalize 2-3 realistic test cases from Phase 1 as eval JSON
- [ ] Benchmark with/without skill via /skill-creator
- [ ] Iterate on SKILL.md based on results
- [ ] Optimize description for triggering
