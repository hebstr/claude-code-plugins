# Claude Code plugins

Skills extend Claude Code with specialized workflows that activate automatically based on the task. Learn more at the [Claude Skills documentation](https://support.claude.com/en/articles/12512180-using-skills-in-claude).

## Install

Add the marketplace, then install plugins individually:

```bash
claude plugin marketplace add hebstr/claude-code-hebstr
claude plugin install review@hebstr
claude plugin install workflow@hebstr
claude plugin install litrev@hebstr
```

## Plugins

### `review`

Code, skill, and MCP review workflows — orchestrated walkthroughs, full-project audits, adversarial critique, and circularity-aware cross-model review.

| Skill | Purpose |
|---|---|
| [`review-walkthrough`](./review/review-walkthrough/) | Interactive, point-by-point walkthrough of any review report — re-evaluates findings, proposes fixes, checks impacted files for regressions |
| [`full-review`](./review/full-review/) | Full-coverage project review with parallel specialist agents (architecture, quality, tests, docs), consolidated into a single deduplicated report |
| [`blindspot-review`](./review/blindspot-review/) | Circularity-aware orchestrator that detects when a reviewer shares its target's codebase or model family, then injects cross-model judging via OpenRouter |
| [`skill-adversary`](./review/skill-adversary/) | Adversarial critic for Claude Code skills — finds trigger edge cases, instruction ambiguities, cross-file coherence issues, and gaps |
| [`mcp-adversary`](./review/mcp-adversary/) | Adversarial critic for MCP servers — finds inter-tool discrimination issues, schema anti-patterns, semantic drift, and undocumented workflow dependencies |

### `workflow`

Project workflow automation — file consistency sweeps and cross-repo synchronization.

| Skill | Purpose |
|---|---|
| [`sync-files`](./workflow/sync-files/) | Scan all files, identify ones that are stale relative to recent changes, and update them. `--deep` mode runs a cross-repo semantic consistency scan with parallel agents |

### `litrev`

Systematic literature reviews for medical and clinical research — search, screen, extract, synthesize. Bundles a Python MCP server (`litrev-mcp`) and 5 skills covering the full PRISMA pipeline.

| Skill | Purpose |
|---|---|
| [`litrev`](./litrev/skills/litrev/) | Orchestrator for systematic, scoping, narrative, rapid, and meta-analytic reviews — sequencing, gates, double audit |
| [`litrev-search`](./litrev/skills/litrev-search/) | Multi-database search aggregation (PubMed, Semantic Scholar, OpenAlex) with relevance gate |
| [`litrev-screen`](./litrev/skills/litrev-screen/) | Title/abstract/full-text screening with structured screening log and PRISMA counts |
| [`litrev-extract`](./litrev/skills/litrev-extract/) | Claim extraction (regex + LLM enrichment), quality assessment, theme assignment |
| [`litrev-synthesize`](./litrev/skills/litrev-synthesize/) | Constrained thematic synthesis from extracted claims with Pandoc citations |

The MCP server is bundled at [`litrev/mcp/`](./litrev/mcp/) and provides 15 deterministic tools (database APIs, deduplication, claim verification, BibTeX generation). It runs via `uv` and is auto-registered when the plugin is installed.

## Requirements

[Claude Code](https://claude.com/claude-code) with the plugin marketplace feature enabled.

## License

[MIT](./LICENSE.md)
