---
name: litrev
context: main
description: Conduct systematic reviews, scoping reviews, meta-analyses, and evidence syntheses for medical, clinical, and health research. Also triggers for medical/health topics: state-of-the-art summaries, evidence maps, clinical practice guidelines, or requests to summarize/synthesize published studies — including functional descriptions like "what does the evidence say about [medical topic]", "what do we know about [medical topic]", "what does the science say about [medical topic]", "what have studies found on [medical topic]", "summarize the research on [medical topic]", "go through all the studies on [treatment/condition]", "combine the results across trials", "find gaps in the literature on [medical topic]", "pull together the evidence on [medical topic]", "what's been published on [medical topic]", "pool/synthesize the estimates across studies", "run a pooled analysis on [medical topic]", "pooled data from multiple trials", or "revue de la littérature / revue systématique / méta-analyse / synthèse des preuves / état de l'art / état des connaissances / guide de pratique clinique / passer en revue les études sur / aperçu de ce qui a été publié sur / résumer les études sur / faire le point sur les publications sur / qu'est-ce qu'on sait sur [sujet médical] / tout ce qui existe comme études sur". Also triggers for informal variants: "lit review on [medical topic]". Searches PubMed/MEDLINE, Semantic Scholar, and OpenAlex (optionally ClinicalTrials.gov and medRxiv) following PRISMA 2020, Cochrane, and GRADE methodologies. Creates markdown documents with BibTeX references and verified citations. Do NOT trigger for: non-medical domains (software engineering, education, environmental science, social sciences, etc.) even if using review methodology vocabulary, formatting existing manuscripts, writing BibTeX cleanup scripts, drawing PRISMA diagrams in code, explaining database search methodology, explaining PRISMA/Cochrane/GRADE methodology without conducting a review, or brief factual summaries on medical topics when the user explicitly declines a structured review.
allowed-tools: Read Write Edit Bash Skill Agent WebFetch WebSearch mcp__litrev-mcp__search_pubmed mcp__litrev-mcp__search_s2 mcp__litrev-mcp__search_openalex mcp__litrev-mcp__fetch_abstracts mcp__litrev-mcp__process_results mcp__litrev-mcp__citation_chain mcp__litrev-mcp__deduplicate_results mcp__litrev-mcp__fetch_fulltext mcp__litrev-mcp__get_section mcp__litrev-mcp__extract_claims_regex mcp__litrev-mcp__verify_dois mcp__litrev-mcp__generate_bibliography mcp__litrev-mcp__audit_claims mcp__litrev-mcp__validate_gate mcp__litrev-mcp__import_corpus
---

# Literature Review — Orchestrator

## Pre-loaded pipeline state

### Working directory
!`pwd`

### Review artifacts found
!`ls -1 review/ 2>/dev/null || echo "(no review/ directory yet)"`

### Protocol (if exists)
!`head -30 review/protocol.md 2>/dev/null || echo "(no protocol yet)"`

### Git status of review/
!`git log --oneline -5 -- review/ 2>/dev/null || echo "(no git history for review/)"`

Sequence sub-skills and MCP tools into a complete literature review pipeline. Planning, sequencing, gates, and error recovery are handled here. Domain work is delegated to sub-skills (LLM reasoning) or MCP tools (deterministic execution).

## Pipeline

```
Planning → litrev-search → litrev-screen → Snowballing (MCP, optional) → litrev-extract → litrev-synthesize → Verification (MCP) → Final QC → Double Audit + Walkthrough → Pipeline Log
```

## Sub-skills and MCP tools

| Phase | Delegate | Purpose |
|-------|----------|---------|
| 2 | Skill `litrev-search` | Multi-database search + aggregation |
| 3a | Skill `litrev-screen` | Title / abstract screening (full-text retrieval available via `fetch_fulltext` + `get_section`) |
| 3b | MCP `citation_chain` + inline screening | Citation chaining (backward + forward) |
| 4 | Skill `litrev-extract` | Claim extraction + quality assessment |
| 5 | Skill `litrev-synthesize` | Constrained thematic writing |
| 6 | MCP `verify_dois` + `generate_bibliography` + `audit_claims` | Citation verification, BibTeX, claims audit |
| 8 | Agent `audit_fidelity` + Agent `audit_methodology` + `/review-walkthrough` | Factual + structural audit, interactive walkthrough |

Sub-skills can be invoked independently (standalone mode) or by this orchestrator (orchestrated mode). In orchestrated mode, sub-skills read their inputs from the conversation context and `review/` files — they do not re-ask the user for information already established.

## Invoking Sub-skills

Use the **Skill tool** to invoke each sub-skill by name (e.g., `skill: "litrev-search"`). The sub-skill loads its own SKILL.md and executes within the current conversation — it has access to the full conversation context and the `review/` directory. Do not attempt to read or execute sub-skill instructions directly; let the Skill tool handle loading.

## Execution Tracker

