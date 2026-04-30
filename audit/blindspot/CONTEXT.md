# blindspot — Context & Design Rationale

## Origin

Conversation du 2026-03-30.
Problème identifié en voulant reviewer skill-adversary avec skill-adversary lui-même : biais circulaire d'auto-référence.

## Le problème

Tout skill d'audit (skill-adversary, mcp-adversary, critical-code-reviewer, sweep…) est susceptible d'auditer un artefact produit par un système de la même famille — y compris lui-même.

Le terme académique est **"self-preference bias"** (Panickssery et al., 2024, arXiv: 2404.13076).
Les LLMs reconnaissent et favorisent systématiquement leurs propres outputs, même à qualité contrôlée.

### Mécanismes documentés

- **Fingerprint stylistique** : le juge reconnaît "sa" distribution de tokens
- **Biais RLHF partagé** : générateur et juge ont la même notion de "bon output"
- **Accord sycophantique** : tendance à valider le contenu présenté plutôt qu'à le critiquer
- **Watermarking implicite** : les modèles détectent les signatures statistiques de leur propre génération

### Consensus académique

Le biais ne peut pas être entièrement éliminé quand juge et sujet partagent la même distribution d'entraînement.
Toutes les mitigations le réduisent sans le supprimer.

### Références clés

| Papier | Contribution |
|--------|-------------|
| Zheng et al. (2023), arXiv: 2306.05685 | LLM-as-a-Judge, positional/verbosity/self-enhancement bias |
| Panickssery et al. (2024), arXiv: 2404.13076 | LLMs reconnaissent et favorisent leurs propres outputs |
| Liu et al. (2023), arXiv: 2303.16634 | G-Eval, circularité GPT-4 évaluant GPT-4 |
| Huang et al. (2024), arXiv: 2310.01798 | LLMs ne peuvent pas auto-corriger leur raisonnement sans vérité externe |
| Xu et al. (2024), "Perils of Self-Feedback" | Les boucles d'auto-raffinement dégradent la qualité quand les angles morts sont partagés |
| Verga et al. (2024), "Replacing Judges with Juries" | Panel de juges diversifiés comme mitigation |

## Mitigations connues (par efficacité décroissante)

| Stratégie | Efficacité | Notes |
|-----------|-----------|-------|
| Cross-model evaluation (famille différente) | Forte | Le plus efficace, largement adopté |
| Panel of judges (jury de LLMs diversifiés) | Forte | Verga et al. 2024 |
| Calibration avec labels humains | Forte mais coûteuse | Chatbot Arena |
| Reference-based judging (réponse gold) | Modérée-forte | G-Eval, MT-Bench |
| Rubric-based evaluation (grille fixe) | Modérée | Réduit mais n'élimine pas |
| Context isolation | Modérée | Déjà dans skill-adversary |
| Metamorphic testing | Modérée | Entrées équivalentes, vérifier cohérence |
| Adversarial evaluation sets | Modérée | Construire des cas exploitant les biais connus |
| Persona/role forcing | Faible-modérée | Déjà dans skill-adversary |
| Self-consistency checks (temperature > 0) | Faible-modérée | Flaguer les scores à haute variance |

## État de l'art communauté Claude Code

Aucun skill de meta-review de skills n'existe. Niche inoccupée.

Patterns proches :
- **ARIS** (4.8k stars) : boucles cross-model, mais pour la recherche
- **ai-pair** (145 stars) : "one creates, two review" avec Claude + Codex + Gemini
- **Ring** (155 stars) : 7 reviewer agents distincts, mais pour du code
- **flow-next** (554 stars) : multi-model review gates via Codex CLI

## Concept retenu

### Nom : `blindspot`

### Rôle

Orchestrateur circularité-aware pour skills d'audit.
Ne remplace aucun skill d'audit — s'interpose quand le risque circulaire est détecté.

### Architecture V1 (implémentée 2026-03-30)

#### Flow

1. **Phase 0 — Détection de circularité** : compare le chemin de la cible avec le répertoire du skill d'audit (path overlap) et vérifie si le modèle juge et le modèle auteur partagent la même famille (model family overlap). Produit un verdict : Strong circularity, Model circularity, ou No circularity.
2. **Phase 1 — Routage cross-model** : si circularité détectée et `OPENROUTER_API_KEY` disponible, lance un agent cross-model-judge qui route l'audit vers un modèle non-Claude (défaut : `google/gemini-2.5-pro`) via OpenRouter API. Sinon, fallback avec warning.
3. **Phase 2 — Rapport transparent** : compile les findings des deux modèles avec une analyse de convergence (agreed / Claude-only / external-only) et un bloc de transparence obligatoire.

