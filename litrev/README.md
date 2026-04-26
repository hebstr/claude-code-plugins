# litrev

A Claude Code skill suite that conducts systematic, scoping, narrative, rapid, and meta-analytic literature reviews on medical and health research topics.
Searches PubMed/MEDLINE, Semantic Scholar, and OpenAlex, screens articles, extracts claims, writes a thematic synthesis with Pandoc citations, and verifies every reference against CrossRef and PubMed.

## Architecture

Hybrid architecture: **sub-skills** handle LLM reasoning (search strategy, screening decisions, synthesis writing), while a **MCP server** (`mcp/`) handles deterministic execution (API calls, deduplication, BibTeX generation, claim verification). **Agents** handle post-pipeline quality audits.

The orchestrator (`litrev`) handles planning, sequencing, and quality gates.

```
skills/
├── litrev/                    ← orchestrator (sequencing + gates)
│   └── agents/
│       ├── audit_fidelity.md  ← Phase 8: fidelity audit (claims vs sources)
│       └── audit_methodology.md ← Phase 8: methodology audit (synthesis critique)
├── litrev-search/             ← Phase 2: search strategy (LLM) + MCP execution
├── litrev-screen/             ← Phase 3: screening decisions (LLM) + MCP abstract fetch
├── litrev-extract/            ← Phase 4: claim extraction (LLM) + MCP regex extraction
└── litrev-synthesize/         ← Phase 5: constrained thematic writing (LLM only)
mcp/                           ← MCP server: 15 deterministic tools
```

### MCP tools (`mcp/`)

| Tool | Purpose |
|------|---------|
| `search_pubmed` | Keyword search on PubMed via NCBI E-utilities |
| `search_s2` | Authenticated keyword search on Semantic Scholar |
| `search_openalex` | Keyword search on OpenAlex Works API |
| `process_results` | Deduplicate, rank, filter, format search results |
| `deduplicate_results` | Deduplicate combined_results.json by PMID/DOI/title |
| `fetch_abstracts` | Retrieve missing abstracts from PubMed |
| `fetch_fulltext` | Full-text retrieval via PMC/Unpaywall/S2 cascade |
| `get_section` | Extract a specific section from cached full text |
| `extract_claims_regex` | Quantitative claim extraction by regex |
| `citation_chain` | Backward/forward citation chaining via Semantic Scholar + OpenAlex |
| `verify_dois` | DOI/PMID validation + retraction check (CrossRef + PubMed) |
| `generate_bibliography` | BibTeX generation (3-level DOI resolution) |
| `audit_claims` | Cross-verify numerical claims vs source abstracts |
| `validate_gate` | Mechanical gate validation for review pipeline phases |
| `import_corpus` | Import user-supplied bibliographic files (BibTeX, RIS, CSV, TSV, PMIDs, DOIs) |

### Design principles

- **Hybrid**: LLM reasoning in skills, deterministic execution in MCP tools
- **Interface contracts**: phases communicate through well-defined JSON and markdown files in `review/`
- **Lightweight orchestrator**: sequencing and gate checks only, no domain logic
- **Session resumable**: pipeline state persisted to `review/` files
- **Double audit**: fidelity + methodology audits with interactive walkthrough before completion

### Pipeline flow

```
Planning → Search → Screen → Snowball (optional) → Extract → Synthesize → Verify → Final QC → Double Audit + Walkthrough → Pipeline Log
```

| Phase | Delegate | What it does |
|-------|----------|--------------|
| 1 | `litrev` | Define research question (PICO/PEO/SPIDER), scope, inclusion/exclusion criteria |
| 2a | Skill `litrev-search` + MCP `process_results`, `deduplicate_results` | Query databases, deduplicate and rank results |
| 2b | MCP `import_corpus` (optional) | Import user-supplied bibliographic files, enrich and merge |
| 3a | Skill `litrev-screen` + MCP `fetch_abstracts`, `fetch_fulltext`, `get_section` | Multi-pass title/abstract screening with PRISMA counts and optional full-text retrieval |
| 3b | MCP `citation_chain` + inline screening | Backward and forward citation chaining |
| 4 | Skill `litrev-extract` + MCP `extract_claims_regex` | Claim extraction, quality assessment, theme assignment |
| 5 | Skill `litrev-synthesize` | Constrained thematic writing — every claim traced to source |
| 6 | MCP `verify_dois` + `generate_bibliography` + `audit_claims` | DOI validation, BibTeX generation, claims audit |
| 7 | `litrev` | Final quality checklist (10 items) |
| 8 | Agent `audit_fidelity` + Agent `audit_methodology` + `/review-walkthrough` | Fidelity + methodology audit, interactive walkthrough |
| 9 | `litrev` | Pipeline log (funnel metrics, gate log, corrections, MCP issues); automatic memory update with new quality patterns and MCP bugs |

### Review types

| Type | Min. databases | Snowballing | Quality assessment | PRISMA |
|------|:-:|---|---|---|
| Systematic | 3 | Automatic (both) | Full (RoB/GRADE) | Full PRISMA 2020 |
| Meta-analysis | 3 | Automatic (both) | Full (RoB/GRADE) | Full PRISMA 2020 |
| Scoping | 3 | User opt-in (both) | Optional (PRISMA-ScR) | PRISMA-ScR |
| Narrative | 2 | User opt-in (backward only) | Simplified | Simplified |
| Rapid | 2 | User opt-in (forward, cap 5) | Simplified | Simplified |

