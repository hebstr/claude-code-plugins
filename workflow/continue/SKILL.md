---
name: continue
description: Flush durable facts to memory, update PLAN.md, and print a minimal continuation prompt. No handoff document is written. User-invocable only via /workflow:continue.
allowed-tools: Read, Write, Edit
---

# Continue: Session Handoff

Persist what matters across sessions, then generate a minimal continuation prompt.
PLAN.md and memory are the authoritative stores.

## Step 1 — Write to memory

For each non-obvious decision, constraint, or pattern discovered this session that would be useful in future conversations:
- Write or update the relevant memory file following project memory conventions.
- Update MEMORY.md index.
- Skip anything derivable from code or git history, and anything that is only relevant to this session.

If nothing new was discovered, skip this step.

## Step 2 — Update PLAN.md

Read `.claude/PLAN.md` if it exists. If it does not exist and the session had no multi-step task, skip this step entirely. Otherwise create it. Update:
- Mark completed steps as done.
- Update current step.
- Add or reorder open items by priority.
- Be precise: file paths, function names, line numbers.

## Step 3 — Print continuation prompt

Print directly (no file written) a short prompt the user can paste into a new session:
- One sentence of context.
- If memory files were written in Step 1: list them by name (e.g. `memory/feedback_xyz.md`), not a generic reference.
- If PLAN.md was written or updated in Step 2: "Read `.claude/PLAN.md` for current task state." and "Continue from: [specific next step, verbatim from PLAN.md]."
- If Step 2 was skipped: omit the PLAN.md lines entirely.

## Rules

- Write in English (memory files and PLAN.md are technical artifacts, not conversation)
- Be precise in PLAN.md: file paths, function names, line numbers — not vague summaries
- Memory: only write what is non-obvious and durable — never ephemeral task state; prefer updating an existing memory file over creating a new one
- Do not create CONTINUATION-PROMPT.md