MANDATORY: Copy this tracker into your first message and update it as you complete each phase. Mark each gate as PASSED only after verifying ALL conditions listed.

If resuming a previous session, check `review/` for existing files and reconstruct tracker state before continuing (see Session Resumption).

```
- [ ] Phase 1 Planning
  - [ ] GATE 1: protocol printed (question, framework, scope, criteria, databases, search terms)
- [ ] Phase 2a Search (litrev-search)
- [ ] Phase 2b Import corpus (optional) — user-supplied BibTeX/RIS/CSV/TSV/PMIDs/DOIs
  - [ ] GATE 2: review/combined_results.json + review/search_results.md + review/search_log.md exist
- [ ] Phase 3a Screening (litrev-screen)
  - [ ] GATE 3a: review/screening_log.md + review/included_indices.json exist, PRISMA counts printed
- [ ] Phase 3b Snowballing (MCP + inline) — optional per review type
  - [ ] GATE 3b: Citation Snowballing section in screening_log.md with Status: COMPLETE
- [ ] Phase 4 Extraction (litrev-extract)
  - [ ] GATE 4: review/extracted_claims.json exists, summary table + quality ratings printed
- [ ] Phase 5 Synthesis (litrev-synthesize)
  - [ ] GATE 5: review/<topic>_review.md exists with all sections, BibTeX block present
- [ ] Phase 6 Verification (MCP tools)
  - [ ] GATE 6: review/references.bib + review/claims_audit.json exist, verification summary printed
- [ ] Phase 7 Final Quality Check
  - [ ] GATE 7: quality checklist printed, all items PASS
- [ ] Phase 8 Double Audit + Review Walkthrough
  - [ ] GATE 8: both audits complete, walkthroughs done, no unresolved critical, all major have status
- [ ] Phase 9 Pipeline Log (automatic, no gate)
  - [ ] review/pipeline_log.md written
```

## Setup

```bash
mkdir -p review
```

All output files go in `review/` under the current working directory. If `review/` already contains files, ask the user whether to resume an existing review or start fresh. When resuming, verify the topic in any existing `*_review.md` matches the current request — if mismatch, ask fresh-or-different-directory. Starting fresh requires explicit user confirmation, then: `rm -rf review && mkdir -p review`.

### MCP tool tips

When any MCP tool response contains a `"tips"` field, relay **one tip at a time** to the user and offer to configure it.
Example: "I notice Semantic Scholar API key isn't configured — this slows down citation chaining significantly. You can get a free key at [link]. Want me to set it up? Just paste the key and I'll add it to your config."
If the user provides the value, read `~/.claude/.mcp.json`, add or update the variable in the `litrev-mcp` server's `env` block, and write the file back. Then tell the user to restart Claude Code for the change to take effect. Note: keys may also be injected via the server's launch script (e.g., sourcing a secrets file) — the `tips` field in MCP tool responses is the authoritative signal for whether a key is missing, not the `.mcp.json` env block.
Do not prompt about the same variable twice in a session.

### Degraded-mode alerting

When any sub-skill or MCP tool reports degraded operation (missing API key, repeated HTTP 429s, database unreachable, partial query failures), the orchestrator must **stop and alert the user interactively** before continuing. Specifically:
1. State the issue clearly (e.g., "Semantic Scholar API key not received by MCP server")
2. State the impact on search coverage or result quality
3. Ask whether to (a) stop and fix the issue now, or (b) continue with degraded results
Never silently log a degradation and proceed — silent degradation leads to incomplete reviews that are only discovered downstream.

## Phase 1: Planning and Scoping

This is the only phase handled directly by the orchestrator (not delegated).

1. **Define Research Question** using the appropriate framework. Selection rule: use **PICO/PICOS** when the question is about an intervention or treatment effect; use **PEO** when investigating an exposure, risk factor, or etiology without an explicit intervention; use **SPIDER** for qualitative or mixed-methods questions. When a question straddles two frameworks, prefer PEO for etiological questions and PICO only when an explicit intervention is being evaluated.
   - **PICO/PICOS**: Population, Intervention, Comparison, Outcome (+Study design)
   - **PEO**: Population, Exposure, Outcome
   - **SPIDER**: Sample, Phenomenon of Interest, Design, Evaluation, Research type

2. **Establish Scope**: review type (systematic, scoping, narrative, meta-analysis, rapid), time period, geographic scope, study types. If the user requests an umbrella review (review of reviews), inform them this type is not yet supported and suggest a systematic review of primary studies instead.

3. **Develop Search Strategy**: 2-4 main concepts, synonyms/abbreviations, Boolean operators, minimum 3 databases (2 for rapid). If the user insists on fewer, warn that the search may be insufficient, document the limitation in the protocol, and proceed if they confirm.

4. **Set Inclusion/Exclusion Criteria**: date range, language, publication types, study designs

5. **Review type not specified?** Ask before proceeding. If the user's response does not map to one of the five review types (systematic, scoping, narrative, meta-analysis, rapid), default to narrative review and mention that the scope can be escalated later.

