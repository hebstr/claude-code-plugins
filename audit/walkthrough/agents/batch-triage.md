---
name: walkthrough-batch-triage
description: Triages review findings into auto-fix, auto-reject, and manual buckets.
  Applies batch fixes with verification, runs post-fix hooks, and hands the manual bucket to the interactive walkthrough.
---

# Review Walkthrough: Batch Triage

The walkthrough skill executes this file in its own main context, never as a subagent: step 2 below waits on the user, and a subagent has no way to reach them.

You accelerate large reviews by triaging findings into three buckets and batch-processing the obvious ones.
You receive the extracted findings list and the deployment context, and hand back the manual bucket for the interactive walkthrough plus batch results for the wrap-up.

## Input

From the parent skill:
- **findings**: the full list of extracted findings (from Step 1), each with: number, description, file(s), severity tier (if any), and (when the input came from `blindspot`) a bucket tag: `agreed`, `claude-only`, or `external-only`
- **deployment context**: personal / internal / production, or `unknown` (from the orchestrator in orchestrator mode, otherwise resolved by SKILL.md Step 1b before it calls this file)

## 1. Rapid pre-verdict

For each finding, read the relevant code first and form your own quick assessment (1-2 sentences) before comparing it to the reviewer's claim, same anti-confirmation-bias discipline as SKILL.md Step 2b.
Do **not** apply the author's defense, it is reserved for the manual walkthrough.
Do **not** invoke Ouroboros QA.

Classify each finding into one bucket:

  | Bucket          | Criteria                                                                                                                           | Action                       |
  | --------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
  | **Auto-fix**    | Clearly valid AND matches a mechanical pattern (whitelist below) AND NOT classified Important+ (see severity rule below)           | Fix applied in batch         |
  | **Auto-reject** | Clearly a false positive or out of context (contradicted by code, calibrated away by context detection, or obviously inapplicable) | Rejected in batch (REJECTED) |
  | **Manual**      | Verdict uncertain, fix non-trivial, touches multiple files, Important+, or none of the above                                       | Full individual walkthrough  |

**Conservative default:** when in doubt, classify as Manual.
Batch mode is an accelerator, not a filter.

**On an `unknown` deployment context**, the auto-reject row's "calibrated away by context detection" ground is unavailable: a finding whose only ground for rejection is the context goes to Manual, and the other two grounds, contradicted by the code and obviously inapplicable, still stand on their own.
Report the unresolved context in the batch summary, so a rejection the context would have carried is visibly absent rather than silently assumed.

**Important+ findings always go to Manual**, regardless of how obvious the fix seems.
"Important+" matches the same tier set used by SKILL.md Step 2b for the author's defense: any tier whose name signals a required or blocking change, case-insensitive (Important, Required, Blocking, Critical, Major, High).
Tiers signalling optional, cosmetic, or informational intent (Minor, Suggestion, Nit, Info, Style) remain eligible for auto-fix or auto-reject.
When a tier name is ambiguous, err toward Manual.

**Blindspot bucket override.** When findings carry a blindspot bucket tag (i.e., the input came from `blindspot`), apply this rule **before** the auto-fix whitelist:

  | Bucket tag      | Eligible for auto-fix      | Eligible for auto-reject | Rationale                                                                                                                                                                        |
  | --------------- | -------------------------- | ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | `agreed`        | yes (if matches whitelist) | yes                      | Cross-validated by external model in Phase 1; both auto paths are safe.                                                                                                          |
  | `claude-only`   | **no, force Manual**       | **no, force Manual**     | The external model did not flag this; high self-preference bias risk. Auto-applying or auto-rejecting would bypass the very check the cross-model judgment was meant to provide. |
  | `external-only` | **no, force Manual**       | **no, force Manual**     | Claude tends to under-rate findings the external model flagged but Claude missed; the cross-provider verdict is load-bearing and must be reviewed by the user before any action. |

This override takes precedence over the severity rule (Important+ → Manual).
It does not relax it: a `claude-only` Suggestion still goes to Manual; an `agreed` Blocking finding still goes to Manual via the severity rule.

### Auto-fix whitelist

Only these mechanical patterns qualify.
Everything else goes to Manual:
- Unused imports or variables (removal only)
- Missing type annotations on function signatures, only when the reviewer's finding names the exact annotation to add (addition only, no logic change)
- Typos in strings, comments, or identifiers (exact correction obvious from context)
- Missing `return` type annotations, on the same condition
- Trivial format/lint fixes explicitly flagged by the reviewer (trailing whitespace, missing newline at EOF)
- Dead code removal when the reviewer explicitly identifies the code as unreachable

The two annotation entries carry that condition and the others do not, because adding an annotation is the only pattern here that invents content rather than removing or correcting what the code already determines.
Nothing in the walkthrough runs a type checker, and Step 2d verifies by re-reading, so an inferred annotation would be judged by the model that inferred it.
Spelled out by the reviewer it is as mechanical as the rest; left to inference it goes to Manual, where the finding meets the author's defense, the cross-model checks and the user.

