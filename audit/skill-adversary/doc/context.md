# Context: skill-adversary for Claude Code

## Goal

Create a `skill-adversary` skill complementary to `skill-creator`, acting as an adversary/critic during skill creation.

---

## Prior art (research conducted)

**What exists nearby but doesn't cover the need:**

- **`task-observer`** (rebelytics) — meta-skill that observes live sessions, captures corrections, and suggests improvements. Passive, not adversarial.
- **`skill-auditor`** in TASKS resources — mentioned in awesome-claude-code, exact repo not publicly findable.
- **`hamelsmu/error-analysis`** and **`hamelsmu/validate-evaluator`** — skills for auditing LLM pipelines, oriented toward general eval, not skill creation.
- **`critical-code-reviewer`** (posit-dev) — adversarial code review (security, edge cases, lazy patterns), but for code, not SKILL.md files.
- **`posit-dev/skills` `critical-code-reviewer`** — adversarial code review, not skill review.

**Conclusion: a dedicated `skill-adversary` for skill creation does not exist.**

---

## Problem to solve

`skill-creator` has a blind spot: it's optimistic by construction. It drafts, tests on positive cases, and iterates toward something that *works*. What it doesn't do: actively search for what *breaks*.

For triggers in particular, the description optimization in `skill-creator` generates training cases consistent with the creator's intent — which is exactly the bias an adversary should attack.

---

## Proposed architecture

```
skill-creator (builder, READ-WRITE)
    ↕  passes the draft
skill-adversary (critic, READ-ONLY)
    → produces a flaw report
    ↕  feedback
skill-creator iterates
```

File structure:

```
skill-adversary/
├── SKILL.md
└── agents/
    ├── trigger-attacker.md   ← false positives / false negatives
    └── instruction-critic.md ← ambiguities in the SKILL.md
```

`output-fuzzer.md` is planned for V2 (see `doc/v2.md`) — it would handle the third axis (output degradation) below.

---

## Three attack axes

**1. Trigger attacks**
Generate prompts that *look like* the skill without being it (false positives) and legitimate prompts phrased differently (false negatives). `skill-creator` optimizes the description but with positive cases — an adversary attacks the boundaries.

**2. Instruction stress-testing**
Identify ambiguities, contradictions, gaps in the SKILL.md: cases where two instructions conflict, under-specified steps, undefined behavior on edge inputs.

**3. Output degradation**
Find valid inputs that cause the output to drift from the expected format — useful for skills with quantitative assertions.

---

## Main limitation: intra-model bias

The judge and the defendant are the same model. Claude evaluates a SKILL.md written by Claude, which limits true adversariality. A human spots ambiguities that Claude won't see because it resolves them implicitly using its context.

**Levers to reduce this bias:**

1. **Context isolation** — The critic is spawned as a sub-agent with only the finished SKILL.md, no conversation history. Simulates a naive reader. Pattern already used in glebis's TDD skill (tester isolated from implementer).

2. **Persona forcing** — Force the critic to adopt specific user profiles incompatible with the author. Not "be critical" (too vague), but: "You are a user who has never heard of X, formulate 10 natural requests without using the skill's keywords."

3. **Different models** — Strongest lever: use a different model for the critique. In agent teams, each teammate can have its own `model:` in the YAML frontmatter. Skill created with Sonnet, critiqued by Opus (or vice versa) — the two models have distinct blind spots.

4. **Deferred critique** — Launch the critic in a fresh session without context. Reduces anchoring on the original intent. Zero cost, modest gain.

5. **Human feedback via task-observer** — task-observer captures corrections made during real usage. A skill-adversary could interface with it: task-observer observations feed the critic.

**What remains irreducible:** levers 1-4 reduce the bias without eliminating it. Human validation on real use cases remains the floor — which skill-creator already provides with the eval viewer. `skill-adversary` is an amplifier of the human phase, not a substitute.

**Practical recommendation:** lever 3 (different models via agent teams) + lever 1 (context isolation) = best effort/gain ratio.

---

## Correct positioning

Position as **"ambiguity detector and edge case generator"** rather than "full red team". The real value is in trigger attacks (false positives/negatives) where systematic generation has concrete value even intra-model.
