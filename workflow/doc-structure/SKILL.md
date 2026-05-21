---
name: doc-structure
description: Audit and reorganize project documentation layout (CLAUDE.md for Claude rules, README.md for human docs). User-invocable ONLY via `/workflow:doc-structure [<project-path>]`; the path is optional and defaults to the current working directory. For monorepos, invoke once per sub-package path. Does not auto-trigger on mentions of CLAUDE.md, README.md, documentation, or sync. Not for code-level docstring/README drift, splitting one doc file into a `docs/` tree, or reorganizing sections within a single CLAUDE.md or README.md.
allowed-tools: Read Write Edit Grep
---

# doc-structure

Captured from the 2026-05-16 audit of `solatis/claude-config:doc-sync`. Convention refined on R packages and mixed-language analysis projects; may further evolve when exercised on Python-only or Quarto book projects.

## Workflow (5 phases, adapted from solatis doc-sync)

### 1. Discovery

Scan exactly these paths relative to the project argument; do not recurse:

- `<project>/CLAUDE.md` (legacy root location)
- `<project>/.claude/CLAUDE.md` (canonical location)
- `<project>/README.md`
- `<project>/README.Rmd` (R package source, generates `README.md`)
- `<project>/README.qmd` (Quarto source, generates `README.md`)

Match the file-name component case-insensitively (`README.md`, `Readme.md`, `readme.md` all hit).

**Generated-source resolution.** For each `.md` file found, scan its first 20 lines (or the first 20 lines after any YAML frontmatter block delimited by `---`); if an HTML comment of the form `<!-- README.md is generated from README.Rmd. Please edit that file -->` (or any `is generated from <file>` marker) is present, drop the `.md` entry from the audit set and substitute the referenced source path. Phase 2 then classifies the source only; Phase 3 edits the source and regenerates the `.md` via the project's pipeline. Common cases: R packages (`README.Rmd` → `README.md` via `devtools::build_readme()` or `rmarkdown::render()`), Quarto projects (`README.qmd` → `README.md`), templated docs (`*.in`, `*.tmpl`).

No glob, no walk, no exclusion list. Any `CLAUDE.md` or `README.md` deeper in the tree is either (a) a generated artifact (`docs/` for pkgdown, `_site/`/`_book/`/`_freeze/` for Quarto, `dist/`/`build/` for JS, `node_modules/*/README.md` for deps, vendored packages) or (b) a sub-package in a monorepo: both out of scope of a single skill invocation. For monorepos, the user invokes the skill once per sub-package path. The skill does not auto-detect monorepo structures. If a `packages/`, `apps/`, `crates/`, or similar sub-package directory sits next to the audited pair, tell the user at the end of Phase 1: "Detected likely sub-packages under `<dir>`; this run covered the root pair only. To audit a sub-package, re-invoke as `/workflow:doc-structure <project>/<sub-package>`." Never recurse into them.

Report what was found.

If both `<project>/CLAUDE.md` and `<project>/.claude/CLAUDE.md` exist, stop after Phase 1: legacy root + canonical location coexist, the user must consolidate before the audit runs.

If neither `CLAUDE.md` nor `README.md` (or its `.Rmd`/`.qmd` source) is found, stop after Phase 1 with a message and exit; there is nothing to audit. If exactly one side is missing, stop after Phase 1 and ask the user whether to create an empty stub for the missing file (do not auto-create). On confirmation, write the corresponding stub verbatim and exit, so the user can populate it before re-running. Do not synthesize content from the present file.

Stub templates:

```markdown
# CLAUDE.md

Project-specific rules for Claude. See README.md for human-facing docs.
```

```markdown
# <project-name>

Project description goes here. See CLAUDE.md for Claude-facing project rules.
```

Substitute `<project-name>` with the directory name of the project root. Write exactly these three lines (heading, blank, prose); no additional metadata.

After writing the stub, scan the present file for an `## Index` table (per Phase 4 convention). If any row points to the stubbed file's path, warn the user: "The existing index in `<present-file>` already references `<stubbed-file>`. Populate the stub before re-running so the index entry reflects real content." Do not modify the index: leave it for the next run.

### 2. Audit

For each file, classify content into:

