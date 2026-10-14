# workflow

Project workflow automation: file consistency sweeps, cross-repo synchronization, prose editing, and source-backed recommendations.

Every skill is **explicit-invocation only**: invoked by typing its slash command, never auto-triggered from natural language.
All three set `disable-model-invocation: true`, which keeps them out of the model's own skill listing as well, so describing a symptom in plain language reaches no skill here: Claude cannot propose, match or launch one it does not see, and the `Skill` tool refuses it by name even when the user typed that name.
That effect is measured rather than assumed: on 2026-10-10, when the marketplace carried nine skills, the four then carrying the flag were absent from the listing and the five without it were listed.
Once the flag reached all nine and both plugins were reinstalled, all nine were absent from the listing of a session started after that install, on 2026-10-14, while a slash command typed by the user still reached its skill.

## Install

```bash
claude plugin marketplace add hebstr/claude-code-plugins
claude plugin install workflow@hebstr
```

## Skills

  | Skill                               | Invocation                                 | Purpose                                                                                                                                                                                                      |
  | ----------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
  | [`sync`](./sync/)                   | `/workflow:sync`                           | Scans all project files for staleness and updates them. Always runs a cross-repo semantic consistency pass with parallel agents.                                                                             |
  | [`write`](./write/)                 | `/workflow:write`                          | Strips AI writing patterns and rewrites prose to read naturally. Routes to a French or English reference per text language; includes a bilingual review mode (FR-EN parity, typography, false friends).      |
  | [`reco`](./reco/)                   | `/workflow:reco`                           | Deep recommendation backed by external sources. Parallel agents pull official docs (WebFetch) and community practice (WebSearch); the skill synthesizes a structured recommendation with verified citations. |

## Per-skill details

### `/workflow:sync`

Performs a single-repo sweep for drift between recently changed files and the rest of the tree (counts, references, doc tables, permission/config gates).
Then runs a cross-repo semantic scan with parallel agents that check consistency between sibling repos sharing concepts (shared docs, shared manifests, mirrored APIs).

### `/workflow:write`

Detects the source language from the text itself and loads the matching FR or EN reference, then edits in place without commentary.
Bilingual review mode applies to FR-EN parity work (release notes, mixed-language docs).

### `/workflow:reco`

Spawns two parallel agents (official documentation via WebFetch, community practice via WebSearch), then produces a structured output (my take, tradeoffs, official docs, community, final recommendation).
URLs are verified before being cited.
Disagreement between sources is surfaced, not papered over.
Use it when external grounding matters; for an unsourced recommendation based only on what Claude already knows, just ask directly.

## Common usage

```bash
# At session end: sweep the current project for staleness and cross-repo inconsistencies
/workflow:sync

# Strip AI slop patterns from a draft
/workflow:write

# Deep, source-backed recommendation on a topic
/workflow:reco "topic"
```

## Requirements

**Required:**

- [Claude Code](https://claude.com/claude-code) with plugin marketplaces enabled
- `git` (for `workflow:sync`; outside a git repo, the skill asks the user for the file list)

No other external dependencies.

## License

[MIT](../LICENSE.md)
