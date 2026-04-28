---
name: write
description: "Invoke ONLY when the user explicitly types `/workflow:write` — do not auto-trigger on mentions of 'draft', 'edit', 'proofread', 'polish', 'rewrite', 'sound natural', or French equivalents ('écris', 'rédige', 'relis', 'corrige', 'polis', 'dégraisse', 'retravaille'). Strips AI writing patterns and rewrites prose to sound natural in English or French. Not for code comments, commit messages, or inline docs."
metadata:
  version: "3.24.0-fr"
---

# Write: Cut the AI Taste

Strip AI patterns from prose and rewrite it to sound human. Do not improve vocabulary; remove the performance of improvement.

## Pre-flight

1. **Text present?** If the user gave only an instruction with no actual prose to edit, ask for the text in one sentence. Do not proceed.
2. **Audience locked?** If the intended audience is unclear and cannot be inferred from the text (blog reader vs RFC vs email), ask before editing. Junior engineer and senior architect prose should read completely different.
3. **Reference file selection: language detected from the text being edited**, not the user's command. (Mode selection is separate — see Bilingual Review Mode for command-keyword triggers.)
   - Contains French (accented chars éèêëàâäîïôöùûüÿç + common French function words: le/la/les/des/un/une/et/est/dans/pour/avec/qui/que/ne/pas/sont/aux/cette/ces) → load `references/write-fr.md`
   - Otherwise → load `references/write-en.md`

   When the text mixes French and English (e.g. French prose with English code identifiers, or a bilingual doc), French wins if the running prose is in French. English code, terms, and inline tokens inside French prose do not flip the routing. Anglicisms idiomatic to French technical prose (framework, deploy, debug, push, ship, refactor, etc.) are part of French and do not flip the routing.

Read the loaded reference file in full before editing. If a single `Read` call hits the token limit (write-fr.md is large enough to trigger this), paginate via `offset`/`limit` until the file is fully read — do not proceed on a partial read. No summary, no commentary, no explanation of changes unless explicitly asked.

## Hard Rules

- **Meaning first, style second.** If removing an AI pattern would change the author's intended meaning, keep the original.
- **No silent restructuring at the document level.** Do not reorganize headings, reorder paragraphs, or merge top-level sections unless structural changes are explicitly requested. Register-level reformatting within a block (e.g. list → prose conversion per the reference files) is in scope.
- **Stop after output.** Deliver the rewritten text. Do not append a list of changes, a justification, or a closer.
- **Code passes through.** Fenced code blocks, inline backticks, file paths, command lines, and identifiers (variable names, function names, options) are data, not prose. Do not rewrite their content. Edit only the prose around them.

## Bilingual Review Mode (FR ↔ EN)

Within an explicit `/workflow:write` invocation, switch to this mode when the input is mixed French/English text or the user mentions "bilingual consistency", "release notes", "version FR/EN", or "traduction parallèle". These are mode selectors, not invocation triggers — the skill itself only fires on `/workflow:write`.

**French typography** (Lexique IN, Lacroux ; full rules in `references/write-fr.md`):
- Non-breaking space before `:`, `;`, `!`, `?`, `»`; after `«`. Absent in EN, so do not propagate EN spacing into FR.
- Quotation marks: `« »` in FR with non-breaking space inside, `" "` in EN. Do not leave `" "` in FR prose.
- No em-dash (—) or en-dash (–) as internal punctuation in either language. EN/DE typography accepts them, but `references/write-en.md` and `references/write-fr.md` both remove them as an AI register tell. Convert to commas, colons, parentheses, or restructure.
- Capitales accentuées obligatoires (État, École). Title case is EN-only ; FR titles capitalise only the first word + proper nouns.
- Decimals: comma in FR (`3,14`), period in EN (`3.14`). Thousands: thin non-breaking space in FR, comma in EN.

**Faux amis and calques to flag** (the EN word survives translation but means something else in FR):

| EN source | Wrong FR | Correct FR |
|---|---|---|
| digital | digital (anatomical sense only) | numérique |
| to support (a feature) | supporter | prendre en charge, gérer |
| to address (a problem) | adresser | traiter, prendre en charge |
| definitely (= certainly) | définitivement (= permanently) | certainement, vraiment |
| eventually (= in the end) | éventuellement (= possibly) | finalement, à terme |
| actually (= in fact) | actuellement (= currently) | en fait, en réalité |
| consistent | consistant (= thick, substantial) | cohérent, régulier |
| to complete (a task) | compléter (= to fill in) | terminer, achever |
| to figure out | figurer | comprendre, déterminer |
| in charge of | en charge de | chargé de, responsable de |
| it makes sense | ça fait (du) sens | c'est cohérent, ça se tient |

**Preserved anglicisms in FR technical prose** (do NOT "translate back" when reviewing FR↔EN parity): framework, runtime, deploy, debug, push, ship, refactor, mock, scope, log, parser, build, embedding, pipeline, stack, commit, merge, rollback, prompt, token, backend, frontend, benchmark, lifecycle, payload, binding. These are part of FR technical register; flagging them as untranslated is a false positive.

**Canonical FR translations to recognise** (do NOT flag as calque, do NOT drift to a creative synonym): `lifecycle → cycle de vie` (drifting to "parcours" loses the technical concept), `payload → charge utile`, `binding → liaison`, `thread → fil` (only if FR uses fil ; "thread" stays in FR tech is also correct).

**Inclusive writing in FR (utilisateur·ice·s, lecteur·rice·s)**: editorial choice of the source, not a translation drift. Do not "fix" inclusive forms when reviewing parity ; flag only if asked to normalise the register.

**Bilingual pairs**: confirm EN and FR convey the same propositional content. Marketing puff that survives translation in both directions is a translation-loss signal ; flag it. Common drift: EN keeps a clean nominal phrase, FR reaches for a verbose verbal construction (or vice versa). Length divergence > 25% per paragraph is worth a second look.

**Translation-loss vs structural asymmetry.** When paragraph length diverges, distinguish two cases. *Translation-loss* : the translated paragraph genuinely says less (a qualifier, a clause, a fact is missing). Flag and propose restoration. *Structural asymmetry* : the content is preserved elsewhere on the page (bullet-list, sibling section, sidebar) and the prose paragraph deliberately stops earlier in one language. Editorial choice — do not request restoring the cut content. Test : grep the missing facts in the rest of the page before flagging. Marketing landing pages and product recaps routinely move feature lists from prose into bullets in one language only ; treat as asymmetry, not loss.

**Output format for this mode.** Return both edited versions in their original order (FR then EN, or EN then FR), separated by a horizontal rule. Parity issues that require author judgment (faux amis, translation-loss, length divergence > 25%) go inline as `[FR↔EN: brief note]` next to the affected sentence. No trailing summary, no separate "Issues" section.

## Output

Return only the edited prose. No wrapper, no preamble, no postscript.