If a finding matches a whitelist pattern but the fix would touch more than one file, it goes to Manual.

## 2. Present the triage

Show the user: a one-line summary (`Triage: N findings — X auto-fix, Y auto-reject, Z manual`), then three tables (auto-fix: `# | Finding | File | Fix`; auto-reject: `# | Finding | Reason | Calibration`; manual: `# | Finding | File | Severity | Reason for manual`).

The auto-reject table's `Calibration` column reads `rule` when SKILL.md Step 4b would turn that rejection into a lasting calibration rule, and `none` when it would not, an excluded category or a rejection too specific to generalize both reading `none`.
A rejection reached this table through the rapid pre-verdict, which skips the author's defense and QA and never reaches L1 or L2, so this prompt is the only place the user sees a permanent rule before it is written.
State that in one line above the prompt rather than leaving the column to speak for itself.

End with `Override? (e.g., "move 3 to manual", "move 2 to auto-fix", or "ok")`.
Wait for confirmation or overrides, apply them, then proceed.

## 3. Batch execution

**Auto-reject:** mark all as REJECTED with the one-line reason from the table.
No code changes.

**Auto-fix:** apply fixes sequentially.
After each fix, re-read the modified file + files one level away (same verification as Step 2d in the parent skill).
If verification fails:

1. Revert the fix immediately, by applying its inverse edit: restore the exact text the fix replaced, with the same editing tool that applied it.
   Never revert with `git checkout`, `git restore`, `git stash` or any other whole-file operation: those discard every uncommitted change in the file, which here means the auto-fixes applied earlier in this same batch and whatever the user already had in the tree, a dirty tree being a case Step 0 tolerates rather than blocks.
   When the inverse edit cannot be reconstructed, leave the change in place and say so rather than reaching for a git command: a reported failure costs the user one manual revert, a wiped file costs them work the walkthrough never touched.
2. Move the finding to Manual.
3. Continue with the next auto-fix.

### Post-fix hooks

After all auto-fix operations, check if any fix modified a dependency manifest (in a dependency section only).

**Do not execute lock/install commands automatically.** Package managers like `npm`, `yarn`, `pnpm`, `uv`, `pip-compile`, and `cargo` resolve and may execute arbitrary code from the dependency tree (e.g. `postinstall` scripts, build scripts).
Running them on behalf of the user without their explicit consent is a supply-chain attack vector, even when the modification was a removal.
Instead, **print the exact command(s) the user should run manually**, with a one-line warning, and continue.

  | File modified                 | Command for the user to run                                              |
  | ----------------------------- | ------------------------------------------------------------------------ |
  | `pyproject.toml` (deps)       | `uv lock` (if uv.lock exists) or `pip-compile`                           |
  | `package.json` (deps)         | `npm install` or `yarn install` or `pnpm install` (detect from lockfile) |
  | `Cargo.toml` (deps)           | `cargo update`                                                           |
  | `renv.lock` / DESCRIPTION (R) | `Rscript -e 'renv::snapshot()'`                                          |

Format the printout as a single block at the end of the batch summary:

```
Dependency manifest(s) modified — run manually before continuing:
  cd <project_root> && <command>
Warning: package install/lock commands may execute scripts from third-party packages. Review the diff before running.
```

### Ouroboros QA on auto-reject (optional)

If Ouroboros is available, run a QA check on each auto-reject finding: `artifact` = the code section, `quality_bar` = the finding's claim.
A score at or above `QA_PASS_THRESHOLD` confirms the rejection, and below it the finding moves to Manual silently.
The threshold is the one `agents/ouroboros-bridge.md` declares, named rather than repeated here: it is calibrated against that file's `MAX_TESTED` and is to be re-validated whenever that is bumped, which a literal copied into this file would quietly survive.
Report the number of QA-promoted findings in the batch summary if any were moved.

## 4. Report and hand back

After all batch operations, report:

```
Batch complete: X/Y auto-fix applied, Z reverted → moved to manual.
W auto-reject confirmed.
Starting manual walkthrough: N findings.
```

## Output

Hand back to the walkthrough skill's Step 2:
- **manual bucket**: the list of findings for interactive walkthrough (Step 2).
**Each finding must preserve all input metadata**: index, severity tier, file paths, and (when present) the blindspot bucket tag (`agreed` / `claude-only` / `external-only`).
The parent skill needs the bucket tag for the Step 3 wrap-up table's Bucket column and for routing decisions in Step 2b.
- **batch results**: auto-fix and auto-reject outcomes for the wrap-up table (Step 3); also include the bucket tag per finding when present.
- **batch stats**: counts for Step 3's breakdown by mode and its Mechanisms block (auto-fix applied, reverted, auto-reject confirmed, QA-promoted), never for Step 1's transparency status, which rendered before this file ran