### === GATE 1 ===

Run MCP tool `validate_gate(gate="1", review_dir="review/")`. All checks must PASS before proceeding.

Print a protocol summary with: research question, framework (with each component filled), review type, time period, databases (>= 3, or >= 2 for rapid), search concepts with synonyms, inclusion criteria, exclusion criteria. Every field must be filled before proceeding.

**Persist the protocol**: write the protocol summary to `review/protocol.md` so it survives session boundaries. On session resumption, read `review/protocol.md` to restore the research question, framework, review type, criteria, and search strategy.

## Phase 2a: Search

Invoke `litrev-search` in orchestrated mode. The protocol from Phase 1 provides all required inputs.

## Phase 2b: Import corpus (optional)

If the user has bibliographic files to import (institutional database exports, hand-curated reference lists, or grey literature collections), merge them into the pipeline before Gate 2.

Ask the user: "Do you have any bibliographic files to import (BibTeX, RIS, Scopus CSV, Web of Science TSV, or lists of PMIDs/DOIs)? If so, provide the file path."

If the user provides a file:

1. Call the MCP tool `import_corpus(file_path=<path>, output_path="review/imported_results.json")`. The tool auto-detects the format, parses records, and enriches sparse entries (bare PMIDs/DOIs) with metadata from PubMed, CrossRef, and OpenAlex.
2. Read `review/imported_results.json` and `review/combined_results.json`, concatenate the two lists, and write the merged result back to `review/combined_results.json`.
3. Call `deduplicate_results(results_path="review/combined_results.json")` to remove duplicates introduced by the merge.
4. Log the import in `review/search_log.md`: format detected, records parsed, records after dedup, source file path.

If the user has multiple files, repeat step 1 for each file before merging.

If the user has no files to import, skip this phase and proceed to Gate 2.

### === GATE 2 ===

Run MCP tool `validate_gate(gate="2", review_dir="review/")`. All checks must PASS before proceeding.

If any check fails, the search phase did not complete — diagnose and re-invoke `litrev-search`.

#### Micro-audit 2 (systematic / meta-analysis only)

Quick quality check after search — skip for scoping, narrative, and rapid reviews.
- Do the executed queries cover all key concepts from the protocol (Population, Intervention/Exposure, Outcome)?
- Is the result ratio across databases balanced (no single DB contributing >80% of total results)?
- Are there failed searches that should be retried?

Print a 3-line summary: concepts covered (yes/partial), DB balance (balanced/skewed), action needed (none/retry X).

## Phase 3a: Screening

Invoke `litrev-screen` in orchestrated mode. Pass the inclusion/exclusion criteria from Phase 1.

### === GATE 3a ===

Run MCP tool `validate_gate(gate="3a", review_dir="review/")`. All checks must PASS before proceeding.

Print PRISMA counts. For systematic/meta-analysis/scoping: identified -> deduplicated -> title-screened -> abstract-screened -> included. For narrative/rapid (simplified): identified -> deduplicated -> screened -> included.

Zero-result detection: check `review/included_indices.json` — if empty array `[]`, screening returned zero articles. Do not proceed to Phase 3b — discuss with the user (broaden criteria, expand search, or report absence of evidence).

If the user chooses to report absence of evidence: skip Phases 3b, 4, and 6. Invoke `litrev-synthesize` (Phase 5) with the instruction to produce a short review documenting the null result — search strategy, screening outcome, and conclusion that no eligible studies were found. In Phase 7, mark items 1-4, 8, and 9 as N/A (no citations, no bibliography, no claims, no thematic organization needed).

If fewer than 5 articles are included, warn the user that the evidence base is thin before proceeding.

If more than 100 articles are included, warn the user that extraction and synthesis will be lengthy and may require multiple sessions. Suggest narrowing inclusion criteria or switching to a scoping/rapid review type to reduce the corpus.

#### Micro-audit 3a (systematic / meta-analysis only)

Quick quality check after screening — skip for scoping, narrative, and rapid reviews.
- Are exclusion reasons consistent with the protocol criteria (not ad-hoc)?
- Sample 3 excluded articles from `screening_log.md`: does each exclusion reason match one of the declared exclusion criteria?
- Is the inclusion rate plausible for the topic (typically 2-15% of screened articles)?

Print a 3-line summary: exclusion consistency (consistent/inconsistent), inclusion rate (N/M = X%), action needed (none/review exclusions).

## Phase 3b: Snowballing (optional)

Consult the review type routing table. For systematic and meta-analysis reviews, run snowballing automatically. For scoping, narrative, and rapid reviews, recommend it to the user and proceed only if they accept. When offering, specify the variant from the routing table (both directions for scoping, backward only for narrative, forward only capped at 5 seeds for rapid).

### Step 3b.1 — Select seed papers

Read `review/included_indices.json` and load corresponding records from `review/combined_results.json`.