#### Décisions d'implémentation

| Décision | Justification |
|----------|--------------|
| OpenRouter only (pas de cascade CLI) | Une seule clé API, un seul chemin de code, choix du modèle, stabilité vs CLI tools jeunes |
| 1 seul agent (cross-model-judge) | Le rapport est compilé par SKILL.md directement — pas besoin d'agent dédié |
| Pas de devil's advocate (V2) | Scope minimal V1 |
| Pas de rubric forcing (V2) | Scope minimal V1 |
| Model family = toujours circulaire dans Claude Code | Le revieweur est toujours Claude — simplifie la logique |
| Fallback = audit normal + warning détaillé | Le skill reste utile même sans clé OpenRouter |
| Convergence analysis comme signal principal | Les findings "external-only" sont les blindspot candidates |

#### Structure

```
blindspot/
├── CONTEXT.md              (ce fichier)
├── SKILL.md                (orchestration, détection, routage, rapport)
├── agents/
│   └── cross-model-judge.md    (routeur OpenRouter → modèle externe)
└── evals/
    ├── evals.json              (9 cas fonctionnels, schéma skill-creator)
    └── trigger_eval.json       (20 queries triggering, format run_loop.py)
```

### Scope V2 (extensions possibles)

- Rubric forcing automatique (grille fixe imposée au skill d'audit)
- Devil's advocate agent (challenge les findings trop indulgents)
- Panel de juges (plusieurs modèles OpenRouter, agrégation Verga et al.)
- Intégration avec task-observer pour feedback de terrain
- Auto-détection de circularité dans les autres skills (hook sur skill-adversary, sweep)

### Cas d'usage concrets

- skill-adversary review skill-adversary
- mcp-adversary review le MCP d'ouroboros (qu'il utilise)
- sweep review le repo de sweep
- critical-code-reviewer review son propre code

### Triggering : invocation explicite uniquement

Testé avec skill-creator `run_loop.py` le 2026-03-30 : recall=0% sur 10 should-trigger queries.
Le skill ne se déclenche jamais implicitement via la description seule.

C'est un comportement attendu et assumé :
- blindspot est un orchestrateur meta — il n'a de sens que quand l'utilisateur sait qu'il existe et l'invoque volontairement
- Le triggering implicite serait même contre-productif : intercepter un `skill-adversary` normal sans que l'utilisateur ait exprimé de concern de circularité serait intrusif
- L'optimisation de description via `run_loop.py` (conçue pour le triggering implicite) n'est pas applicable à ce type de skill

Mode d'invocation prévu :
- `/blindspot <target-path> [--reviewer <audit-skill>]` (slash command, syntaxe harmonisée avec /walkthrough)
- Mention explicite par l'utilisateur ("lance blindspot", "blindspot review", "check for circularity")

Les should-not-trigger queries passent à 100% (precision=100%), ce qui confirme l'absence de faux positifs.

### Premier test fonctionnel (2026-03-31)

Invocation : `/blindspot skill-adversary ~/.claude/skills/skill-adversary/`

Résultat : flow complet exécuté avec succès.
- Phase 0 : Strong circularity détectée (path overlap + model family overlap) — OK
- Phase 1 : cross-model-judge agent lancé (Gemini 2.5 Pro via OpenRouter) — 10 findings retournés. Skill-adversary lancé en parallèle (Sonnet agents) — 18 findings instrution + 16 findings trigger.
- Phase 2 : rapport de convergence compilé — 5 agreed, 6 Claude-only, 3 external-only.

**Validation clé du concept :** les 2 findings critiques (prompt injection, path traversal) ont été flaggés uniquement par Gemini. Claude ne les a pas vus. C'est exactement le type de blindspot que le skill est conçu pour détecter.

Aucun bug ou finding sur blindspot lui-même lors de ce test.

### Passage par skill-creator (2026-03-31)

- evals.json reformaté au schéma skill-creator (id, skill_name, expectations)
- trigger_eval.json créé (20 queries : 10 should-trigger, 10 should-not)
- run_loop.py lancé pour optimisation de description : recall=0% (attendu, skill à invocation explicite)
- Description mise à jour avec mention "EXPLICIT-INVOCATION skill"
- Optimisation de description abandonnée (inadaptée pour ce type de skill)

### Self-review (2026-03-31)

Invocation : `/blindspot skill-adversary ~/.claude/skills/blindspot/`

