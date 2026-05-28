---
name: reco
description: "Deep recommendation backed by external sources (official documentation + community practice + verified citations). For an unsourced recommendation, ask the model directly; use this skill when external grounding is what makes the answer load-bearing. Without arguments: ask the user what they want a recommendation on. With arguments: research the topic via parallel agents (official docs via WebFetch, community practice via WebSearch), then synthesize a structured recommendation. User-invocable ONLY via /workflow:reco; does not auto-trigger on mentions of 'recommendation', 'reco', 'recommend', 'suggest', 'advice', or French equivalents ('reco', 'recommande', 'recommandation', 'conseille', 'suggère')."
allowed-tools: WebFetch WebSearch Agent
---

# Reco

Deep-mode recommendation backed by external sources.

## Invocation

This skill only runs when the user types `/workflow:reco` explicitly. It is not auto-triggered by semantic description matching.

If you arrived here through anything other than an explicit `/workflow:reco` invocation, stop and ask the user what they actually want.

For an unsourced recommendation, ask the model directly without invoking this skill. Use `/workflow:reco` when external grounding (official documentation + community practice + verified citations) is what makes the answer load-bearing.

## Input

`/workflow:reco <free-form description of what the user is considering>`

Examples:
- `/workflow:reco should I use polars or pandas for this CSV pipeline (1M rows, mostly transforms)?`
- `/workflow:reco best way to structure a Python CLI with subcommands and a config file`
- `/workflow:reco what's the recommended pattern for stopping criteria in evolutionary algorithms`

If invoked with no arguments, ask the user what they want a recommendation on: do not guess from prior context. Once they reply, treat the reply as the topic and proceed to Step 1.

## Process

1. **Parse the input.** Identify the domain (R, Python, shell, architecture, statistics, etc.), the specific question, and the constraints if mentioned. A dimension is *load-bearing* when its value would plausibly change the recommendation, typically scale (data size, request volume), context (one-off vs production, team size), or stack (existing tooling that constrains the choice). If the input is silent on a load-bearing dimension, ask one clarifying question before proceeding. Otherwise, proceed without asking, do not interrogate the user about non-load-bearing dimensions.

2. **Write the "My take" section now, before spawning any agent.** Emit the section heading and 1-3 sentences of your prior recommendation from training-data knowledge alone. This is the only point in the workflow where the prior can be formed without contamination by agent output. Commit to the take in writing here; do not rewrite it after agents return.

   **Scope check.** After writing the take, decide whether external sources can meaningfully refine it. If the question is purely local (naming a private variable, choosing between two same-codebase helpers, formatting a single function), no public source will outweigh the user's own context. Stop here, emit a one-line note ("Question is local, no external research applicable; the unsourced take above is the full answer."), and do not spawn agents. Otherwise, proceed to Step 3.

3. **Spawn two parallel agents** in a single message (two `Agent` tool calls):
   - **Agent A: official documentation.** Search for and fetch the relevant official docs. Prefer authoritative sources (project websites, PEPs for Python, CRAN docs for R, RFCs, etc.). Verify URLs before citing. Report what the doc actually says, with quoted excerpts and source URLs. The agent must have WebFetch and WebSearch.
   - **Agent B: community practice.** Search blogs, conference talks, GitHub issues, Stack Overflow answers, and notable practitioners' writing. Report consensus and divergences with sources. Same capability requirement as Agent A.

4. **Synthesize in the main thread.** Wait for both agents, then produce the remaining output sections (`## Tradeoffs`, `## What the official documentation says`, `## What the community recommends`, `## Final recommendation`): `## My take` was already emitted in Step 2 and must not be rewritten.

   **Verification before citing.** Agent reports are unverified: do not rubber-stamp. Every URL that appears in the synthesis must be re-verified via WebFetch in the main thread; on verification failure, drop the URL, replace with the source name in prose, and lower the Final recommendation confidence. For CLI flags, API syntax, and version numbers: check the top citation per claim against the official doc agent's quoted excerpt; if the excerpt does not support the claim, omit it from the synthesis.

   **Agent failure handling.** If one agent errors out, times out, or returns nothing usable: proceed with the other agent's results, render the failed agent's section with an explicit "<source-type> retrieval failed: no evidence available" note, and lower the confidence in the Final recommendation. If both agents fail: stop, tell the user that no external sources could be retrieved, and do not fabricate placeholder content to fill the template.

## Output structure

```
## My take
<1-3 sentences: direct recommendation with reasoning, written in Step 2 before any agent is spawned>

## Tradeoffs
<bullet list of the key tradeoffs, max 5>

## What the official documentation says
<summary from Agent A with quoted excerpts and verified URLs; if no authoritative doc found, say so>

## What the community recommends
<summary from Agent B noting consensus vs divergence, with sources; flag if the community contradicts the docs; if no community signal found, say so>

## Final recommendation
<single sentence stating the recommendation, then 1-2 lines of justification grounded in the evidence above>
<if sources disagree or evidence is thin, say so explicitly and lower the confidence>
```

## Guardrails

- Never write a URL without verifying it with WebFetch. Training-data URLs are unreliable. If verification fails, omit the link and say so.
- If sources disagree, surface the disagreement: do not paper over it.
- If neither agent finds authoritative material, lower confidence in the final recommendation and say what evidence is missing.
- Mirror the user's conversation language for prose. The output structure headers (`## My take`, `## Tradeoffs`, `## What the official documentation says`, `## What the community recommends`, `## Final recommendation`) stay in English regardless of conversation language: they are technical section identifiers, not prose.
- Stay in the scope of the question. Do not expand to adjacent decisions unless directly relevant.
- The "My take" section is written in Step 2, before any agent is spawned: this is intentional, so that external sources can confirm, refine, or overturn an independent prior rather than anchor it.