Seed selection:
- If ≤10 included articles: use all as seeds (rapid reviews: cap at 5, pick highest citation count)
- If >10: select the 10 most relevant by citation count, then relevance to the research question, then recency. Present the selection and confirm with the user
- Each seed needs a DOI or PMID. Skip seeds without identifiers and warn the user if more than half lack them

### Step 3b.2 — Run citation chaining

Call the MCP tool `citation_chain` with:
- `results_path`: `"review/combined_results.json"`
- `indices`: list of 0-based seed indices
- `direction`: `"both"` (systematic/meta-analysis/scoping), `"backward"` (narrative), or `"forward"` (rapid)
- `sources`: `"s2,openalex"`
- `output_path`: `"review/chaining_candidates.json"`

The tool deduplicates candidates against existing results.

### Step 3b.3 — Screen candidates

Read `review/chaining_candidates.json`. Apply the same inclusion/exclusion criteria from the screening phase (from `review/screening_log.md` or conversation context).

This is a **single-pass combined screen** (title + abstract together). Snowball candidates are citation-adjacent to included studies, so they are more likely relevant. For each candidate: check exclusion criteria in order, exclude at first failure, include when in doubt.

If >50 candidates, screen in batches of 20 with a running tally.

### Step 3b.4 — Document and merge

Append a `## Citation Snowballing` section to `review/screening_log.md`:

```markdown
## Citation Snowballing

- **Date**: YYYY-MM-DD
- **Seed papers**: <count> (indices: <space-separated>)
- **Direction**: backward / forward / both
- **Sources**: Semantic Scholar, OpenAlex
- **Raw candidates found**: <count>
- **After deduplication (vs existing)**: <count>
- **Criteria applied**: <same criteria as original screening>

### Retained (<count>)

| Index | Title (truncated) | First Author (Year) | Source |
|-------|-------------------|---------------------|--------|
| — | Effect of probiotics... | Smith (2023) | S2-backward |

### Excluded (<count>)

| Title (truncated) | First Author (Year) | Reason |
|-------------------|---------------------|--------|
| Pediatric C. diff... | Jones (2020) | Pediatric population |

Status: COMPLETE
```

Then merge retained candidates:
1. Append retained candidates to `review/combined_results.json`
2. Call MCP `deduplicate_results` on `review/combined_results.json` as a safety net (should be a no-op if `citation_chain` deduplication worked correctly, but guards against index errors during manual merge)
3. Add new indices to `review/included_indices.json` (indices are the positions of appended candidates *after* dedup — re-identify them by DOI/title match, not by pre-dedup offset)
4. Overwrite `review/chaining_candidates.json` with only the retained candidates (the raw MCP output is no longer needed — screening decisions are documented in `screening_log.md`)

Print a snowballing summary: seeds → raw candidates → after dedup → screened → retained/excluded with top exclusion reasons.

### === GATE 3b ===

Run MCP tool `validate_gate(gate="3b", review_dir="review/")`. If snowballing was intentionally skipped (status FAIL with "N/A if intentionally skipped"), mark GATE 3b as N/A and proceed. Otherwise all checks must PASS. The gate verifies that the Citation Snowballing section contains both `### Retained` and `### Excluded` subsections — this ensures candidates were actually screened, not just bulk-included.

## Phase 4: Extraction

Invoke `litrev-extract` in orchestrated mode.

### === GATE 4 ===

Run MCP tool `validate_gate(gate="4", review_dir="review/")`. All checks must PASS before proceeding.

Additionally verify:
- Summary table was printed with columns: Author (Year), Design, N, Quality, Key Finding, Theme(s)
- Quality ratings and theme assignments are present (quality may be null for scoping reviews). See `litrev-extract` for quality assessment details per review type
- `stats` counts match actual array lengths (see litrev-extract Step 7)

#### Micro-audit 4 (systematic / meta-analysis only)

Quick quality check after extraction — skip for scoping, narrative, and rapid reviews.
- Sample 3 articles from `extracted_claims.json`: are claims specific (numbers, effect sizes, CIs) rather than vague summaries?
- Are quality ratings justified by study design and sample size (e.g., small uncontrolled study should not get "high" quality)?
- Do theme assignments reflect the actual claim content?

Print a 3-line summary: claim specificity (specific/vague), quality calibration (calibrated/over-rated/under-rated), action needed (none/re-extract N articles).

## Phase 5: Synthesis

Invoke `litrev-synthesize` in orchestrated mode. The sub-skill auto-detects skipped phases from `screening_log.md` (absence of `## Citation Snowballing` section) and includes required limitation disclosures (AI-assisted timeline, skipped phases).

### === GATE 5 ===

Run MCP tool `validate_gate(gate="5", review_dir="review/")`. All checks must PASS before proceeding.

The `<topic>` slug is determined by `litrev-synthesize`. The orchestrator detects existing review files by glob pattern `review/*_review.md`.

