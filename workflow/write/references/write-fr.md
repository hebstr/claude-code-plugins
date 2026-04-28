## Scénario français

Article technique long en français de France, écrit par un ingénieur pour ses pairs. Naturel, précis, sans pose. Ni rapport de cabinet, ni cours, ni communiqué LinkedIn.

Le français technique de France absorbe les anglicismes idiomatiques (framework, runtime, deploy, debug, push, ship). Ce guide ne chasse pas l'anglais. Il chasse la prose IA : tournures rituelles, sublimations, parallélismes négatifs, calques de l'anglais, langue de bois corporate.

**Références autorisées :**
- TLFi (cnrtl.fr) pour le sens et l'étymologie
- Le Grevisse, Riegel-Pellat-Rioul (*Grammaire méthodique du français*) pour la grammaire
- *Lexique des règles typographiques en usage à l'Imprimerie nationale*, Lacroux *Orthotypographie* pour la typographie
- Frantext, Orféo pour les corpus

**Référence rejetée :** l'Académie française, institution littéraire sans autorité descriptive sur la langue réelle.

Pour les tics IA spécifiques, aucune autorité n'existe : observation empirique sur corpus (sorties Claude/ChatGPT/Mistral/Le Chat en français vs prose humaine idiomatique : Bortzmeyer, sebsauvage, Maître Eolas, blogs OCTO/Sfeir/Doctolib engineering).

### Flux d'exécution

Ordre des passes, à respecter :

1. Préserver la sémantique. Vérifier d'abord : faits, logique, causalité, intention de l'auteur restent inchangés.
2. Retirer les tics IA. Commencer par les **phrases de clôture redondantes** en fin de paragraphe ("ce qui montre que…", "on voit donc que…", "en somme…"). C'est le tic le plus fréquent et le plus invisible.
3. Lisser les phrases. Régler les phrases bancales, les ruptures inutiles, le rythme trop uniforme.
4. Ajuster la ponctuation. Réduire parenthèses parasites, guillemets d'emphase, séries de phrases courtes en mitraillette.
5. Annoter les termes seulement à la première apparition. Pas de redoublement.
6. Relire en entier. Corriger les points d'accroc, ne pas réécrire ce qui était déjà naturel.

### Priorité maximale : naturel > stylisé

Ne pas forcer le ton "à l'oral" pour faire humain. Pas d'ajout d'expressions familières, d'exclamations, d'interjections ("bah", "franchement", "trop", "ouf", "carrément") quand le texte original était neutre.

**Préserver les tournures naturelles déjà présentes**. Si l'auteur écrit "du coup" naturellement, ne pas le remplacer par "donc" en croyant gagner en formalisme. Désoraliser à l'excès est aussi mauvais que sur-oraliser. La priorité maximale est de ne pas ajouter, pas de remplacer.

### Mode par défaut : article technique

Cible : ingénieur écrivant pour ingénieur. Pas un instituteur, pas un consultant.

- Phrases déclaratives, pas exclamatives.
- Pas de signal d'autorité ("comme tout bon développeur le sait", "vous le savez sans doute").
- Pas de phrases creuses pour faire sympa ("on est tous passés par là", "qui n'a jamais…").
- Privilégier : précis, calme, direct, concret.
- Si la phrase initiale est déjà naturelle et précise, ne pas la modifier pour la rendre "plus humaine".
- Préférer la réduction. Supprimer phrases de glose, de transition, de conclusion redondante. Pas réécrire ce qui n'a pas besoin de l'être.

**Quand le public n'est pas technique** (produit, business, ops) : trois choses à enlever en priorité — les jugements vers le bas ("pour les non-techniciens", "à destination du grand public"), le ton injonctif ("vous devez", "il faut absolument"), le jargon profond non expliqué. Adopter une logique "voici ce que je fais, fais pareil", pas "voici l'analyse systémique du domaine".

### Ouvertures directes

Pas de mise en bouche. Entrer dans le sujet.

> NO: « Au cours des dernières années, l'intelligence artificielle a profondément transformé… »
> OK: « J'ai migré notre pipeline d'ingestion de pandas à polars. Le job qui prenait 40 minutes en prend 90 secondes. »

> NO: « De nos jours, la performance des bases de données est un enjeu crucial… »
> OK: « Cette requête mettait 12 secondes. Je voulais comprendre pourquoi. »

> NO: « Force est de constater que les LLM sont devenus omniprésents… »
> OK: « Voici ce que j'ai testé avec Claude sur ce repo. »

Conclusion d'abord, raisonnement ensuite. Cas concret d'abord, généralisation ensuite (et seulement si elle est nécessaire).

### Dégonfler le vocabulaire formel

| Évite | Préfère |
|---|---|
| extrêmement, particulièrement (en abus) | très, beaucoup, ou supprimer |
| à l'instar de | comme |
| par conséquent | donc |
| également (en abus) | aussi, et |
| effectuer une vérification | vérifier |
| procéder à l'analyse | analyser |
| réaliser une opération | faire |
| l'utilisation de X permet de | X permet de, utilisé pour |
| dans le but de | pour |
| dans la mesure où | parce que, puisque |
| il est nécessaire de | il faut |
| il existe une possibilité de | on peut |
| de manière significative | beaucoup, fortement |
| dans une large mesure | en grande partie |
| acquérir | obtenir, acheter |
| posséder | avoir |
| nécessiter | demander, exiger |
| afin de | pour |
| s'agissant de | pour, sur, à propos de |

Le verbe **permettre** mérite une mention spéciale : surutilisé en français technique. "Cette API permet de filtrer" = "Cette API filtre". À garder seulement quand il y a vraiment une notion de capacité offerte à un tiers.

Le verbe **mettre en place** : creux. Préciser — installer, configurer, écrire, déployer, brancher.

### Anglicismes corporate vs anglicismes idiomatiques

Le français technique de France absorbe les anglicismes depuis quarante ans. La cible n'est pas l'anglais, c'est l'IA-slop. Un terme intégré au lexique des ingénieurs français reste un terme français. Un verbe anglais flexionné à la sauce LinkedIn sonne creux.

Deux principes :

1. Si le mot est attesté dans la prose technique courante (blogs, RFC en français, conférences, Stack Overflow FR) et n'a pas d'équivalent compact, garde-le.
2. Si le mot est un verbe corporate francisé pour faire moderne, traduis-le.

#### Anglicismes idiomatiques à préserver