- **HOW (operational)**: paths, Claude-facing operational commands (e.g. "to rebuild the index, run X"), naming conventions, decision log entries (e.g. "2026-04: switched from polars to duckdb for joins because Y"), "when editing X do Y". Belongs in `CLAUDE.md`. Excludes user-facing install/usage commands, which always go to README.
- **WHY (architectural)**: rationale, invariants, tradeoffs, design decisions, install/usage docs (including the commands users run to install or use the project). Belongs in `README.md`
- **Mixed / ambiguous**: flag for user judgment. Default-route these section types to Mixed so they reach the end-of-Phase-2 adjudication (where the user can drop them): license headers, changelogs, contributor lists, code of conduct, security policies, embedded YAML/JSON config blocks. Scope is **embedded sections inside the audited files only**, never pull in adjacent stand-alone files (`CHANGELOG.md`, `CODE_OF_CONDUCT.md`, `LICENSE`, etc.), which are out of scope per Phase 1. Do not silently skip embedded sections of these types, a security policy paragraph inside `README.md` may contain operational instructions for Claude that warrant migration

**Dual-register repetition is not duplication.** When a fact appears in both files but in different registers, narrative prose in README, rule-form in CLAUDE.md (e.g. README L14 "Le droit d'opposition est appliqué systématiquement", CLAUDE.md "Droit d'opposition : filtre `RETRAIT == 0` obligatoire"), they serve different audiences (human evaluator vs Claude editing code). Do not classify rule-form CLAUDE.md content as Mixed just because narrative-form coverage exists in README. Keep as HOW.

At the end of Phase 2, before Phase 3 starts, surface all Mixed/ambiguous items as a single batched list with one-line rationale per item. For each, ask the user to assign HOW, WHY, or "drop, no migration". Phase 3 then runs on the consolidated HOW/WHY classifications.

### 3. Migration

This is what distinguishes `/workflow:doc-structure` from `/workflow:sync`, which only detects inconsistencies without proposing moves.

**Source files identified in Phase 1** are the migration targets. For each file pair where Phase 1 substituted a source for a generated `.md`:

- Apply the edit to the source file (`.Rmd` / `.qmd` / `.in` / etc.), not the generated file
- After edits, surface the regen command to the user instead of running it: print the exact command (`Rscript -e 'rmarkdown::render("README.Rmd", quiet = TRUE)'` for R, `quarto render README.qmd` for Quarto) with a one-line note that running it may evaluate code chunks with side effects (DB connections, package loads, network calls). Let the user run it themselves. Never auto-execute regen commands: Claude cannot reliably classify which chunks are safe to evaluate
- The diff bundle shown to the user must reference the source path, with a note that the generated file will be rebuilt

**Verbatim-move as guard-rail.** Migration is proposed only when the prose can move verbatim into the target file and still make sense. If a candidate migration would require reformulation, granularity adjustment (file-level paths abstracted to module names), audience adaptation (dev-facing register rewritten as user-facing prose), or partial extraction (one bullet of a multi-bullet section), keep the content as HOW in CLAUDE.md and do not propose the move. Reformulating misplaced content belongs to a separate editorial pass, not to this skill's mechanical migration.

For each piece of misplaced prose that meets the verbatim bar:

- Propose verbatim move (CLAUDE.md prose → README.md section, or vice versa)
- **Pre-bundle reference check.** Before adding a proposed move to the bundle, parse the candidate prose for three reference classes and flag anything a verbatim move would break. Let the user decide per-move whether to drop the flagged move or accept it knowing the references will need a follow-up fix.
  - **Intra-file anchors** (`[text](#anchor)`). For each anchor, verify the target heading is either also being moved or already present in the destination file. Flag dangling anchors as "⚠ move M references `#anchor` which stays in source: link will break".
  - **Relative file paths** (`[text](relative/path.md)`, `[text](../sibling/file.md)`). Only relevant when source and target are in different directories (e.g. monorepo sub-package where `pkg/CLAUDE.md` and `pkg/docs/README.md` resolve relative paths differently). For each non-absolute, non-URL link, re-resolve the path from the target file's directory; if the resolved path does not exist or points to a different file than from the source, flag as "⚠ move M references `relative/path.md` which will resolve differently from target dir (source: `<from-resolved>`, target: `<to-resolved>`)".
  - **Image references** (`![alt](path)`, both Markdown and HTML `<img src="path">`). Same rule as relative paths above: flag when source and target directories differ and the path is relative. Image breakage is silent at render time, so the pre-diff flag is the only catch.
  - Same-directory moves (most root-level CLAUDE.md ↔ README.md cases) skip the relative-path and image checks entirely; only the anchor check runs.
- Bundle all proposed moves for the selected CLAUDE.md/README.md pair into a single before/after diff covering both files
- Wait for user approval on that bundle. The user may accept the whole bundle, reject the whole bundle, or selectively accept/reject individual moves within it (numbered list). No auto-apply across the project; granularity is per file pair, not per prose block