Additionally verify:
- YAML header declares `bibliography: references.bib` (the file itself is created in Phase 6 — do not check for its existence here)
- A `bibtex` fenced code block with draft reference entries (consumed by MCP `generate_bibliography` in Phase 6 to produce the authoritative `references.bib`)
- litrev-synthesize self-checks 1–9 all reported PASS (including blocking check #8: PICO outcome coverage, and check #9: no DOIs in BibTeX)

#### Micro-audit 5 (systematic / meta-analysis only)

Quick quality check after synthesis — skip for scoping, narrative, and rapid reviews.
- Sample 5 claims from `extracted_claims.json`: is each present (with preserved numbers) in the review text?
- Are there statements in the review with specific numbers that do NOT trace to any claim in `extracted_claims.json` (potential fabrication)?
- Do all PICO outcomes from the protocol have a corresponding section or subsection?

Print a 3-line summary: claim traceability (N/5 found), fabrication risk (none/N suspicious), PICO coverage (complete/missing: X).

## Phase 6: Verification

This phase uses MCP tools directly (no sub-skill invocation). Detect the topic slug from the existing `review/*_review.md` filename.

### Step 6.1 — Verify DOIs and PMIDs (Gate 6a)

Call the MCP tool `verify_dois` with:
- `review_path`: `"review/<topic>_review.md"`
- `check_retractions`: `true`
- `timeout`: `15`

Review the output report:
- **Verified DOIs**: no action
- **Failed DOIs**: search CrossRef by title, update the DOI in the review's BibTeX block. If no DOI exists, remove the `doi` field but keep the citation
- **Retracted publications**: flag to the user immediately. Ask whether to remove or keep with retraction notice — do NOT silently proceed

Re-run `verify_dois` after corrections until all resolvable DOIs pass (max 2 correction rounds per DOI). Print Gate 6a checkpoint: total DOIs, verified, failed, retracted.

### Step 6.2 — Generate bibliography (Gate 6b)

Call the MCP tool `generate_bibliography` with:
- `review_path`: `"review/<topic>_review.md"`
- `output_path`: `"review/references.bib"`
- `timeout`: `15`

Review cross-verification output (OK / MISMATCH / MISSING / EXTRA). Fix mismatches in the review's BibTeX block and re-run if needed (max 2 re-runs).

After generation, cross-check citation keys used in text (`[@Key]`) against keys in `review/references.bib`. For keys cited but absent (no DOI → tool couldn't resolve), copy the entry from the review's embedded BibTeX block into `review/references.bib`.

Print Gate 6b checkpoint: entries generated, mismatches, missing, extras.

### Step 6.3 — Audit claims (Gate 6c)

Call the MCP tool `audit_claims` with:
- `review_path`: `"review/<topic>_review.md"`
- `claims_path`: `"review/extracted_claims.json"`
- `output_path`: `"review/claims_audit.json"`

Review the audit report:
- **VERIFIED**: confirmed in abstract with matching context — no action
- **LABEL_UNCERTAIN**: number found in abstract but context words differ — verify that the predictor/label in the review matches the source. Fix misattributions before proceeding
- **UNVERIFIED**: check for `<!-- UNVERIFIED: ... -->` comment (expected if from full-text). Otherwise, verify against source abstract — fix or remove hallucinated claims
- **NO_ABSTRACT**: needs manual full-text verification
- **NO_EXTRACTION**: key mismatch — check key resolution
- Claims flagged `multi_citation: true` have ambiguous attribution (sentence cites >1 source) — verify which source the number belongs to

After corrections, re-run `audit_claims`. Print Gate 6c checkpoint: total claims, verified, label_uncertain, unverified, no-abstract, no-extraction.

### === GATE 6 ===

Run MCP tool `validate_gate(gate="6", review_dir="review/")`. All checks must PASS before proceeding.

Additionally verify that the verification summary was printed (DOIs verified/failed, claims verified/unverified).

## Phase 7: Final Quality Check

Print each item and mark PASS or FAIL. If any item is FAIL, fix it using the corrective action below. If not resolved after 2 attempts (2 distinct corrective actions), mark FAIL (UNRESOLVABLE), document the reason, and proceed.

Corrective actions by item:
- Items 1-3: re-run the relevant MCP tool (`verify_dois`, `generate_bibliography`, or `audit_claims`)
- Item 4: edit `review/<topic>_review.md` directly (fix citation syntax)
- Items 5-7: edit `review/<topic>_review.md` directly (add missing sections)
- Item 8: re-invoke `litrev-synthesize` (restructure results), then re-run Phase 6 (verify_dois + generate_bibliography + audit_claims) since the review document changed
- Item 9: re-invoke `litrev-extract` (redo quality assessment), then re-run audit_claims since extracted_claims.json changed
- Item 10: edit `review/<topic>_review.md` directly (add limitations)

```
1. All resolvable DOIs verified?                            [PASS/FAIL]
2. references.bib exists and referenced in YAML header?     [PASS/FAIL]
3. Claims audit completed, hallucinated claims fixed?       [PASS/FAIL]
4. Citations use consistent Pandoc syntax?                  [PASS/FAIL]
5. PRISMA flow documented?                                  [PASS/FAIL or N/A]
6. Search methodology fully documented?                     [PASS/FAIL]
7. Inclusion/exclusion criteria clearly stated?             [PASS/FAIL]
8. Results organized thematically (not study-by-study)?     [PASS/FAIL]
9. Quality assessment completed?                            [PASS/FAIL or N/A]
10. Limitations acknowledged?                               [PASS/FAIL]
```

### === GATE 7 ===

Run MCP tool `validate_gate(gate="7", review_dir="review/")`. All checks must PASS before proceeding.

## Phase 8: Double Audit + Review Walkthrough

Post-GATE 7 quality assurance. Two independent audits run in parallel, each followed by an interactive walkthrough with the user.

### Step 8.1 — Run both audits in parallel

Launch two agents simultaneously using the Agent tool:

1. **Fidelity audit**: Agent reads `agents/audit_fidelity.md` instructions. Reads `review/extracted_claims.json`, `review/claims_audit.json`, `review/references.bib`, `review/combined_results.json`, `review/protocol.md`. Writes `review/audit_fidelity.md`.

2. **Methodology audit**: Agent reads `agents/audit_methodology.md` instructions. Reads `review/*_review.md`, `review/protocol.md`, `review/extracted_claims.json`, `review/screening_log.md`. Writes `review/audit_methodology.md`.

Prompt each agent with:
```
Read the agent instructions at agents/<agent_file>.md, then execute the audit on the review/ directory in the current working directory. Write the report to review/<output_file>.md.
```

Both agents run in the background (parallel). Wait for both to complete before proceeding.

### Step 8.2 — Deduplicate findings across audits

Before walkthroughs, read both reports and check for overlapping findings:
- Same underlying issue flagged by both audits (e.g., grey literature gap appears as coverage issue in A and undisclosed limitation in B)
- Cross-reference by article key or section

For overlaps: keep the finding in the audit where it fits best, add a cross-reference note in the other (e.g., "See also F-FID-16" or "See also F-MET-03"). Do not present the same issue twice in walkthroughs.

### Step 8.3 — Interactive walkthroughs (sequential)

Run walkthroughs sequentially — they are interactive and require user decisions.

**Walkthrough A**: Invoke `/review-walkthrough` on the Audit A report. The user decides for each finding:
- **ACCEPTED**: fix is applied immediately
- **NOTED**: acknowledged, no action needed
- **DEFERRED**: postponed with justification, recorded in `review/DEFERRED.md`
- **REJECTED**: finding is invalid, with justification

**Walkthrough B**: Same process on the Audit B report.

After each walkthrough, update the corresponding audit report with decision annotations if needed.

### Step 8.4 — Record deferred findings

Create or update `review/DEFERRED.md` with all DEFERRED findings:

```markdown
# Deferred Findings

| Date | Finding | Files affected | Reason | Deadline |
|------|---------|---------------|--------|----------|
| YYYY-MM-DD | F-XXX: description | file1, file2 | reason for deferral | condition or date |
```

### === GATE 8 ===

Run MCP tool `validate_gate(gate="8", review_dir="review/")`. All checks must PASS before proceeding.

Additionally verify:
4. Every MAJOR finding has an explicit status (ACCEPTED, NOTED, or DEFERRED with justification)
5. If any findings were DEFERRED, `review/DEFERRED.md` exists

MINOR findings do not block GATE 8 — they may be left without action.

If GATE 8 fails on criterion 3 (unresolved critical): the user must address the critical finding before proceeding. Offer to apply the recommended fix.

## Phase 9: Pipeline Log

Automatic, no gate. Write `review/pipeline_log.md` summarizing the entire pipeline run. This file documents how the review was produced and serves as a benchmark for future runs.

Compute all metrics from `review/` files and conversation context. Use the following template:

```markdown
# Pipeline Log — <Topic>

- **Date**: YYYY-MM-DD
- **Topic**: <one-line description>
- **Review type**: <type> (<guideline>)
- **Framework**: <PEO/PICO/SPIDER>
- **Working directory**: <path>

## Funnel Metrics

| Stage | N | Ratio |
|-------|---|-------|
| Identified | <from combined_results.json length> | — |
| After title screening | <from screening_log.md> | % |
| After abstract screening | <from screening_log.md> | % |
| Included | <from included_indices.json length> | % |
| With claims | <from extracted_claims.json> | % of included |
| Quantitative claims | <from extracted_claims.json stats> | per article |
| Semantic claims | <from extracted_claims.json stats> | per article |
| Articles cited in synthesis | <count unique [@Key] in review> | % of included |
| Themes | <from extracted_claims.json> | — |

## Gate Log

| Gate | Status | Notes |
|------|--------|-------|
<one row per gate, with PASSED/FAILED/N-A and any notable issues>

## User Decision Points

| Point | Options | Choice | Rationale |
|-------|---------|--------|-----------|
<decisions where the user was asked to choose>

## Corrections Applied

### Critical
<table: finding, issue, fix>

### Major
<table: finding, issue, fix>

### Minor
<count accepted, count noted, key fixes>

## MCP Tool Issues

| Tool | Issue | Severity | Workaround |
|------|-------|----------|------------|
<any MCP tool failures or unexpected behavior>

## Timing

| Phase | Duration | Notes |
|-------|----------|-------|
<approximate duration per phase, derived from conversation timestamps>

## Output Files

| File | Size | Content |
|------|------|---------|
<ls -la review/ formatted as table>

## Run-Specific Notes

Factual observations specific to this run — anomalous funnel ratios, unexpected behaviors, or notable decisions. Not generalized recommendations (those belong in memory via Step 9b).

Categories:
- Anomalous ratios (e.g., "only 4.8% of included articles cited in synthesis")
- Phase bottlenecks (e.g., "extraction took 20 min, synthesis hit rate limit")
- User decisions that could become defaults in future runs
```

Populate each section from:
- **Funnel Metrics**: read `combined_results.json` (length), `included_indices.json` (length), `extracted_claims.json` (stats), count `[@` citations in `*_review.md`
- **Gate Log**: from the execution tracker maintained during the conversation
- **User Decision Points**: from conversation context (decisions where the user chose between options)
- **Corrections**: from walkthrough decisions in Phase 8
- **MCP Tool Issues**: from any tool errors encountered during the pipeline
- **Timing**: approximate durations from conversation timestamps (message creation times between phase boundaries). File timestamps are unreliable — files updated across multiple phases reflect only the last write
- **Output Files**: `ls -la review/`
- **Run-Specific Notes**: from conversation context — anomalous observations, bottlenecks, notable user decisions

### Step 9b — Update memory with pipeline learnings

After writing `pipeline_log.md`, automatically check whether the run produced observations that are **not already documented** in the litrev memory files. Memory accumulates under the current project context — locate the relevant files via glob:
- `~/.claude/projects/*/memory/feedback_litrev_extraction_patterns.md`
- `~/.claude/projects/*/memory/project_mcp_bugs_*.md`

**New MCP bugs**: if the MCP Tool Issues section of `pipeline_log.md` contains a bug not already documented in `project_mcp_bugs_*.md`, append it to the existing file or create a new one if no file exists.

**New quality patterns**: if the Corrections section reveals a recurring synthesis quality issue (DOI fabrication, causal language, missing confrontation, undocumented deviation, etc.) not already in `feedback_litrev_extraction_patterns.md`, append the pattern using the existing format (issue description, **Why:**, **How to apply:**).

**Do not duplicate**: if a bug or pattern is already covered by an existing entry, skip it — even if the specific instance is slightly different. Only add genuinely new patterns that will recur in future runs.

**Do not ask**: persist directly and report what was written (e.g., "Memory updated: 1 new MCP bug (audit_claims timeout), 1 new quality pattern (geographic coverage gap)" or "No new patterns — all issues already documented").

## Review Type Routing

Each sub-skill handles its own adaptations internally. The orchestrator's role is to route correctly:

| Review Type | Databases | Screening | Snowballing | Quality | PRISMA |
|-------------|-----------|-----------|-------------|---------|--------|
| Systematic | >= 3 | Title + Abstract + Full-text | Automatic (both) | Full (RoB/GRADE) | Full PRISMA 2020 |
| Meta-analysis | >= 3 | Title + Abstract + Full-text | Automatic (both) | Full (RoB/GRADE) | Full PRISMA 2020 |
| Scoping | >= 3 | Title + Abstract + Optional FT | User opt-in (both) | Optional (PRISMA-ScR) | PRISMA-ScR |
| Narrative | >= 2 | Title + Abstract + Optional FT | User opt-in (backward only) | Simplified | Simplified |
| Rapid | >= 2 | Combined title/abstract | User opt-in (forward, cap 5) | Simplified | Simplified |

Gate adjustments by review type:
- **Gate 3b**: N/A when snowballing is skipped
- **Gate 4 quality**: may be null for scoping reviews
- **Gate 5 PRISMA**: simplified flow acceptable for narrative/rapid
- **Gate 7 items 5 and 9**: N/A where indicated above

## Session Resumption

When `review/` already contains files, reconstruct the pipeline state:

| File | Indicates |
|------|-----------|
| `protocol.md` | Gate 1 passed — read to restore research question, framework, review type, criteria, search strategy |
| `combined_results.json` | Gate 2 input ready |
| `search_results.md` + `search_log.md` | Gate 2 passed |
| `screening_log.md` (check for `Status: COMPLETE` on each section) | Gate 3a progress |
| `included_indices.json` | Gate 3a passed |
| `chaining_candidates.json` (without `## Citation Snowballing` + `Status: COMPLETE` in screening_log) | Phase 3b in progress — verify that `chaining_candidates.json` seed indices match current `included_indices.json` (compare the `seed_indices` field in the file header, if present, against the current included set). If they diverge, delete `chaining_candidates.json` and re-run `citation_chain`. Otherwise screen candidates in this file (Step 3b.3), do not re-run `citation_chain` |
| `screening_log.md` with `## Citation Snowballing` + `Status: COMPLETE` | Gate 3b passed |
| `extracted_claims.json` | Gate 4 passed |
| `*_review.md` (glob `review/*_review.md`) | Gate 5 in progress or passed (check for all sections). If missing required sections, re-invoke `litrev-synthesize` — it detects existing files and resumes. If multiple files match, ask the user which to use. |
| `references.bib` | Gate 6 partially passed (bibliography generated) |
| `claims_audit.json` + `*_review_citation_report.json` | Gate 6 passed (all three outputs present) |
| `audit_fidelity.md` | Gate 8 fidelity audit complete (check for walkthrough decisions) |
| `audit_methodology.md` | Gate 8 methodology audit complete (check for walkthrough decisions) |
| `DEFERRED.md` | Gate 8 walkthroughs done (deferred findings recorded) |
| `pipeline_log.md` | Phase 9 complete (pipeline fully documented) |

Resume from the first incomplete gate. Tell the user which phases are already done.

## Error Recovery

If a sub-skill fails:

1. **Missing input file**: identify which upstream phase produces the missing file (see Interface Contracts below) and re-run that phase
2. **Gate not passed**: re-invoke the sub-skill for that phase — do not skip the gate
3. **Zero results at screening**: discuss with the user (broaden criteria, expand search, or report absence)
4. **API failures during search/verify**: the sub-skills handle retries internally — if still failing, document the failure and ask the user whether to proceed with partial results or retry later
5. **MCP tool not found or connection error**: the `litrev-mcp` server is not connected in this session. Tell the user to restart Claude Code so the MCP server is loaded from `~/.claude/.mcp.json`. Do not attempt to replicate MCP tool logic manually — the tools depend on rate-limited API clients and deduplication state that cannot be reproduced inline

## Interface Contracts

| Delegate | Reads | Writes |
|----------|-------|--------|
| Skill `litrev-search` | Protocol from conversation | `combined_results.json`, `search_results.md`, `search_log.md` |
| Skill `litrev-screen` | `search_results.md`, `combined_results.json`, criteria | `screening_log.md`, `included_indices.json` |
| MCP `citation_chain` | `combined_results.json`, seed indices | `chaining_candidates.json` |
| Orchestrator (3b inline) | `chaining_candidates.json`, criteria | updates `combined_results.json`, `included_indices.json`, `screening_log.md` |
| Skill `litrev-extract` | `combined_results.json`, `included_indices.json` | `extracted_claims.json` |
| Skill `litrev-synthesize` | `extracted_claims.json`, `screening_log.md`, `search_results.md`, `combined_results.json`, `protocol.md` (optional) | `<topic>_review.md`, `vancouver.csl` |
| MCP `verify_dois` | `<topic>_review.md` | `<topic>_review_citation_report.json` |
| MCP `generate_bibliography` | `<topic>_review.md` | `references.bib` |
| MCP `audit_claims` | `<topic>_review.md`, `extracted_claims.json` | `claims_audit.json` |
| Agent `audit_fidelity` | `extracted_claims.json`, `claims_audit.json`, `references.bib`, `combined_results.json`, `protocol.md` | `audit_fidelity.md` |
| Agent `audit_methodology` | `<topic>_review.md`, `protocol.md`, `extracted_claims.json`, `screening_log.md` | `audit_methodology.md` |
| Orchestrator (8.4 inline) | Walkthrough decisions | `DEFERRED.md` |
| Orchestrator (Phase 9) | All `review/` files, conversation context | `pipeline_log.md` |

## Output Files

- `review/protocol.md` — persisted protocol (question, framework, review type, criteria, search strategy)
- `review/<topic>_review.md` — main review document
- `review/references.bib` — BibTeX bibliography
- `review/combined_results.json` — aggregated search results
- `review/search_results.md` — ranked search results table
- `review/search_log.md` — search documentation
- `review/screening_log.md` — screening decisions
- `review/abstracts_for_screening.md` — fetched abstracts for screening (Phase 3a)
- `review/included_indices.json` — included article indices
- `review/extracted_claims.json` — structured claims + quality + themes
- `review/claims_audit.json` — claims cross-verification report
- `review/<topic>_review_citation_report.json` — citation verification report
- `review/vancouver.csl` — citation style file
- `review/audit_fidelity.md` — factual audit report (claims vs sources)
- `review/audit_methodology.md` — structural audit report (synthesis critique)
- `review/DEFERRED.md` — deferred findings with justifications (created only if deferrals exist)
- `review/pipeline_log.md` — pipeline run report (funnel metrics, gate log, corrections, MCP issues)