Résultat : Strong circularity détectée, cross-model judge + skill-adversary lancés en parallèle.
- Gemini 2.5 Pro : 9 findings (2 critical, 3 high, 3 medium, 1 low)
- Skill-adversary (Claude) : 22 findings (3 critical, 11 important, 8 minor)
- Convergence : 3 agreed, 8 Claude-only, 5 external-only

**Pattern confirmé :** les 2 findings critiques de sécurité (command injection via model name, path traversal vers API externe) sont à nouveau flaggés uniquement par Gemini — même pattern que le test sur skill-adversary.

#### Fixes appliqués (8 corrections)

| Fix | Fichier | Description |
|-----|---------|-------------|
| G1 | cross-model-judge.md | Allowlist de 6 modèles autorisés, rejet des model IDs inconnus |
| G2+C-3 | SKILL.md | Validation d'input : path boundary (~/.claude/ ou cwd), anti-récursion (rejet de blindspot comme audit-skill) |
| G7 | cross-model-judge.md | `trap EXIT` pour cleanup du fichier temp, `2>/dev/null` sur stderr curl |
| C2 | SKILL.md | Méthodologie de convergence analysis (semantic matching, 3 buckets, gestion source manquante) |
| I-1 | SKILL.md | Reformulation "no subagent" → "orchestration in main model, seul cross-model-judge délégué" |
| I-3 | SKILL.md | Path overlap restructuré en 3 critères OR explicites |
| I-5/G3 | SKILL.md | Claim de model override supprimée, renvoi à l'allowlist |
| XF1 | SKILL.md | Instructions explicites pour passer les 4 inputs au cross-model-judge |

#### Findings différés (passe 2, non urgents)

- Trigger FPs/FNs : skill à invocation explicite, recall=0% assumé
- API key leakage : risque théorique (curl en subshell)
- Finding cap de 10 : cosmétique
- Unreachable matrix rows : documentation théorique
- Validation existence audit skill : l'erreur du Skill tool suffit

### Deuxième test fonctionnel — skill-adversary (2026-03-31)

Invocation : `/blindspot skill-adversary ~/.claude/skills/skill-adversary/`

Objectif : obtenir un rapport frais et appliquer les fixes qui avaient été identifiés lors du premier test mais jamais appliqués à skill-adversary.

Résultat : flow complet exécuté avec succès.
- Phase 0 : Strong circularity (path overlap + model family overlap) — OK
- Phase 1 : cross-model-judge (Gemini 2.5 Pro) — 10 findings. Skill-adversary (Claude, agents Sonnet) — 16 trigger + 17 instruction findings.
- Phase 2 : convergence compilée — 5 agreed, 10 Claude-only, 4 external-only.

**Pattern confirmé pour la 3e fois :** les 2 mêmes findings critiques de sécurité (path traversal E1, prompt injection E2) sont flaggés uniquement par Gemini. Claude ne les voit toujours pas de lui-même.

#### Fixes appliqués à skill-adversary (9 corrections)

| Fix | Source | Fichier | Description |
|-----|--------|---------|-------------|
| E1 | Gemini-only (critical) | SKILL.md | Input validation : résolution absolue, vérification existence, restriction path à ~/.claude/ et cwd, disambiguation global/project |
| E2 | Gemini-only (important) | SKILL.md | Prompt injection defense : data-boundary warning dans les prompts sub-agents, section SECURITY |
| E3 | Gemini-only (minor) | SKILL.md | Bias mitigation reframé en "heuristiques" avec limites explicites |
| E4 | Gemini-only (minor) | trigger-attacker.md | "8-10 prompts" → "up to 10 prompts" |
| A3 | Agreed | SKILL.md | Cross-model fallback reporting dans le Summary |
| A5 | Agreed | SKILL.md | Gestion YAML malformed + name field manquant |
| C4 | Claude-only (critical) | SKILL.md | 6 étapes de compilation explicites (parse, dedup, sort, generate, compute) |
| C5 | Claude-only (important) | SKILL.md | Limite 80K chars pour l'inventaire avec stratégie de troncature |
| C2 | Claude-only (important) | SKILL.md | Glob pattern explicite `**/*.{md,txt,yaml,yml}` |

### Prochaine étape

V1 complète, self-reviewée, et deuxième test fonctionnel concluant. Prêt pour utilisation en production.
Extensions V2 possibles : rubric forcing, devil's advocate, panel de juges.

### Ce que ça ne résout pas

- Le biais résiduel intra-distribution même avec cross-model (Gemini a ses propres biais)
- Le cas où l'utilisateur bypass blindspot et lance directement le skill d'audit
- La validation humaine reste le plancher irréductible