### 4. Index updates

After migrations, ensure `CLAUDE.md` provides a table-style index of what's where:

```
| Path | What | When to read |
|------|------|--------------|
| README.md | install + usage + architecture | when onboarding or evaluating an integration |
```

Placement: insert the table under a top-level `## Index` heading at the bottom of `CLAUDE.md`. If `## Index` already exists, replace its content (do not append a duplicate section). The "What" column states the file's primary content type in 3-6 words. "When to read" states a concrete trigger condition tied to a task ("when adding a new dataset", "when debugging the join pipeline", "when reviewing the consent-filter logic"), not a generic phrase like "before starting work".

When zero migrations were accepted in Phase 3, skip the table-replacement step but still run an index-freshness check: verify every path listed in the existing `## Index` table still exists at the project root. Surface any dangling entry as "Index references `<path>` which no longer exists" and let the user decide whether to remove it manually. Do not auto-remove.

### 5. Verification

When verification surfaces any issue (broken link, unresolved anchor, missing target file), do not auto-fix and do not roll back the migration. Report each issue as a list at the end of the run with file path, line number, and what looks wrong; let the user decide whether to fix manually, revert, or accept. Do not block the run on verification failures.

- Re-read modified files end-to-end
- Check that cross-references between CLAUDE.md and README.md still resolve. Scope: markdown links of the form `[text](path)` and `[text](path#anchor)` only. "Resolve" means: target file exists at the link path (relative to the linking file's directory), and if an anchor is present, a heading in the target file plausibly generates that anchor. Slug check is **best-effort, not a full GFM implementation**: apply the common rule (lowercase, spaces → `-`, punctuation stripped) and accept a match. Edge cases not covered: consecutive-space collapse, leading/trailing dash strip, non-ASCII characters, duplicate-heading `-1`/`-2` suffixes. When a link looks broken under the best-effort rule but the target heading exists with a similar slug, surface it as "unresolved: verify manually" rather than reporting a hard break. Do not check bare URLs, plain-text mentions of file names, or external links.

**Out of scope.** This skill does not propose relocation of a legacy `<project>/CLAUDE.md` to `<project>/.claude/CLAUDE.md`, even when the canonical location is missing. File-tree reorganization is a one-shot setup task; this skill audits the content layout of whichever location the user has chosen. To migrate the file itself, the user moves it manually with `git mv` before invoking the skill.

## Convention

- `.claude/CLAUDE.md` = project-specific rules for Claude (paths, datasets, naming, recent decisions) + an `## Index` section listing project documentation files with their purpose and read-trigger
- `README.md` (project root) = human-facing: architecture, install, usage
- No `README.md` in subdirectories unless at least one of these conditions holds: (a) the subdirectory contains a public entry point (CLI, library export, plugin install command) with its own usage instructions that do not fit the parent narrative; (b) the subdirectory is an independently testable or runnable unit; (c) the subdirectory is published, vendored, or distributed as a standalone artifact

**Monorepo handling.** One skill invocation covers one CLAUDE.md/README.md pair. For monorepos with sub-package docs, invoke the skill once per sub-package path (`/workflow:doc-structure <project>/packages/foo`). The skill never scans across multiple sub-packages in a single run.

## Lineage (not runtime instructions)

Three adjacent names tend to be confused. None of them is interchangeable:

- **`solatis/claude-config:doc-sync`**: original inspiration, captured during the 2026-05-16 audit. The HOW/WHY classification and the 5-phase workflow come from there.
- **`/workflow:doc-structure`** (this skill): renamed to avoid collision with `/workflow:sync` and to describe what it produces (a *structure* across `CLAUDE.md`/`README.md`) rather than the action.
- **`/workflow:sync`**: sibling skill in the same plugin. Detects drift inside one repo and propagates updates; does not migrate prose between files. Not derived from `doc-sync`; only the suffix is shared.

If you typed `/workflow:doc-sync`, it was likely a typo for `/workflow:doc-structure`.

## Maintainer notes (not runtime instructions)

The block below is a TODO list for the human maintainer. Claude must not act on it during normal skill invocation: do not propose `/audit:walkthrough` or any other command **on the basis of items listed in this block**. The global Build discipline rule still applies to the migration work itself: if a run produced non-trivial changes, propose adversarial review on the migration diff per the user's standing instructions.

- Re-audit with `/audit:walkthrough --reviewer audit:skill-adversary` to validate the trigger language now that the convention has stabilized.
