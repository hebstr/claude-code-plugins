# blindspot: Context & Design Rationale

## Origin

Problème identifié en voulant reviewer skill-adversary avec skill-adversary lui-même : biais circulaire d'auto-référence.

## Le problème

Tout skill d'audit (skill-adversary, mcp-adversary, critical-code-reviewer, sweep…) est susceptible d'auditer un artefact produit par un système de la même famille, y compris lui-même.

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
Ne remplace aucun skill d'audit, s'interpose quand le risque circulaire est détecté.

### Architecture

#### Flow

1. **Phase 0, détection de circularité** : compare le chemin de la cible avec le répertoire du skill d'audit (path overlap) et vérifie si le modèle juge et le modèle auteur partagent la même famille (model family overlap). Produit un verdict : Strong circularity, Model circularity, ou No circularity.
2. **Phase 1, routage cross-model** : si circularité détectée et `OPENROUTER_API_KEY` disponible, lance un agent cross-model-judge qui route l'audit vers un modèle non-Claude (défaut : `google/gemini-2.5-pro`) via OpenRouter API. Sinon, fallback avec warning.
3. **Phase 2, rapport transparent** : compile les findings des deux modèles avec une analyse de convergence (agreed / Claude-only / external-only) et un bloc de transparence obligatoire.

#### Décisions d'implémentation

| Décision | Justification |
|----------|--------------|
| OpenRouter only (pas de cascade CLI) | Une seule clé API, un seul chemin de code, choix du modèle, stabilité vs CLI tools jeunes |
| 1 seul agent (cross-model-judge) | Le rapport est compilé par SKILL.md directement, pas besoin d'agent dédié |
| Pas de devil's advocate (V2) | Scope minimal V1 |
| Pas de rubric forcing (V2) | Scope minimal V1 |
| Model family overlap dépend du target, pas du reviewer | Le reviewer est toujours Claude en Claude Code, mais le target peut être human-written ; les 4 lignes de la matrice sont atteignables |
| Fallback = audit normal + warning détaillé | Le skill reste utile même sans clé OpenRouter |
| Convergence analysis comme signal principal | Les findings "external-only" sont les blindspot candidates |

#### Structure

```
blindspot/
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

blindspot est un orchestrateur meta : il n'a de sens que quand l'utilisateur sait qu'il existe et l'invoque volontairement. Le triggering implicite serait contre-productif : intercepter un `skill-adversary` normal sans que l'utilisateur ait exprimé de concern de circularité serait intrusif.

Mode d'invocation prévu :
- `/blindspot <target-path> [--reviewer <audit-skill>]` (slash command, syntaxe harmonisée avec /walkthrough)
- Mention explicite par l'utilisateur ("lance blindspot", "blindspot review", "check for circularity")

## Ce que ça ne résout pas

- Le biais résiduel intra-distribution même avec cross-model (Gemini a ses propres biais)
- Le cas où l'utilisateur bypass blindspot et lance directement le skill d'audit
- La validation humaine reste le plancher irréductible