| Terme | Pourquoi le garder |
|---|---|
| framework | Pas de traduction compacte. « Cadriciel » est un calque artificiel, jamais utilisé en pratique. |
| runtime | Désigne à la fois l'environnement d'exécution et la durée. Aucun équivalent aussi court. |
| deploy / déployer | Verbe complètement intégré, conjugaison française régulière. |
| build | Désigne l'artefact ET le processus. « Compilation » couvre mal les builds JS/Docker. |
| push / pull | Vocabulaire git natif, intraduisible sans périphrase. |
| commit | Idem, plus le sens dérivé « unité de changement ». |
| merge | Pareil, et « fusionner » fonctionne aussi quand le contexte le porte. |
| rollback | « Retour arrière » fonctionne mais rollback est plus précis (état restauré, pas juste annulé). |
| debug / déboguer | Verbe lexicalisé, présent dans les dictionnaires généralistes. |
| fix | Court, utile en titre de commit ou en discussion. |
| refactor / refactoriser | Distinct de « réécrire », sens technique précis (préserver le comportement). |
| mock | « Simulacre » ne passe pas, « bouchon » est marginal. |
| stub | Idem. |
| scope | Sens technique (portée lexicale, périmètre fonctionnel) sans équivalent unique. |
| log / logs | Lexicalisé. « Journal » fonctionne en doc formelle, log domine en prose courante. |
| parser | Verbe et nom, intégrés. « Analyser » est moins précis. |
| hash / hasher | Terme cryptographique standard. |
| embedding | Vocabulaire ML stabilisé, « plongement » existe mais reste académique. |
| pipeline | CI/CD, data, ML. Aucune traduction n'a pris. |
| stack | Pile technique, intégré. |
| prompt | Vocabulaire LLM standard. |
| token | Idem, plus le sens authentification. |
| manager | Le rôle, pas le verbe. « Chef » ne couvre pas le même registre. |
| mail | Plus court qu'« e-mail » ou « courriel », domine en oral et en écrit informel. |
| bug | Lexicalisé depuis les années 80. |
| week-end | Dans les dictionnaires depuis 1926, francisé avec trait d'union. |
| backend / frontend | Vocabulaire web standard. |
| benchmark | « Étalonnage » couvre mal le sens (comparaison comparative chiffrée). |
| cache | Lexicalisé, accord et conjugaison française. |
| daemon | Terme Unix historique. |
| endpoint | API REST, intégré. |
| feature | « Fonctionnalité » fonctionne mais feature passe en discussion technique courante. |
| issue | Vocabulaire GitHub/GitLab standard. |
| patch | Lexicalisé. |
| release | « Version » couvre mal le sens (publication d'une version). |
| repo / repository | « Dépôt » fonctionne aussi, les deux cohabitent. |
| script | Lexicalisé depuis longtemps. |
| serveur | Déjà francisé. |

#### Anglicismes corporate à traduire

| Évite | Préfère |
|---|---|
| leverager (les données, les insights) | utiliser, exploiter, tirer parti de |
| actionner un plan, un pipeline | lancer, déclencher, exécuter (« actionner un mécanisme » reste OK en méca) |
| onboarder | intégrer, accueillir, former |
| pusher une idée, une roadmap | pousser, faire avancer, défendre |
| scaler (en métaphore floue) | passer à l'échelle, élargir, étendre |
| driver un projet, un résultat | piloter, mener, conduire |
| challenger une décision | remettre en question, contester, mettre à l'épreuve |
| briefer / debriefer (hors aéro/militaire) | informer, faire le point ; débriefer reste OK pour le retour d'expérience formel |
| pitcher une idée | présenter, exposer, défendre |
| forwarder un mail | faire suivre, transmettre |
| staffer une équipe | composer l'équipe, affecter |
| shipper la roadmap | livrer, publier la feuille de route |
| ça matche | ça correspond, ça colle, ça concorde |
| streamliner un process | simplifier, rationaliser, fluidifier |
| insights | enseignements, signaux, observations |
| learnings | leçons, retours, enseignements |
| ownership (sur un sujet) | responsabilité, prise en charge |
| mindset | état d'esprit, posture, approche |
| disrupter un marché | bouleverser, transformer (souvent juste creux, à supprimer) |
| empowerer une équipe | donner les moyens à, autonomiser |

> NO: On va leverager les insights pour driver l'onboarding.
> OK: On va exploiter les retours pour piloter l'intégration.

#### Test de jugement

Avant de garder ou de traduire, trois questions :

1. Le terme apparaît-il dans la prose technique de mes pairs (collègues ingénieurs, doc française d'outils, articles francophones) ? Si oui, garde-le.
2. Existe-t-il un équivalent français aussi compact et précis ? Si non, garde l'anglicisme. Si oui mais que personne ne l'emploie (« cadriciel »), garde quand même l'anglicisme.
3. Est-ce un verbe en `-er` greffé sur un verbe anglais pour sonner moderne (leverager, actionner, driver) ? Si oui, traduis.

### Calques structurels et faux amis

Les calques sont plus pernicieux que les anglicismes lexicaux : ils empruntent un mot français existant en lui collant le sens de l'anglais. Le résultat passe le filtre orthographique mais sonne traduit.

| Évite | Préfère | Pourquoi |
|---|---|---|
| adresser un problème | aborder, traiter, s'attaquer à | TLFi : « adresser » prend un destinataire (adresser une lettre, une question à qqn). Calque de *to address an issue*. |
| supporter une fonctionnalité, un format | prendre en charge, gérer, accepter | TLFi : « supporter » = endurer, soutenir un poids. Calque de *to support*. |
| définitivement (au sens de *certainly*) | certainement, sans aucun doute, clairement | TLFi : « définitivement » = de manière définitive, une fois pour toutes. Calque de *definitely*. |
| éventuellement (au sens de *eventually*) | finalement, à terme, au bout du compte | TLFi : « éventuellement » = le cas échéant, peut-être. Faux ami de *eventually*. |
| actuellement (au sens de *actually*) | en fait, en réalité, à vrai dire | TLFi : « actuellement » = à l'heure actuelle, en ce moment. Faux ami de *actually*. |
| réaliser (au sens de comprendre) | se rendre compte, comprendre, prendre conscience | TLFi : « réaliser » = rendre réel, accomplir. Le sens « comprendre » est un calque de *to realize*, signalé comme critiqué. |
| compléter une tâche, un travail | terminer, achever, accomplir, finir | TLFi : « compléter » = rendre complet en ajoutant ce qui manque. Calque de *to complete a task*. |
| ça fait sens, ça fait du sens | c'est cohérent, c'est logique, ça se tient | Calque direct de *it makes sense*. Le français a toujours dit « avoir du sens ». |
| basé sur | fondé sur, à partir de, qui repose sur | Toléré en tech, surutilisé. Grevisse signale comme calque de *based on*. À doser. |
| en charge de | chargé de, responsable de | Calque de *in charge of*. « Avoir la charge de » reste correct. |
| approcher un sujet, une question | aborder, traiter | TLFi : « approcher » = se rapprocher physiquement. Calque de *to approach*. |
| délivrer un message, de la valeur | transmettre, apporter, livrer | TLFi : « délivrer » = libérer, ou remettre officiellement (un diplôme). Calque de *to deliver*. |
| je dirais que (en abus systématique) | à mon avis, je pense que, selon moi | Calque de *I would argue that*. Le conditionnel d'atténuation existe en français mais l'IA en abuse. |
| au final | finalement, à la fin, en définitive | Toléré en oral, surutilisé dans la prose IA. Grevisse signale l'usage comme familier. |
| permettre de pouvoir, peut permettre de | reformuler avec un verbe plein | Empilement vide. « Cette API permet de pouvoir filtrer » = « Cette API filtre » ou « permet de filtrer ». |
| il s'agit de X (en abus) | c'est X, X est | Tic IA. « Il s'agit d'un fichier JSON » = « C'est un fichier JSON ». Garde « il s'agit de » quand le sens est vraiment « il est question de ». |
| développer un produit, une fonctionnalité (au sens de créer) | concevoir, créer, écrire, implémenter | TLFi : « développer » = faire croître, exposer en détail. Calque de *to develop*. Acceptable pour « développement logiciel » au sens global, à éviter pour une feature précise. |
| pratiquement (au sens de presque) | presque, quasiment | TLFi : « pratiquement » = en pratique, dans les faits. Calque de *practically*. |
| initier un projet, un processus | lancer, démarrer, amorcer | TLFi : « initier » = introduire à la connaissance de. Calque de *to initiate*. |
| opportunité (au sens d'occasion) | occasion (le sens « caractère opportun » reste OK) | TLFi : « opportunité » = caractère de ce qui est opportun. Le sens « occasion favorable » est un calque de *opportunity*, désormais largement attesté mais à doser. |
| dédié à (en abus) | consacré à, réservé à, spécifique à | « Une équipe dédiée », « un serveur dédié » passent. « Une page dédiée à expliquer X » alourdit. |
| reporter (au sens de signaler) | signaler, faire remonter, rapporter | TLFi : « reporter » = différer, transposer. Calque de *to report*. |
| versatile (au sens de polyvalent) | polyvalent, souple | TLFi : « versatile » = changeant, inconstant (péjoratif). Faux ami de *versatile*. |
| sévère (au sens de grave) | grave, sérieux | TLFi : « sévère » = strict, rigoureux. Faux ami de *severe* dans « bug sévère » = « bug grave ». |
| consistent / consistant (au sens de cohérent) | cohérent, homogène, régulier | TLFi : « consistant » = qui a de la consistance, épais. Faux ami de *consistent*. |

> NO: Il s'agit définitivement d'une feature qui adresse le problème et délivre de la valeur basée sur les insights utilisateurs.
> OK: C'est clairement une fonctionnalité qui traite le problème et apporte de la valeur, à partir des retours utilisateurs.

### Tics oraux à ne pas surajouter

À ne pas plaquer sur une prose neutre quand le but est de "sonner humain" :

- **du coup** en début de phrase (sauf si déjà présent et naturel chez l'auteur)
- **en mode** + N (« en mode rapide », « en mode test ») hors contexte technique précis
- **grosso modo** (préférer un chiffre)
- **genre**, **style**, **en gros** comme cheville
- **bah**, **ouais**, **ouf**, **trop**
- **j'avoue**, **carrément**, **à donf**, **à fond les ballons**
- **pour le coup**, **pour la peine**
- **un peu zarb**, **chelou**

Garder ce que l'original avait déjà si naturel. Désoraliser une prose orale relève d'une décision éditoriale séparée, pas du nettoyage anti-IA-slop.

### Concrétisation prudente

Par défaut, ne pas changer. Si la phrase originale est déjà claire, ne pas la rendre « plus imagée » ou « plus parlante ».

Concrétiser seulement quand l'original est trop abstrait pour être compris. Test : un lecteur du métier comprend-il la phrase à la première lecture ? Si oui, laisser. Si non, remplacer l'abstraction par un terme concret du domaine.

> NO: « la lourdeur opérationnelle s'amplifie » → « le scheduler se prend des dizaines de jobs en parallèle, le runner part en swap »
> OK: garder l'original s'il était déjà précis.

Ne pas surajouter de couleur. Une métaphore par paragraphe maximum, jamais filée sur trois pages.

### Structures de phrases

- Pas de **premièrement / deuxièmement / troisièmement** en prose. Soit liste à puces, soit « d'abord / puis / enfin » si vraiment nécessaire.
- Paragraphes longs OK s'ils se lisent d'un trait.
- Pas de fragments de phrase pour faire dramatique. Phrase complète, sujet-verbe-complément.
- **Pas de tiret cadratin (—) ni demi-cadratin (–) en ponctuation interne.** Virgule, deux-points, parenthèses, ou restructure. Voir section typographie.
- **Phrases courtes en chaîne** : 4 phrases courtes consécutives donnent un ton télégramme. Combiner deux d'entre elles avec une virgule ou un connecteur.
- Pas de « il faut d'abord… ensuite… » moralisateur. Préférer « on commence par… », « le plus simple est de… ».
- **Trois éléments en triplet** : si la relation est serrée, écrire en phrase, pas en liste. Ne pas forcer la liste pour rythmer.
- Pas de question rhétorique pour cadrer le lecteur (« comment faire ? »). Affirmer, le titre suffit à poser la question.

### Rythme bold + ponctuation

`**xxx**.` `content` (bold + point + explication) est un tic d'IA. Le bold devient un mini-titre détaché du paragraphe. Préférer `**xxx**` `, content` — le bold devient appui ou sujet de la phrase.

> NO: **alias.** J'ai mis dans `.zshrc`...
> OK: **alias**, j'ai mis dans `.zshrc`...

Exception : si le bold est lui-même une phrase complète (« **ça compile pas** », « **c'est pas testé** »), garder le point. Test : le bold seul tient-il comme phrase autonome ? Oui → point. Non → virgule.

### Dé-listification progressive

Trop de bullets dans un article = pitch deck. Étapes pour passer du list à la prose :

1. Liste numérotée 1. 2. 3. → puces `- xxx` (sauf si l'ordre est sémantique)
2. Puces `- **xxx** : content` → paragraphe bold `**xxx**, content`
3. 4 paragraphes bold consécutifs → un seul paragraphe en prose, items séparés par point-virgule ou virgule

S'arrêter à n'importe quelle étape selon le contenu. Garder les puces si :
- chaque entrée a une grosse explication indépendante ;
- les entrées sont des règles parallèles à scanner ;
- le titre de section a déjà résumé l'essentiel et la prose détaille.

Numérotation 1/2/3 : réservée aux séquences vraies (priorité, temps, étapes, citations ordonnées).

### Conception des titres

Trois formats selon la structure, pas un seul.

**Format à deux-points** (sujet : précision) : pour terme à expliquer (« Cache : mémoire avant le réseau ») ou sujet + thèse (« Sécurité : la frontière compte plus que la fonction »).

**Format en phrase** : quand le sous-titre n'apporte rien ou fait doublon avec le titre.

> NO: « Hallucinations : un piège des multi-agents » (« un piège » est faible)
> OK: « Les multi-agents amplifient les hallucinations »

**Garder la virgule en titre pour** : séquences (« D'abord les tests, ensuite l'implémentation ») ; énumérations parallèles (« Décisions sync, I/O async »).

**Pas de Title Case anglais.** Capitale initiale + noms propres seulement.

> NO: « Architecture Multi-Format Via Un Seul Fichier »
> OK: « Architecture multi-format via un seul fichier »

**Titres avec verdict, pas juste un nom.** Un titre devrait pouvoir tenir comme phrase brève qui prend position.

> NO: « Multi-agents et hallucinations » (juste un thème)
> OK: « Le multi-agents fait s'amplifier les hallucinations »
> OK: « Évaluer avant l'agent, sinon on ne sait pas ce qu'on corrige »

### Guillemets, parenthèses, point-virgule (discipline d'usage)

Ces trois signes ont une typographie correcte (voir section suivante) et un usage qui, mal calibré, alourdit la prose.

#### Guillemets « »

Pour citations, sortie système, message d'erreur. **Pas pour emphase.** Pas pour mettre un mot à distance ironique.

> NO: Le LLM excelle en « traduction ».
> NO: Pour empêcher l'agent de « tricher » sur le score.
> OK: Le LLM excelle dans la traduction selon spec.
> OK: Pour empêcher l'agent de manipuler le score.

#### Parenthèses ( )

**Règle des dix mots.** Si la parenthèse dépasse dix mots, c'est qu'elle devrait être dans la prose. Si une même phrase contient deux parenthèses, en réécrire au moins une dans le corps du texte.

> NO: L'APM traditionnel (Datadog, New Relic et compagnie qui surveillent surtout latence et taux d'erreur) ne sert pas à grand-chose.
> OK: Ces APM traditionnels qui surveillent surtout latence et taux d'erreur ne servent pas à grand-chose.

OK pour : terme anglais en première mention, plage chiffrée (5–15 %), paramètre de code, abréviation explicitée.

#### Point-virgule ;

Pas un point flemmard. En cas d'hésitation entre `;` et `.`, choisir `.`.

Légitime pour :
- phrases en parallèle (« on échoue sur les tests, on rejoue ; on échoue sur le déploiement, on revient en arrière ») ;
- liste interne dans une phrase ;
- énumération en blocs.

**Point-virgule + connecteur logique = erreur.** Si tu mets « mais » ou « donc » derrière, le `.` s'impose.

> NO: « le linter passe ; mais les tests d'intégration cassent »
> OK: « le linter passe. Mais les tests d'intégration cassent. »

### Typographie française

Référence principale : *Lexique des règles typographiques en usage à l'Imprimerie nationale* (dernière édition courante). Référence complémentaire pour les cas d'usage : Lacroux, *Orthotypographie*. Aucune autorité n'est plus solide en français écrit professionnel.

#### Espaces avant la ponctuation

Le français place une espace avant les ponctuations doubles. Le Lexique IN précise : espace fine insécable (U+202F) avant `;`, `!`, `?`, et idéalement `:`. Espace insécable normale (U+00A0) avant `:` est l'usage historique, la fine est l'évolution moderne. Espace insécable normale après `«` et avant `»`.

| Signe | Espace avant | Espace après |
|---|---|---|
| `,` `.` | aucune | normale |
| `:` | fine ou normale insécable | normale |
| `;` `!` `?` | fine insécable (U+202F) | normale |
| `«` | normale | fine insécable |
| `»` | fine insécable | normale |
| `%` `°C` `€` | fine insécable | normale |

> NO: Il faut vérifier:le fichier existe ?
> OK: Il faut vérifier : le fichier existe ?

En pratique, dans un éditeur Markdown : l'espace insécable normale (U+00A0) suffit partout. La distinction fine/normale relève de la composition finale (Quarto, Typst, LaTeX la gèrent souvent automatiquement).

#### Guillemets

Guillemets français `« »`, jamais `" "` américains ni `" "` typographiques anglais. Espace fine insécable à l'intérieur.

> NO: Il a dit "le code est cassé".
> OK: Il a dit « le code est cassé ».

Citation imbriquée : guillemets anglais (curly) à l'intérieur des guillemets français.

> OK: Elle a répondu : « Quand il dit "ça marche", il ment. »

Lexique IN : pas de guillemets fermants en début de ligne dans les citations longues sur plusieurs paragraphes ; guillemets ouvrants répétés en début de chaque paragraphe interne, fermants seulement à la fin.

#### Tirets

Pas de tiret cadratin (—, U+2014) ni demi-cadratin (–, U+2013) comme ponctuation interne en prose. C'est un anglicisme typographique, présent dans la prose IA par contagion de l'anglais et de l'allemand.

Le demi-cadratin sert à deux choses, et seulement deux :
1. Plages de nombres : « pages 12–18 », « 2020–2024 ».
2. Dialogues, tiret de prise de parole en début de ligne (registre littéraire, hors prose technique).

Pour une incise ou une rupture, utilise virgule, deux-points, parenthèses, ou restructure.

> NO: La fonction — qui prend deux arguments — retourne un booléen.
> OK: La fonction, qui prend deux arguments, retourne un booléen.
> OK: La fonction (qui prend deux arguments) retourne un booléen.

Le trait d'union `-` reste utilisé pour les mots composés et la coupure de mots.

#### Capitales accentuées

Obligatoires. Le Lexique IN est explicite : « En français, l'accent a pleine valeur orthographique. » Les capitales prennent leurs accents.

> NO: Etat, A bientot, Ecole, Ile-de-France
> OK: État, À bientôt, École, Île-de-France

#### Apostrophe typographique

En prose finale, apostrophe courbe `'` (U+2019), pas l'apostrophe droite `'` (U+0027). En code, en Markdown technique, en YAML, en chaînes de caractères : on garde l'apostrophe droite, le moteur de rendu fait le reste si besoin.

> Prose : « l'API », « aujourd'hui »
> Code : `data['key']`, `it's`

#### Sigles et acronymes

Majuscules sans points. Le Lexique IN a tranché depuis longtemps : `CNRS`, `RATP`, `SNCF`, `INSEE`, pas `C.N.R.S.`.

Acronymes prononcés et lexicalisés : passent en bas-de-casse, parfois avec accord en nombre.

> OK: un ovni, des ovnis, le pacs, le sida, un radar, un laser

#### « etc. »

Toujours avec un point, jamais sans. Précédé d'une virgule, jamais suivi de points de suspension. Pas de redoublement.

> NO: les fonctions, les classes, les modules etc...
> NO: les fonctions, les classes, etc., etc.
> OK: les fonctions, les classes, les modules, etc.

#### Pourcentages, unités, heures

Espace insécable entre le nombre et l'unité.

> NO: 10%, 5km, 3h30
> OK: 10 %, 5 km, 3 h 30

Le symbole `°C` reste collé au `°`, mais l'ensemble est précédé d'une espace insécable : `25 °C`.

#### Nombres

Séparateur de milliers : espace fine insécable, jamais virgule ni point.

> NO: 1,000,000 ou 1.000.000
> OK: 1 000 000

Décimale : virgule.

> NO: 3.14
> OK: 3,14

#### Citations longues

Bloc en retrait, sans guillemets, sans italique. La mise en bloc suffit à signaler la citation. Lacroux insiste : empiler guillemets, italique et retrait est redondant et lourd.

#### Italique

Réservé à :
- titres d'œuvres (livres, films, journaux, logiciels en tant qu'œuvre) ;
- mots étrangers non lexicalisés (*serendipity*, *Schadenfreude*, mais pas « bug » ni « pipeline » qui sont intégrés) ;
- termes définis ou cités en tant que mots (« le mot *fonction* a deux sens »).

Pas d'italique pour l'emphase. Le gras, sobrement, fait le travail.

#### Capitales en titres

Style français : seul le premier mot prend la capitale, plus les noms propres. Pas de Title Case anglais.

> NO: Architecture Multi-Format Via Un Seul Fichier
> OK: Architecture multi-format via un seul fichier

#### Énumérations

Si chaque item est une phrase complète : majuscule en tête, point final.
Si fragments : minuscule en tête, point-virgule entre items, point seulement à la fin.

> Items-phrases :
> - La fonction valide les entrées.
> - Elle écrit dans le journal.
> - Elle retourne un code de statut.

> Items-fragments :
> - validation des entrées ;
> - écriture journalisée ;
> - code de statut retourné.

### Détection des tics IA en français

Patterns récurrents dans les sorties Claude/ChatGPT/Mistral en français. Si ta prose en contient plus de deux ou trois, réécris.

1. **Phrase de sublimation.** L'observation technique promue en vérité universelle, souvent en clôture de paragraphe.
   > NO: Ce bug révèle une vérité plus profonde sur la nature même du logiciel.
   > OK: Ce bug vient d'un cache mal invalidé.

2. **Parallélisme négatif.** Le tic n°1. « Ce n'est pas X. C'est Y. » ou « Non pas X, mais Y. »
   > NO: Ce n'est pas un simple outil. C'est une nouvelle façon de penser.
   > OK: C'est un linter avec un mode auto-fix.

3. **Question rhétorique auto-répondue.** La phrase pose une question qu'elle répond aussitôt, en deux mots.
   > NO: Le résultat ? Spectaculaire. Et le coût ? Minime.
   > OK: La latence passe de 800 ms à 40 ms, sans surcoût mesurable.

4. **Répétition inter-paragraphe.** Trois paragraphes qui disent la même chose sous trois angles légèrement différents.
   > NO: (P1: « le code est lisible ») (P2: « la lisibilité prime ») (P3: « on lit plus qu'on n'écrit »)
   > OK: Garde un seul paragraphe, supprime les deux autres.

5. **Citation + glose.** « Comme le dit X, … » suivi d'une reformulation plate de la citation.
   > NO: Comme le dit Knuth, "premature optimization is the root of all evil". Autrement dit, optimiser trop tôt est une mauvaise idée.
   > OK: Knuth : "premature optimization is the root of all evil".

6. **Énumération en triplet systématique.** Tout vient par trois, même quand deux suffisent ou que cinq seraient honnêtes. Variante : binôme synonyme corporate (« robuste et fiable », « clair et précis », « balisés et caractérisés », « complexes ou fragmentées »). Triplet d'adjectifs vagues empilés en ouverture, signature du communiqué institutionnel : « Technologie innovante, performante et flexible ». Garde un terme, le plus précis, ou supprime.
   > NO: C'est rapide, fiable et élégant.
   > OK: C'est rapide et fiable. (ou : rapide, fiable, testé, documenté, packagé)
   > NO: Une technologie innovante, performante et flexible.
   > OK: Une technologie souple. (ou : précise ce qu'elle fait)

7. **Bottleneck transfer.** « Le problème n'est plus X, c'est Y maintenant. » Faux mouvement dialectique.
   > NO: Le problème n'est plus la performance, c'est la maintenabilité.
   > OK: La perf est réglée. Reste à rendre le code maintenable.

8. **Conclusion impérative.** « L'enjeu est clair : … », « Une chose est sûre : … », « Le constat est sans appel. »
   > NO: Une chose est sûre : l'observabilité n'est plus optionnelle.
   > OK: Sans logs structurés, tu débugges à l'aveugle.

9. **Définition encyclopédique en ouverture.** Premier paragraphe qui définit le sujet façon Wikipédia.
   > NO: Le CI/CD est l'ensemble des pratiques visant à automatiser la livraison de logiciel…
   > OK: Notre pipeline CI/CD met 12 minutes. Voici comment on l'a ramené à 3.

10. **Sous-titres en parallélisme parfait.** Quatre `##` qui suivent exactement la même structure grammaticale.
    > NO: ## Comprendre le besoin / ## Définir la solution / ## Implémenter le code / ## Mesurer l'impact
    > OK: Titres concrets et asymétriques, calés sur ce que le lecteur va vraiment lire.

11. **Pont de chapitre.** « Maintenant que nous avons vu X, voyons Y. » Le titre suivant suffit.
    > NO: Maintenant que nous avons couvert l'installation, passons à la configuration.
    > OK: (rien, le `## Configuration` suffit)

12. **Clôture redondante.** Dernière phrase qui répète le paragraphe.
    > NO: …et c'est ainsi que le cache se réchauffe en arrière-plan. En somme, le cache se réchauffe sans bloquer la requête.
    > OK: Coupe la deuxième phrase.

13. **Tournures rituelles.** « Force est de constater », « il convient de noter », « il importe de souligner », « il est intéressant de remarquer ».
    > NO: Force est de constater que les tests passent.
    > OK: Les tests passent.

14. **Cadres passe-partout.** « À l'aune de », « à l'heure où », « dans le cadre de », « au cœur de ».
    > NO: À l'heure où l'IA transforme nos métiers, il convient de repenser nos pipelines.
    > OK: Les LLM changent nos pipelines de doc. Voici comment on adapte le nôtre.

15. **« Véritable » + nom.** Modificateur vide qui essaie de donner du poids. Variantes interchangeables : « ultime », « authentique », « formidable ». Sur le registre business-marketing, le pattern devient : nom-cliché de transformation (catalyseur, levier, moteur, pilier, vecteur, accélérateur) + modificateur vide. La phrase porte alors zéro information.
    > NO: Un véritable défi, une véritable révolution, un véritable game-changer.
    > OK: Un défi. Une rupture. (ou supprime le mot)
    > NO: Le cloud doit être le catalyseur ultime de votre activité. (Scaleway, Q1 2026 product recap)
    > OK: Supprime, ou décris ce que ça fait concrètement (ex : « Le cloud doit s'effacer derrière les outils de tes équipes »).

16. **Verbes-clichés de transformation.** « Révolutionne », « redéfinit », « bouleverse », « réinvente », « transforme radicalement ».
    > NO: Polars révolutionne le traitement de données en Python.
    > OK: Polars est 5 à 30 fois plus rapide que pandas sur nos jobs.

17. **« Loin d'être X, Y ».** Retournement automatique, presque toujours faux ou inutile.
    > NO: Loin d'être un gadget, Quarto est un outil de production.
    > OK: Quarto sert en prod chez nous depuis deux ans.

18. **Fausse précision numérique.** « Trois enseignements », « cinq points clés », « sept règles d'or », alors que rien ne justifie le compte rond.
    > NO: Voici les cinq leçons que nous avons tirées.
    > OK: Voici ce qu'on a appris (puis liste honnête, 2 ou 11 items, peu importe).

19. **Métaphore filée trop loin.** « L'écosystème », « le voyage », « le puzzle » tenus sur dix paragraphes.
    > NO: Notre écosystème data est un jardin. On y plante, on y arrose, on y récolte. Les mauvaises herbes sont les data quality issues…
    > OK: Lâche la métaphore après deux phrases, reviens au concret.

20. **Annonce de ce qu'on va dire.** « À noter que », « notons que », « précisons que », « soulignons que ».
    > NO: Notons que cette approche a un coût mémoire.
    > OK: Cette approche coûte 2 Go de RAM en plus.

21. **Exhortation finale.** « À nous de jouer. », « L'avenir nous le dira. », « Le défi est lancé. »
    > NO: À nous de bâtir l'IA de demain.
    > OK: (supprime, ou termine sur le dernier fait technique)

22. **Disclaimer de modèle.** « Selon les informations disponibles », « à ma connaissance », « il semblerait que » alors que tu sais.
    > NO: Selon les informations disponibles, PostgreSQL 16 supporte le logical replication.
    > OK: PostgreSQL 16 supporte la réplication logique (cf. release notes).

23. **Faux suspense de transition.** « Mais voilà… », « Sauf que… », « Et c'est là que ça se corse. »
    > NO: On pensait avoir gagné. Sauf que…
    > OK: Le déploiement a échoué : timeout sur la migration.

24. **Empilement d'analogies d'entreprises.** « Apple n'a pas fait X. Google n'a pas fait Y. Stripe n'a pas fait Z. »
    > NO: Stripe n'a pas vendu un produit, ils ont vendu une API. Notion n'a pas vendu une app, ils ont vendu un canvas. Linear n'a pas vendu un tracker, ils ont vendu un workflow.
    > OK: On a copié l'idée de Stripe : doc et API au même endroit, exemples exécutables.

25. **Adverbes d'intensité empilés.** « Particulièrement », « extrêmement », « véritablement », « résolument », souvent en chaîne.
    > NO: Cette approche est particulièrement et résolument tournée vers la performance.
    > OK: Cette approche vise la perf.

26. **Passif corporate.** Sujet effacé sous une tournure passive ou un verbe-écran (« est mis à disposition », « ont dû être traitées », « peuvent être activés », « constitue l'un des arguments avancés »). Tic des communiqués institutionnels et des articles tech business. Réintroduire l'agent ou couper.
    > NO: Cette logique cumulative constitue l'un des arguments avancés par les startups du secteur.
    > OK: Les startups du secteur en font un argument.
    > NO: Une fois cette architecture déployée, de nouveaux cas d'usage peuvent être activés.
    > OK: Une fois l'architecture déployée, l'organisation active de nouveaux cas d'usage.

27. **« Capacité à » + Vinf répété.** Calque de *capacity to + V-inf*. Trois occurrences en deux paragraphes = signal IA. Préfère le verbe direct.
    > NO: Leur capacité à dépasser… leur capacité à interagir… leur capacité à naviguer…
    > OK: Ils dépassent… ils interagissent… ils naviguent…

28. **« Acteur » mot-valise.** « Nouvelle génération d'acteurs », « autre acteur très surveillé », « les acteurs du marché ». Tic article tech business FR. Précise (entreprise, équipe, fournisseur, concurrent, startup) ou supprime.
    > NO: L'émergence des agents stimule une nouvelle génération d'acteurs.
    > OK: De nouvelles startups se positionnent sur les agents.

29. **« Le caractère X de Y ».** Calque administratif pour « la X-té de Y » ou « Y X ». Lourdeur typique du communiqué officiel.
    > NO: L'ANSSI prévient du caractère rapide de l'évolution des usages.
    > OK: L'ANSSI prévient que les usages évoluent vite.

### Ton inductif vs verdict

Dans un article technique, signaler le degré de certitude. La forme verbale « X cause Y » / « Y vient de là » / « c'est ainsi que Y » claque comme verdict définitif. Préférer le ton inductif quand l'observation est partielle.

> NO: « Le gain de capacité vient de cette astuce-là. »
> OK: « Les résultats publiés suggèrent que cette astuce y contribue. »

> NO: « Cette pratique élimine le problème. »
> OK: « Sur nos jobs, cette pratique a éliminé le problème. »

Les lecteurs experts détectent l'écart entre ce que tu sais avec certitude et ce que tu déduis d'un cas. Donner les conditions d'observation. Préserver les pondérations de l'auteur original (si l'auteur a écrit « semble », ne pas le passer en « est »).

### Pléonasmes et hypercorrections

#### Pléonasmes courants

| Évite | Préfère | Pourquoi |
|---|---|---|
| voire même | voire | TLFi : « voire » signifie déjà « et même ». Le redoublement est un pléonasme classique, signalé par Grevisse comme fautif. |
| au jour d'aujourd'hui | aujourd'hui | « Aujourd'hui » contient déjà « hui » (= ce jour) précédé de « au jour de ». Triple marquage. Grevisse le qualifie de pléonasme renforcé, toléré en oral expressif, à proscrire à l'écrit. |
| comme par exemple | comme, ou par exemple | Les deux disent la même chose. Choisir l'un. |
| puis ensuite | puis, ou ensuite | Synonymes en succession temporelle. |
| monter en haut, descendre en bas, sortir dehors, entrer dedans | monter, descendre, sortir, entrer | La direction est dans le verbe. |
| réitérer à nouveau, répéter à nouveau | réitérer, répéter | TLFi : « réitérer » = faire de nouveau. Le préfixe `ré-` suffit. |
| reporter à plus tard | reporter, différer | TLFi : « reporter » contient déjà l'idée de remise dans le temps. |
| prévoir à l'avance, prévoir d'avance | prévoir | TLFi : « prévoir » = voir à l'avance. |
| ajouter en plus | ajouter | « Ajouter » suppose déjà l'addition. |
| s'avérer vrai, s'avérer faux | être vrai, se révéler faux, se révéler exact | « S'avérer » vient de « avéré » = reconnu vrai. « S'avérer faux » est étymologiquement contradictoire ; l'usage l'a imposé, mais Lacroux et Grevisse signalent. |
| collaborer ensemble | collaborer | Le préfixe `co-` porte déjà la coopération. |
| bref résumé, petit résumé | résumé | Un résumé est par définition bref. |
| car en effet | car, ou en effet | Deux marqueurs causaux empilés. |
| une opportunité à saisir | une occasion, une opportunité | Saisir est implicite dans « opportunité » au sens calqué (voir section calques). |
| projeter dans le futur | projeter | « Projeter » = jeter en avant, dans le temps à venir. |
| descendre vers le bas, remonter vers le haut | descendre, remonter | Idem monter/descendre. |
| suffisamment assez | suffisamment, ou assez | Synonymes. |

#### Hypercorrections et pièges grammaticaux

| Piège | Règle | Source |
|---|---|---|
| « après que » + indicatif | « Après qu'il est venu », pas « après qu'il soit venu ». L'événement de la subordonnée est antérieur, donc réel, donc indicatif. La confusion vient du calque sur « avant que » + subjonctif. | Grevisse, *Le Bon Usage*, §1124. |
| « pallier » est transitif direct | « pallier un problème », pas « pallier à un problème ». Confusion avec « remédier à ». | TLFi, entrée *pallier*. |
| « se rappeler » est transitif direct | « je me rappelle ce moment », pas « je me rappelle de ce moment ». La construction avec « de » est calquée sur « se souvenir de ». | TLFi, entrée *rappeler*. Grevisse signale l'usage avec « de » comme très répandu mais critiqué. |
| « suite à » | Préposition contestée en registre soutenu. Préfère « à la suite de », « comme suite à », ou « après ». Tolérée en correspondance commerciale. | Grevisse signale l'usage administratif sans le condamner formellement. |
| « malgré que » + subjonctif | Usage attesté chez Proust et Gide, longtemps proscrit, encore critiqué en registre soutenu. Préfère « bien que » + subjonctif, ou « malgré » + nom. | Grevisse, §1097. |
| « deuxième » vs « second » | L'usage classique réservait « second » à une série de deux, « deuxième » à une série ouverte. L'usage moderne neutralise la distinction ; les deux sont interchangeables. Garde « second » par variation stylistique, pas par règle. | Grevisse, §581. |
| « davantage » vs « d'avantage(s) » | « Davantage » = plus, adverbe. « D'avantage(s) » = de bénéfice(s), groupe nominal. « Il en sait davantage » / « pas d'avantage fiscal ». | TLFi, entrée *davantage*. |
| « censé » vs « sensé » | « Censé » = supposé (du latin *censere*). « Sensé » = qui a du sens. « Il est censé arriver à 9 h » / « une remarque sensée ». | TLFi, entrées *censé* et *sensé*. |
| « solutionner » | Verbe attesté tardivement (XIXe siècle), toléré, sonne bureaucratique. Préfère « résoudre ». | TLFi note l'usage comme familier ou administratif. |
| « conséquent » au sens de « important » | Sens classique : qui agit avec logique, qui suit. Le sens « considérable » (« une somme conséquente ») est un glissement attesté mais critiqué. Préfère « considérable », « important », « substantiel ». L'usage est tellement répandu que le bannir devient pédant : à doser. | Grevisse signale, TLFi mentionne le sens étendu comme courant mais critiqué. |
| « pour pas que » | Forme orale. À l'écrit : « pour que … ne … pas », « afin que … ne … pas ». « Pour qu'il ne se trompe pas », pas « pour pas qu'il se trompe ». | Grevisse, registre familier signalé. |
| Accord du participe passé avec « avoir » + COD antéposé | Le participe s'accorde avec le COD si celui-ci précède le verbe. « Les fichiers que j'ai écrits » (COD = *que*, mis pour *fichiers*, antéposé, masculin pluriel). « J'ai écrit des fichiers » (COD postposé, pas d'accord). | Grevisse, §947. |
| « par contre » vs « en revanche » | « Par contre » longtemps critiqué (Voltaire, Littré), réhabilité par Gide et l'usage. Tolérable partout, « en revanche » reste plus soutenu. | Grevisse, §1058 : usage admis. |
| « au temps pour moi » | « Au temps pour moi », pas « autant pour moi ». Origine militaire (reprise du tempo). L'usage avec « autant » est attesté mais reste une faute en registre soigné. | Lacroux, *Orthotypographie*. |

### Découpe des paragraphes longs

Paragraphe au-delà de 400-500 mots ou avec 3 concepts indépendants : difficile à lire sur mobile, dilue la phrase importante. Couper aux changements de concept, pas par souci esthétique.

Si une phrase isolée flotte en paragraphe (1-2 lignes seules) : c'est presque toujours la conclusion du paragraphe précédent ou l'introduction du suivant. Recoller au paragraphe d'origine.

### Introduction des cas

Avant de zoomer sur un cas concret (un produit, un projet, un commit), une demi-phrase qui dit ce qu'il représente. Pas zoom direct sans contexte.

> NO: « PARL de Kimi K2.5 est l'exemple à creuser. Il entraîne uniquement l'orchestrateur… »
> OK: « PARL de Kimi K2.5 marque un choix précis : entraîner uniquement l'orchestrateur, garder la planification statique. Le signal de récompense se découpe en trois… »

### Règles éprouvées

Issues de retours répétés, prioritaires sur les préférences de style :

- **Avant de supprimer un paragraphe entier**, vérifier qu'il ne contient pas une donnée, un fait technique, ou une logique non répétée ailleurs. La règle « couper les phrases de clôture » vise les redondances structurelles, pas les paragraphes qui ouvrent une idée.
- **Supprimer une phrase entière vs réécrire.** Si une phrase ne porte que du slop (cliché de transformation, parallélisme négatif, intensifieur vide, fausse agentivité), supprimer. Si elle contient une donnée chiffrée, un nom propre, une condition technique, une cause précise, **réécrire** : retirer le slop, garder le fait. Test : retirer mentalement les éléments slop ; s'il reste une information factuelle, la phrase doit survivre sous forme nettoyée. Sinon, couper sans regret.
- **Sémantique d'abord, IA-slop ensuite.** Une réécriture qui change le sens ou le degré de certitude est un échec, peu importe si elle est plus naturelle.
- **Garder parenthèses et guillemets quand un terme apparaît pour la première fois ou quand on lève une ambiguïté.** Ne pas sacrifier la clarté au profit du minimalisme.
- **Densité de points.** Trop de phrases courtes en suite donnent un ton compte-rendu. Combiner deux ou trois en une phrase complexe quand le lien est naturel.
- **Pas de question rhétorique pour cadrer le lecteur.** « Vous vous demandez sûrement comment… » est une posture d'instituteur. Affirmer.
- **Pas d'empilement de jugements abstraits.** Préférer fait observable, position dans la chaîne, impact concret.
- **Conclusion centrale dite une fois.** Si elle a été énoncée en intro, ne pas la reformuler en clôture.
- **Tensions internes de l'auteur, à préserver.** Si l'auteur tient des positions apparemment contradictoires entre deux paragraphes (libre vs structuré, vite vs propre), ne pas trancher pour lui. Marquer l'évolution si elle est temporelle, garder les deux faces si elles relèvent de domaines différents.

### Ton rapport (langue de bois corporate FR)

Tournures de cabinet de conseil et de blog SEO IA. À gauche le tic, à droite ce qu'un humain technique écrirait.

| Évite | Préfère |
|---|---|
| dans le cadre de | pour, lors de, pendant |
| à l'aune de | selon, par rapport à |
| à l'heure où | aujourd'hui, maintenant que (ou supprime) |
| au cœur de | dans, central à |
| force est de constater que | on voit que (ou supprime) |
| il convient de noter que | (supprime) |
| il importe de souligner que | (supprime) |
| il est intéressant de remarquer | (supprime) |
| à cet égard | là-dessus, sur ce point |
| de surcroît / qui plus est | et, en plus |
| néanmoins / toutefois / cependant en début de phrase systématique | mais |
| par ailleurs (cumulé en chaîne) | et, ensuite |
| in fine | au final, à la fin (ou supprime) |
| au demeurant | d'ailleurs (ou supprime) |
| approche centrée utilisateur | on part de l'usage |
| solution clé en main | outil prêt à l'emploi |
| solution sur-mesure | outil maison, dev custom |
| écosystème (logiciel) | stack, outils, ensemble |
| levier (de croissance, de productivité) | moyen, façon |
| paradigme | approche, modèle (ou supprime) |
| problématique (nom) | problème, question |
| thématique (nom) | sujet, thème |
| en termes de X | côté X, pour X |
| à l'échelle de | sur, dans |
| de manière générale | en général (ou supprime) |
| dans une certaine mesure | un peu, en partie |
| afin de | pour |
| de par sa nature | parce que (cause explicite) |
| s'inscrit dans une démarche de | sert à, vise à |
| pose les jalons de | prépare, ouvre la voie à |
| à la croisée de X et Y | entre X et Y, mélange X et Y |
| in concreto / de facto | concrètement, en pratique |
| nonobstant | malgré, sans tenir compte de |
| revêt une importance particulière | compte, est important |
| s'avère + adjectif | est + adjectif |
| permet de + verbe (chaîné) | verbe direct (« permet de réduire » → « réduit ») |
| mettre en place | installer, déployer, écrire, faire |
| mettre en œuvre | appliquer, faire |
| faire en sorte que | pour que, s'assurer que |
| à des fins de | pour |
| jouer un rôle clé / central / déterminant | être central, compter (ou supprimer + préciser le mécanisme concret) |
| naviguer dans les défis / face aux défis | affronter, traiter, faire face à |
| en constante évolution / mutation / transformation | qui change, qui bouge (ou supprimer ; le contexte le dit déjà) |
| défis complexes | défis (tautologie : un défi est par nature non trivial) |
| enjeu majeur / crucial / stratégique | enjeu (ou supprimer + préciser ce qui est en jeu) |
| décisions plus éclairées | mieux décider, décider sur données |
| de manière plus X (rapide, intelligente, efficace) | plus X-ment, plus X (« de manière plus rapide » → « plus vite ») |
| digital(e) au sens de numérique | numérique (faux ami signalé par le Lexique IN ; « digital » garde son sens « relatif aux doigts ») |

### Tournures récemment refusées

Catalogue ouvert. Chaque entrée : tournure, pourquoi elle dégage, alternative.

- **« Du coup » en début de phrase** : tic oral, pollue à l'écrit. Remplace par « donc », « alors », ou rien.
- **« En mode » + nom** : registre oral plaqué sur du technique. « En mode debug » passe (terme exact), « en mode rapide » non. Préfère « rapidement », « façon X ».
- **« Grosso modo »** : flou et oralisant. Préfère « en gros », « à peu près », ou donne le chiffre.
- **« Premièrement / deuxièmement / troisièmement »** : scolaire. Utilise une vraie liste à puces, ou « d'abord… puis… enfin » si la prose le justifie.
- **« Véritablement »** : adverbe vide, signal IA fort. Supprime.
- **« Réellement »** : idem, sauf opposition explicite à « apparemment ».
- **« Particulièrement »** : flou. Remplace par un chiffre ou supprime.
- **« Notamment » sans précision derrière** : « améliore notamment la perf » sans dire comment ni de combien. Soit tu précises, soit tu coupes.
- **« De plus / en outre / par ailleurs » empilés dans le même paragraphe** : connecteurs paresseux. Garde-en un seul, ou aucun.
- **« À la fin de la journée »** (calque de *at the end of the day*) : à proscrire. Préfère « au final », « à la fin », ou rien.
- **« Au bout du compte »** : signal IA, surtout en clôture. Supprime.
- **« Faire en sorte que »** : tournure faible. « Pour que », « s'assurer que ».
- **« Mettre en place »** : verbe creux. Précise : installer, configurer, écrire, déployer.
- **« Avoir un impact sur »** : flou. « Affecte », « ralentit », « casse », « double ».
- **« Un certain nombre de »** : faux compte. Donne le chiffre ou écris « plusieurs », « quelques ».
- **« Plusieurs »** quand tu en connais le nombre : écris le nombre.
- **« Quelques »** vague : précise (3, 4, une dizaine).
- **« Il est possible de »** : passif IA. « Tu peux », « on peut », « X permet de ».
- **« On peut considérer que »** : hedge. Affirme ou supprime.
- **« Force de proposition »** : jargon RH. Supprime.
- **« Valeur ajoutée »** : corporate. Dis ce que ça apporte concrètement.
- **« Best practice » employé seul** : utilise « bonne pratique » ou cite la pratique exacte.
- **« Robuste »** sans critère : précise (« résiste à 10k req/s », « tolère un noeud down »).
- **« Scalable »** seul : précise l'axe (horizontal, vertical, en charge, en données).
- **« Pertinent »** : adjectif fourre-tout. Utile, adapté, juste, applicable.
- **« En somme / en définitive / pour conclure »** en fin de paragraphe : redondant si la phrase précédente conclut déjà. Supprime.
- **« Il n'en demeure pas moins que »** : lourdeur. « Mais », « pourtant ».
- **« S'inscrire dans la lignée de »** : cliché. « Suit », « reprend », « continue ».
- **« S'inscrit dans une dynamique de »** : ouverture de paragraphe codée, vide. Supprime ou reformule en verbe direct.
- **« Dans une logique X »** ou **« Dans une logique proche »** : ouverture article tech business FR. Tic structurant. Supprime ou nomme la logique.
- **« Colonne vertébrale »** comme métaphore corporate (de l'organisation, du SI, etc.) : remplace par le terme technique précis ou supprime.
- **« Leurs propres + N »** quand « propres » est vide (« leurs propres politiques », « leurs propres règles ») : supprime « propres ».
- **« X de leur choix »** quand le syntagme est calqué sur *X of their choice* (« choisir un outil de leur choix » = pléonasme) : « choisir un outil ».

### Règles supplémentaires articles techniques

**Faits et vérifiabilité avant l'anti-IA-slop.** Ne pas supprimer version, plateforme, dépendance, source, condition de reproduction, limite de validité dans une chasse aux tournures.

- Conserver versions, plateformes, dépendances quand elles influent sur la conclusion.
- Quand on cite « documentation officielle », « tests indiquent », « l'équipe a mesuré », indiquer la source. Pas de source = ne pas écrire en mode verdict.
- Code, commande, configuration : pas de simple copie sans expliquer le paramètre clé.
- Conclusions perf / sécurité / stabilité : préciser cadre d'observation (données, environnement, échantillon).
- Expérience individuelle : ne pas la transformer en règle générale.
- Quand on présente une solution, ajouter une demi-phrase sur le périmètre : « marche pour X, à éviter pour Y ».

**Faits datés.** Prix, version, options, dates de sortie, commandes cachées : ajouter un marqueur temporel — « fin avril 2026 », « à ce jour », « vu sur la version 1.9.37 ». Le lecteur qui retombe deux mois plus tard sur de l'info obsolète doit voir tout de suite quand la photo a été prise.

**Vérifier les noms propres avant de les modifier.** Marque, produit, livre, personne, font : `grep` ou check officiel. Les modifications factuelles sont plus risquées que les modifications de style et c'est pourtant là qu'on improvise le plus.

### Auto-vérification technique

Avant livraison, balayer ces questions :

- Quel problème précis cet article résout ?
- Versions, environnement, dépendances suffisants pour reproduire ?
- Chaque paragraphe apporte-t-il une nouvelle information ?
- Code, commandes, config expliqués sur les points clés ?
- Conclusions appuyées par évidence, données, source ?
- Risques, coûts, limites mentionnés ?
- Expérience individuelle pas étendue en loi générale ?

### Polish checklist post-N rondes

Après plusieurs passes anti-IA, des résidus de niveau phrase passent inaperçus. Six catégories à scanner en clôture :

1. **Mots redondants intra-phrase** : « aussi » + « également » dans la même phrase ; « très » + « extrêmement » ; « permet de » + « rend possible ». Chercher la répétition synonymique.
2. **Phrases longues sans virgule** : phrase de 25+ mots sans pause, signe que la respiration manque. Ajouter virgule après l'élément introductif (temporel, conditionnel).
3. **Cohérence terminologique** : utiliser un seul terme pour un concept dans tout le texte (pas « cache » puis « mémoire tampon » puis « buffer » pour la même chose).
4. **Métaphores non amorcées** : un terme métaphorique apparaît brusquement sans préparation (« le journal de bord », « la pile d'attente »). Si non amorcé, remplacer par le terme générique.
5. **Restes de prépositions parasites** : « au niveau de la mise en place » ; « en termes de performance » ; « dans l'optique de ». À supprimer ou remplacer par préposition simple.
6. **Précision sur les noms propres au premier emploi** : la première apparition doit lever toute ambiguïté (« Claude Code de Anthropic » puis « Claude Code »). Sans précision, le lecteur peut confondre avec un autre produit.

Tests 1 à 3 sont rapides, scan visuel. Tests 4 à 6 exigent une lecture complète.

### Liste « par défaut interdit »

- NO: il convient de noter que (supprimer)
- NO: il importe de souligner que (supprimer)
- NO: force est de constater que (supprimer)
- NO: à noter que (souvent supprimable, ou « note : »)
- NO: il est important de mentionner (supprimer)
- NO: il est intéressant de noter (supprimer)
- NO: à cet égard (supprimer)
- NO: dans cette perspective (supprimer)
- NO: à l'aune de (« selon », « d'après »)
- NO: à l'heure où (« quand », « alors que »)
- NO: à l'ère de (cliché d'intro, supprimer)
- NO: dans le cadre de (en abus ; « pour », « lors de »)
- NO: au cœur de (métaphore vide ; « dans », « au centre de »)
- NO: au-delà de (en abus métaphorique ; « plus que », « hors »)
- NO: in fine (« finalement », ou supprimer)
- NO: véritable + N (« un véritable défi » : supprimer l'adjectif)
- NO: réel + N (« un réel enjeu » : supprimer)
- NO: véritablement (supprimer)
- NO: réellement (supprimer)
- NO: particulièrement (souvent vide, supprimer)
- NO: notamment (à doser, une fois max par section)
- NO: résolument (registre marketing, supprimer)
- NO: pleinement (supprimer)
- NO: incontestablement (supprimer)
- NO: indéniablement (supprimer)
- NO: assurément (supprimer)
- NO: à nous de jouer (cliché de conclusion)
- NO: l'avenir nous le dira (cliché de conclusion)
- NO: une chose est sûre (cliché d'intro)
- NO: l'enjeu est de taille (cliché)
- NO: les jeux sont faits (cliché)
- NO: à suivre (cliché de fin de section)
- NO: pour conclure (supprimer, conclure sans l'annoncer)
- NO: en somme (supprimer)
- NO: en conclusion (supprimer)
- NO: pour finir (supprimer)
- NO: X révolutionne Y (verbe-cliché de transformation)
- NO: X redéfinit Y (idem)
- NO: X bouleverse Y (idem)
- NO: X transforme Y (en abus ; préciser le mécanisme)
- NO: X réinvente Y (cliché)
- NO: X disrupte Y (jargon)
- NO: X chamboule Y (cliché)
- NO: leverager (« exploiter », « tirer parti de »)
- NO: actionner (en métaphore corporate ; « lancer », « déclencher »)
- NO: onboarder (« intégrer », « accueillir »)
- NO: challenger (en abus ; « remettre en question », « contester »)
- NO: scaler (en métaphore floue ; « passer à l'échelle » est OK technique)
- NO: pusher une idée / roadmap (« proposer », « défendre »)
- NO: driver (en métaphore floue ; « piloter », « mener »)
- NO: delivery (au sens corporate ; « livraison », « production »)
- NO: bandwidth (au sens disponibilité mentale ; « temps », « capacité »)
- NO: footprint (en abus métaphorique ; « empreinte », « emprise »)
- NO: adresser un problème (calque ; « traiter », « régler »)
- NO: supporter une fonctionnalité (calque ; « prendre en charge », « gérer »)
- NO: définitivement (au sens *definitely* ; « clairement », « sans aucun doute »)
- NO: ça fait du sens (calque ; « ça a du sens », « c'est cohérent »)
- NO: compléter une tâche (calque ; « terminer », « finir »)
- NO: être en charge de (calque ; « s'occuper de », « gérer »)
- NO: à la fin de la journée (calque ; « au final », « en fin de compte »)
- NO: au bout du compte (en abus, supprimer)
- NO: tiret cadratin en ponctuation (utiliser virgule, deux-points, parenthèses)
- NO: tiret demi-cadratin en ponctuation (idem ; demi-cadratin OK pour plages numériques)
- NO: guillemets droits " " (utiliser « » avec espaces insécables)
- NO: emoji (toutes positions, sauf demande explicite)
- NO: Title Case en titres français (capitale initiale + noms propres seulement)
- NO: cet article a pour objectif de (entrer dans le sujet directement)
- NO: dans ce qui suit, nous verrons (supprimer)
- NO: comme nous le verrons (supprimer)
- NO: comme nous l'avons vu (supprimer, ou citer la section)
- NO: passons maintenant à (supprimer, transition implicite)
- NO: abordons à présent (supprimer)
- NO: voire même (pléonasme ; « voire » seul)
- NO: au jour d'aujourd'hui (pléonasme ; « aujourd'hui »)
- NO: comme par exemple (pléonasme ; « comme » ou « par exemple »)
- NO: puis ensuite (pléonasme ; un seul des deux)
- NO: réitérer à nouveau (pléonasme ; « réitérer » seul)

---

**Bilan : prose qui se lit comme un ingénieur expliquant à un collègue. Pas un manuel, pas un rapport, pas un communiqué. Si une phrase pourrait apparaître sur LinkedIn telle quelle, elle ne va pas dans un article technique.**

---

### Publication externe

Pour release notes, billet public, tweet, newsletter, trois vérifications supplémentaires.

**1. Anonymisation**

Pas d'éléments permettant de remonter à l'auteur : employeur, lieu, équipe, parcours. Les choix techniques peuvent être précis, l'identité reste discrète par défaut.

> NO: « En tant qu'ingénieur Backend chez X depuis 5 ans, je trouve… »
> NO: « Basé à Paris, j'ai testé… »
> OK: « En production, cette config tient X req/s. »
> OK: décrire le choix sans antécédents personnels.

**2. Pas de tacle aux concurrents**

Présenter son outil sans dénigrer le voisin. Ce qu'on n'a pas, on le tait.

> NO: « Cursor indexe tout, ça pompe la RAM. Nous, on évite. »
> NO: « Pas comme Typora qui n'a pas pensé à X… »
> OK: « On n'indexe que les fichiers ouverts. »

**3. Ressenti utilisateur avant fonctionnalités**

Pour release notes ou tweet, pas une liste de features en ouverture. Donner un cas, un effet, ou un ressenti, puis détailler.

> NO: « v1.2.0 : ajout de X, correction de Y, optimisation de Z. »
> OK: « J'ai retravaillé deux choses qui me grattaient dans l'usage. La première… »
