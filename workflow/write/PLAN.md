# PLAN — Skill `/workflow:write`

> Plan vivant du skill `write` (plugin `workflow`, marketplace `hebstr`). FR/EN uniquement, mode bilingue FR↔EN. Le CHANGELOG marketplace suit le versioning par plugin ; pas de tag interne dans le frontmatter SKILL.md.

## Items ouverts

- [ ] Tester mode bilingue FR↔EN sur 2e registre marketing (release note autre que landing produit, ou README produit) pour confirmer la note slogans-titres et l'allowlist hors registre MDN/landing
- [ ] Confirmer ou infirmer tics #27 (« capacité à » + Vinf), #28 (« acteur » mot-valise), #29 (« le caractère X de Y ») sur 2 corpus FR business-tech long-form supplémentaires. Corpus actuels : ANSSI + Frenchweb (Session 4). NB : ces 3 tics sont en **extended** (#15, #16, #17 de la section "Tics IA secondaires"), pas en core.
- [ ] Distiller règle « pas de triplet/binôme symétrique vide » dans `~/.claude/CLAUDE.md` si 3e corpus FR pur la confirme. Corpus actuels : ANSSI ✓, Frenchweb ✓, Scaleway ✗ (FR coupé). Pas EN.
- [ ] Étendre allowlist tech FR↔EN si futurs tests bilingues font dériver : `cycle de vie` (déjà ajouté en Session 4), `worker`, `event-driven` (idiome FR : « piloté par les évènements »), `polyfill`

## Décisions à préserver (ne pas relitiger)

- **Académie française rejetée.** Sources retenues : TLFi (cnrtl.fr), Le Grevisse, Riegel-Pellat-Rioul (*Grammaire méthodique du français*), *Lexique des règles typographiques en usage à l'Imprimerie nationale*, Lacroux *Orthotypographie*. Étalons empiriques : Bortzmeyer, sebsauvage, Maître Eolas, blogs OCTO/Sfeir/Doctolib engineering.
- **Français de France (`fr_FR`), pas québécois.** Pas de croisade anti-anglicismes.
- **Anglicismes techniques idiomatiques préservés** : framework, runtime, deploy, debug, push, ship, refactor, mock, scope, log, parser, build, embedding, pipeline, stack, commit, merge, rollback, prompt, token, backend, frontend, benchmark, lifecycle, payload, binding.
- **Verbes corporate francisés à traduire** : leverager, actionner, onboarder, scaler (en métaphore), pusher (une idée), driver, challenger.
- **Calques structurels à traduire** : adresser un problème, supporter une feature, définitivement (au sens *certainly*), ça fait du sens, compléter une tâche, en charge de.
- **Pas de tiret cadratin (`—`) ni demi-cadratin (`–`)** comme ponctuation interne en FR. Demi-cadratin OK pour plages numériques (`5–15 %`).
- **Skill reste un skill.** La référence FR (~924 lignes) ne va pas dans `~/.claude/CLAUDE.md`. Seuls ~10 essentiels distillés sous `## Prose hygiene` y sont always-on.
- **Pas de support chinois.** Décision Session 3. Le skill ne couvre que EN et FR.
- **Écriture inclusive en FR (utilisateur·ice·s)** = choix éditorial du source, jamais dérive de traduction.

## Référents techniques

- Source canonique : `workflow/write/` dans ce repo (suivi en git, marketplace `hebstr`)
- Installation : `claude plugin install workflow@hebstr`
- `workflow/write/SKILL.md` : routage FR/EN, mode bilingue FR↔EN, mode release note. Invocation explicite uniquement via description (convention `workflow:*` description-only).
- `workflow/write/references/write-fr-core.md` : référence FR core, 234 lignes, 19 règles cross-registre + 12 tics IA principaux, always-loaded en mode FR
- `workflow/write/references/write-fr-extended.md` : référence FR étendue, 680 lignes, faux amis complet + corporate-tone + typographie rare + dé-listification, on-demand
- `workflow/write/references/write-en.md` : référence EN, single-file
- `~/.claude/memory/feedback_french_prose.md` : décisions méta persistées
- `~/.claude/CLAUDE.md` section `## Prose hygiene` : ~10 essentiels always-on