## Installation

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed and authenticated
- Python >= 3.11 with [uv](https://docs.astral.sh/uv/)
- Internet access (PubMed, Semantic Scholar, OpenAlex, CrossRef, doi.org APIs)

### Install via plugin

```bash
claude plugin marketplace add hebstr/claude-code-hebstr
claude plugin install litrev@hebstr
```

The MCP server (`litrev-mcp`) is auto-registered via the bundled `.claude-plugin/.mcp.json`, which uses `${CLAUDE_PLUGIN_ROOT}/mcp` to resolve the install path:

```json
{
  "mcpServers": {
    "litrev-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "${CLAUDE_PLUGIN_ROOT}/mcp", "litrev-mcp"],
      "env": {
        "LITREV_EMAIL": "${LITREV_EMAIL}",
        "NCBI_API_KEY": "${NCBI_API_KEY}",
        "S2_API_KEY": "${S2_API_KEY}"
      },
      "timeout": 120
    }
  }
}
```

`uv` regenerates the project venv on first invocation. No manual `uv sync` step required.

### Optional: environment variables

The litrev-mcp server works without these, but setting them improves rate limits and API compliance.
Configure them in your MCP client `env` block or shell environment.

| Variable | Effect |
|---|---|
| `LITREV_EMAIL` | Your email — activates polite pool (faster rates) for NCBI, CrossRef, OpenAlex. Falls back to `NCBI_EMAIL`. |
| `NCBI_API_KEY` | Raises PubMed rate limit from 3 to 10 req/s. Free at https://www.ncbi.nlm.nih.gov/account/settings/ |
| `S2_API_KEY` | **Strongly recommended.** Without it, Semantic Scholar searches are severely rate-limited (~1 req/s) and may return incomplete results. The orchestrator will halt on degraded S2 search. Free at https://www.semanticscholar.org/product/api#api-key |

## Usage

### Full review (orchestrated)

Navigate to any directory where you want the review output, then ask Claude Code:

```
Fais-moi une revue systématique sur les probiotiques dans le traitement des infections récurrentes à C. difficile
```

```
What does the evidence say about rotator cuff comorbidities in shoulder pain?
```

```
Revue de la littérature sur l'impact du diabète sur la chirurgie de la coiffe des rotateurs
```

The orchestrator triggers automatically, guides you through planning, and runs each phase sequentially.
All output goes to `review/` in the current directory.

See [PROMPT_RECOS.md](skills/litrev/PROMPT_RECOS.md) for tips on writing effective prompts (exclusion criteria, framework, review type, grey literature).

### Individual phases (standalone)

Each sub-skill can be invoked independently:

```
/litrev-search
/litrev-screen
/litrev-extract
/litrev-synthesize
```

MCP tools can also be called directly by the LLM when needed.

### Resuming a review

If a review is interrupted, simply re-invoke the skill in the same directory.
The orchestrator detects existing files in `review/` and resumes from the first incomplete phase.

## Output

All files are written to `review/` in the current working directory:

| File | Content |
|------|---------|
| `protocol.md` | Research question, framework, criteria, search strategy |
| `combined_results.json` | Aggregated, deduplicated search results |
| `search_results.md` | Ranked results table |
| `search_log.md` | Search documentation (queries, databases, counts) |
| `screening_log.md` | Screening decisions with PRISMA flow |
| `abstracts_for_screening.md` | Fetched abstracts for screening (Phase 3a) |
| `included_indices.json` | Indices of included articles |
| `extracted_claims.json` | Structured claims with quality ratings and themes |
| `<topic>_review.md` | The review document (Pandoc markdown with `[@citations]`) |
| `references.bib` | Verified BibTeX bibliography |
| `claims_audit.json` | Cross-verification of every numerical claim |
| `<topic>_review_citation_report.json` | DOI/PMID verification results |
| `vancouver.csl` | Citation style file |
| `audit_fidelity.md` | Fidelity audit report (claims vs sources) |
| `audit_methodology.md` | Methodology audit report (synthesis critique) |
| `DEFERRED.md` | Deferred findings with justifications (if any) |
| `pipeline_log.md` | Pipeline run report (funnel metrics, gate log, corrections, MCP issues) |

The review document can be compiled to PDF, DOCX, or HTML with Pandoc:

```bash
cd review
pandoc <topic>_review.md --citeproc --bibliography=references.bib --csl=vancouver.csl -o review.pdf
```

## Example

See [example-3/](workspace/example-3/) for example inputs (prompt + context). Output files are generated by running the skill in that directory.

## Development

| Doc | Purpose |
|-----|---------|
| [PLAN.md](PLAN.md) | Current objective, steps, and resume context |
| [DEFERRED.md](DEFERRED.md) | Findings deferred from code reviews |
| [PROMPT_RECOS.md](skills/litrev/PROMPT_RECOS.md) | User-facing tips for writing litrev prompts |
