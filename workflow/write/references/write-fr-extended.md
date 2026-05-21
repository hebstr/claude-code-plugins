## Scénario français — appendice exhaustif

Ce fichier complète `references/write-fr-core.md`. Il contient les tables exhaustives, les cas limites, les sections scopées registre (article technique long-form, publication externe), les catalogues évolutifs (tournures récemment refusées, listes « par défaut interdit ») et les détails typographiques que le core résume.

Charger ce fichier en plus du core quand :
- le mode bilingue FR↔EN est actif (parité demande l'arsenal complet calques/faux amis) ;
- l'utilisateur demande un review approfondi ou exhaustif ;
- un cas marginal apparaît (registre administratif, publication externe, ton rapport long).

**Référence rejetée :** l'Académie française, institution littéraire sans autorité descriptive sur la langue réelle.

---

### Mode article technique long-form

Cible : ingénieur écrivant pour ingénieur. Pas un instituteur, pas un consultant.

- Phrases déclaratives, pas exclamatives.
- Pas de signal d'autorité (« comme tout bon développeur le sait », « vous le savez sans doute »).
- Pas de phrases creuses pour faire sympa (« on est tous passés par là », « qui n'a jamais… »).
- Privilégier : précis, calme, direct, concret.
- Si la phrase initiale est déjà naturelle et précise, ne pas la modifier pour la rendre « plus humaine ».
- Préférer la réduction. Supprimer phrases de glose, de transition, de conclusion redondante.

### Vocabulaire formel à dégonfler — table complète

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

Le verbe **permettre** mérite une mention spéciale : surutilisé en français technique. « Cette API permet de filtrer » = « Cette API filtre ». À garder seulement quand il y a vraiment une notion de capacité offerte à un tiers.

Le verbe **mettre en place** est creux. Préciser : installer, configurer, écrire, déployer, brancher.

### Anglicismes idiomatiques à préserver — table complète

| Terme | Pourquoi le garder |
|---|---|
| framework | « Cadriciel » est un calque artificiel, jamais utilisé en pratique. |
| runtime | Désigne à la fois l'environnement d'exécution et la durée. |
| deploy / déployer | Verbe complètement intégré, conjugaison française régulière. |
| build | Désigne l'artefact ET le processus. |
| push / pull | Vocabulaire git natif. |
| commit | Idem, plus le sens dérivé « unité de changement ». |
| merge | « Fusionner » fonctionne aussi quand le contexte le porte. |
| rollback | « Retour arrière » fonctionne mais rollback est plus précis. |
| debug / déboguer | Verbe lexicalisé, présent dans les dictionnaires. |
| fix | Court, utile en titre de commit ou en discussion. |
| refactor / refactoriser | Distinct de « réécrire », sens technique précis. |
| mock | « Simulacre » ne passe pas, « bouchon » est marginal. |
| stub | Idem. |
| scope | Sens technique sans équivalent unique. |
| log / logs | Lexicalisé. |
| parser | Verbe et nom, intégrés. |
| hash / hasher | Terme cryptographique standard. |
| embedding | Vocabulaire ML stabilisé. |
| pipeline | CI/CD, data, ML. Aucune traduction n'a pris. |
| stack | Pile technique, intégré. |
| prompt | Vocabulaire LLM standard. |
| token | Idem, plus le sens authentification. |
| manager | Le rôle, pas le verbe. |
| mail | Plus court qu'« e-mail » ou « courriel ». |
| bug | Lexicalisé depuis les années 80. |
| week-end | Dans les dictionnaires depuis 1926. |
| backend / frontend | Vocabulaire web standard. |
| benchmark | « Étalonnage » couvre mal le sens. |
| cache | Lexicalisé, accord et conjugaison française. |
| daemon | Terme Unix historique. |
| endpoint | API REST, intégré. |
| feature | « Fonctionnalité » fonctionne mais feature passe en discussion technique. |
| issue | Vocabulaire GitHub/GitLab standard. |
| patch | Lexicalisé. |
| release | « Version » couvre mal le sens. |
| repo / repository | « Dépôt » fonctionne aussi, les deux cohabitent. |
| script | Lexicalisé depuis longtemps. |
| serveur | Déjà francisé. |

### Anglicismes corporate à traduire — table complète

| Évite | Préfère |
|---|---|
| leverager (les données, les insights) | utiliser, exploiter, tirer parti de |
| actionner un plan, un pipeline | lancer, déclencher, exécuter |
| onboarder | intégrer, accueillir, former |
| pusher une idée, une roadmap | pousser, faire avancer, défendre |
| scaler (en métaphore floue) | passer à l'échelle, élargir, étendre |
| driver un projet, un résultat | piloter, mener, conduire |
| challenger une décision | remettre en question, contester |
| briefer / debriefer (hors aéro/militaire) | informer, faire le point |
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

### Calques structurels et faux amis — table complète

| Évite | Préfère | Pourquoi |
|---|---|---|
| adresser un problème | aborder, traiter, s'attaquer à | TLFi : « adresser » prend un destinataire. Calque de *to address*. |
| supporter une fonctionnalité | prendre en charge, gérer, accepter | TLFi : « supporter » = endurer, soutenir un poids. Calque de *to support*. |
| définitivement (au sens de *certainly*) | certainement, sans aucun doute, clairement | TLFi : « définitivement » = de manière définitive. Calque de *definitely*. |
| éventuellement (au sens de *eventually*) | finalement, à terme | TLFi : « éventuellement » = le cas échéant. Faux ami. |
| actuellement (au sens de *actually*) | en fait, en réalité | TLFi : « actuellement » = en ce moment. Faux ami. |
| réaliser (au sens de comprendre) | se rendre compte, comprendre | TLFi : « réaliser » = rendre réel. Calque de *to realize*. |
| compléter une tâche | terminer, achever, finir | TLFi : « compléter » = rendre complet en ajoutant. Calque de *to complete a task*. |
| ça fait (du) sens | c'est cohérent, ça se tient | Calque de *it makes sense*. Le français a toujours dit « avoir du sens ». |
| basé sur | fondé sur, à partir de | Toléré en tech, surutilisé. Grevisse signale comme calque. |
| en charge de | chargé de, responsable de | Calque de *in charge of*. |
| approcher un sujet | aborder, traiter | Calque de *to approach*. |
| délivrer un message, de la valeur | transmettre, apporter, livrer | TLFi : « délivrer » = libérer, ou remettre officiellement. |
| je dirais que (en abus) | à mon avis, je pense que | Calque de *I would argue that*. |
| au final | finalement, à la fin | Toléré en oral, surutilisé en prose IA. |
| permettre de pouvoir | reformuler avec un verbe plein | Empilement vide. |
| il s'agit de X (en abus) | c'est X, X est | Tic IA. |
| développer une feature (au sens de créer) | concevoir, créer, écrire, implémenter | Calque de *to develop*. |
| pratiquement (au sens de presque) | presque, quasiment | TLFi : « pratiquement » = en pratique. Calque de *practically*. |
| initier un projet | lancer, démarrer, amorcer | TLFi : « initier » = introduire à la connaissance de. |
| opportunité (au sens d'occasion) | occasion | Calque attesté de *opportunity*, à doser. |
| dédié à (en abus) | consacré à, réservé à, spécifique à | « Une équipe dédiée » passe ; « une page dédiée à expliquer X » alourdit. |
| reporter (au sens de signaler) | signaler, faire remonter | Calque de *to report*. |
| versatile (au sens de polyvalent) | polyvalent, souple | Faux ami : « versatile » = changeant, péjoratif. |
| sévère (au sens de grave) | grave, sérieux | Faux ami de *severe*. |
| consistent / consistant (au sens de cohérent) | cohérent, homogène | Faux ami de *consistent*. |

> NO: Il s'agit définitivement d'une feature qui adresse le problème et délivre de la valeur basée sur les insights utilisateurs.
> OK: C'est clairement une fonctionnalité qui traite le problème et apporte de la valeur, à partir des retours utilisateurs.

### Rythme bold + ponctuation

`**xxx**.` `content` (bold + point + explication) est un tic d'IA. Le bold devient un mini-titre détaché du paragraphe. Préférer `**xxx**, content`, le bold devient appui ou sujet de la phrase.

> NO: **alias.** J'ai mis dans `.zshrc`...
> OK: **alias**, j'ai mis dans `.zshrc`...

Exception : si le bold est lui-même une phrase complète (« **ça compile pas** »), garder le point. Test : le bold seul tient-il comme phrase autonome ? Oui → point. Non → virgule.

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

### Conception des titres — formats détaillés

Trois formats selon la structure, pas un seul.

**Format à deux-points** (sujet : précision) : pour terme à expliquer (« Cache : mémoire avant le réseau ») ou sujet + thèse (« Sécurité : la frontière compte plus que la fonction »).

**Format en phrase** : quand le sous-titre n'apporte rien ou fait doublon avec le titre.

> NO: « Hallucinations : un piège des multi-agents » (« un piège » est faible)
> OK: « Les multi-agents amplifient les hallucinations »

**Garder la virgule en titre pour** : séquences (« D'abord les tests, ensuite l'implémentation ») ; énumérations parallèles (« Décisions sync, I/O async »).

### Discipline guillemets, parenthèses, point-virgule

#### Guillemets « »

Pour citations, sortie système, message d'erreur. **Pas pour emphase.** Pas pour mettre un mot à distance ironique.

> NO: Le LLM excelle en « traduction ».
> OK: Le LLM excelle dans la traduction selon spec.

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

### Typographie française complète

Référence principale : *Lexique des règles typographiques en usage à l'Imprimerie nationale*. Référence complémentaire : Lacroux, *Orthotypographie*.

#### Espaces avant la ponctuation

Le français place une espace avant les ponctuations doubles. Espace fine insécable (U+202F) avant `;`, `!`, `?`, et idéalement `:`. Espace insécable normale (U+00A0) avant `:` est l'usage historique, la fine est l'évolution moderne. Espace insécable normale après `«` et avant `»`.

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

#### Guillemets imbriqués

Citation imbriquée : guillemets anglais (curly) à l'intérieur des guillemets français.

> OK: Elle a répondu : « Quand il dit "ça marche", il ment. »

Lexique IN : pas de guillemets fermants en début de ligne dans les citations longues sur plusieurs paragraphes ; guillemets ouvrants répétés en début de chaque paragraphe interne, fermants seulement à la fin.

#### Sigles et acronymes

Majuscules sans points. `CNRS`, `RATP`, `SNCF`, `INSEE`, pas `C.N.R.S.`.

Acronymes prononcés et lexicalisés : passent en bas-de-casse, parfois avec accord en nombre.

> OK: un ovni, des ovnis, le pacs, le sida, un radar, un laser

#### « etc. »

Toujours avec un point, jamais sans. Précédé d'une virgule, jamais suivi de points de suspension. Pas de redoublement.

> NO: les fonctions, les classes, les modules etc...
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

Bloc en retrait, sans guillemets, sans italique. La mise en bloc suffit. Lacroux insiste : empiler guillemets, italique et retrait est redondant.

#### Italique

Réservé à :
- titres d'œuvres (livres, films, journaux, logiciels en tant qu'œuvre) ;
- mots étrangers non lexicalisés (*serendipity*, *Schadenfreude*) ;
- termes définis ou cités en tant que mots (« le mot *fonction* a deux sens »).

Pas d'italique pour l'emphase. Le gras, sobrement, fait le travail.

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

### Tics IA secondaires (20 tics complémentaires)

Ces tics complètent les 12 tics du core. Plus rares, scopés à un registre, ou moins immédiatement reconnaissables.

1. **Répétition inter-paragraphe.** Trois paragraphes qui disent la même chose sous trois angles légèrement différents.
   > NO: (P1: « le code est lisible ») (P2: « la lisibilité prime ») (P3: « on lit plus qu'on n'écrit »)
   > OK: Garde un seul paragraphe.

2. **Citation + glose.** « Comme le dit X, … » suivi d'une reformulation plate.
   > NO: Comme le dit Knuth, "premature optimization is the root of all evil". Autrement dit, optimiser trop tôt est une mauvaise idée.
   > OK: Knuth : "premature optimization is the root of all evil".

3. **Bottleneck transfer.** « Le problème n'est plus X, c'est Y maintenant. » Faux mouvement dialectique.
   > NO: Le problème n'est plus la performance, c'est la maintenabilité.
   > OK: La perf est réglée. Reste à rendre le code maintenable.

4. **Définition encyclopédique en ouverture.** Premier paragraphe qui définit le sujet façon Wikipédia.
   > NO: Le CI/CD est l'ensemble des pratiques visant à automatiser la livraison de logiciel…
   > OK: Notre pipeline CI/CD met 12 minutes. Voici comment on l'a ramené à 3.

5. **Sous-titres en parallélisme parfait.** Quatre `##` qui suivent exactement la même structure grammaticale.
   > NO: ## Comprendre le besoin / ## Définir la solution / ## Implémenter le code / ## Mesurer l'impact
   > OK: Titres concrets et asymétriques.

6. **Pont de chapitre.** « Maintenant que nous avons vu X, voyons Y. » Le titre suivant suffit.
   > NO: Maintenant que nous avons couvert l'installation, passons à la configuration.
   > OK: (rien, le `## Configuration` suffit)

7. **« Loin d'être X, Y ».** Retournement automatique, presque toujours faux ou inutile.
   > NO: Loin d'être un gadget, Quarto est un outil de production.
   > OK: Quarto sert en prod chez nous depuis deux ans.

8. **Fausse précision numérique.** « Trois enseignements », « cinq points clés », « sept règles d'or », alors que rien ne justifie le compte rond.
   > NO: Voici les cinq leçons que nous avons tirées.
   > OK: Voici ce qu'on a appris (puis liste honnête, 2 ou 11 items).

9. **Métaphore filée trop loin.** « L'écosystème », « le voyage », « le puzzle » tenus sur dix paragraphes.
   > NO: Notre écosystème data est un jardin. On y plante, on y arrose, on y récolte. Les mauvaises herbes sont les data quality issues…
   > OK: Lâche la métaphore après deux phrases.

10. **Exhortation finale.** « À nous de jouer. », « L'avenir nous le dira. », « Le défi est lancé. »
    > NO: À nous de bâtir l'IA de demain.
    > OK: (supprime, ou termine sur le dernier fait technique)

11. **Disclaimer de modèle.** « Selon les informations disponibles », « à ma connaissance », « il semblerait que » alors que tu sais.
    > NO: Selon les informations disponibles, PostgreSQL 16 supporte le logical replication.
    > OK: PostgreSQL 16 supporte la réplication logique (cf. release notes).

12. **Faux suspense de transition.** « Mais voilà… », « Sauf que… », « Et c'est là que ça se corse. »
    > NO: On pensait avoir gagné. Sauf que…
    > OK: Le déploiement a échoué : timeout sur la migration.

13. **Empilement d'analogies d'entreprises.** « Apple n'a pas fait X. Google n'a pas fait Y. Stripe n'a pas fait Z. »
    > NO: Stripe n'a pas vendu un produit, ils ont vendu une API. Notion n'a pas vendu une app, ils ont vendu un canvas.
    > OK: On a copié l'idée de Stripe : doc et API au même endroit.

14. **Passif corporate.** Sujet effacé sous une tournure passive ou un verbe-écran (« est mis à disposition », « ont dû être traitées », « peuvent être activés », « constitue l'un des arguments avancés »). Tic des communiqués institutionnels et des articles tech business.
    > NO: Cette logique cumulative constitue l'un des arguments avancés par les startups du secteur.
    > OK: Les startups du secteur en font un argument.

15. **« Capacité à » + Vinf répété.** Calque de *capacity to + V-inf*. Trois occurrences en deux paragraphes = signal IA.
    > NO: Leur capacité à dépasser… leur capacité à interagir… leur capacité à naviguer…
    > OK: Ils dépassent… ils interagissent… ils naviguent…

16. **« Acteur » mot-valise.** « Nouvelle génération d'acteurs », « autre acteur très surveillé », « les acteurs du marché ». Tic article tech business FR.
    > NO: L'émergence des agents stimule une nouvelle génération d'acteurs.
    > OK: De nouvelles startups se positionnent sur les agents.

17. **« Le caractère X de Y ».** Calque administratif pour « la X-té de Y » ou « Y X ».
    > NO: L'ANSSI prévient du caractère rapide de l'évolution des usages.
    > OK: L'ANSSI prévient que les usages évoluent vite.

18. **« C'est ça X. »** Démonstratif qui mime l'emphase, n'ajoute rien à ce qui précède.
    > NO: C'est ça le vrai problème. / C'est ça le levier. / C'est ça qui casse tout.
    > OK: Énonce le problème ou le levier directement.

19. **Refermer un paragraphe sur sa propre conclusion.** Reformuler en fin de paragraphe ce que les phrases précédentes ont déjà établi.
    > NO: …[paragraphe]… Ce qu'il faut retenir : … / Autrement dit, … / Au fond, …
    > OK: Termine sur la dernière phrase substantielle. Le lecteur vient de lire le paragraphe.

20. **Pronom orphelin après édition.** Après une coupe, « il », « ce », « cela », « celui-ci » perd son antécédent.
    > NO: « L'interface accepte les listes de colonnes. Il gère aussi la coercion. » (le paragraphe au-dessus parlait du « préprocesseur », coupé depuis : « il » devient flottant.)
    > OK: Relis chaque pronom après une coupe. Si tu ne peux pas pointer son antécédent dans les une à deux phrases précédentes, remplace par le nom ou restructure.

### Pléonasmes — table complète

| Évite | Préfère | Pourquoi |
|---|---|---|
| voire même | voire | TLFi : « voire » signifie déjà « et même ». |
| au jour d'aujourd'hui | aujourd'hui | « Aujourd'hui » contient déjà « hui » (= ce jour). Triple marquage. |
| comme par exemple | comme, ou par exemple | Synonymes. |
| puis ensuite | puis, ou ensuite | Synonymes en succession temporelle. |
| monter en haut, descendre en bas, sortir dehors | monter, descendre, sortir | La direction est dans le verbe. |
| réitérer à nouveau, répéter à nouveau | réitérer, répéter | Préfixe `ré-` suffit. |
| reporter à plus tard | reporter, différer | Idée de remise dans le temps déjà présente. |
| prévoir à l'avance, prévoir d'avance | prévoir | « Prévoir » = voir à l'avance. |
| ajouter en plus | ajouter | « Ajouter » suppose déjà l'addition. |
| s'avérer vrai, s'avérer faux | être vrai, se révéler faux | « S'avérer » vient de « avéré » = reconnu vrai. |
| collaborer ensemble | collaborer | Préfixe `co-` porte la coopération. |
| bref résumé, petit résumé | résumé | Un résumé est par définition bref. |
| car en effet | car, ou en effet | Deux marqueurs causaux empilés. |
| projeter dans le futur | projeter | « Projeter » = jeter en avant, dans le temps à venir. |
| descendre vers le bas, remonter vers le haut | descendre, remonter | Idem monter/descendre. |
| suffisamment assez | suffisamment, ou assez | Synonymes. |

### Hypercorrections et pièges grammaticaux

| Piège | Règle | Source |
|---|---|---|
| « après que » + indicatif | « Après qu'il est venu », pas « après qu'il soit venu ». L'événement est antérieur, donc réel, donc indicatif. | Grevisse, *Le Bon Usage*, §1124. |
| « pallier » est transitif direct | « pallier un problème », pas « pallier à un problème ». | TLFi, entrée *pallier*. |
| « se rappeler » est transitif direct | « je me rappelle ce moment », pas « je me rappelle de ce moment ». | TLFi, entrée *rappeler*. |
| « suite à » | Préposition contestée. Préfère « à la suite de », « après ». | Grevisse signale l'usage administratif. |
| « malgré que » + subjonctif | Critiqué en registre soutenu. Préfère « bien que » + subjonctif. | Grevisse, §1097. |
| « deuxième » vs « second » | Distinction neutralisée. Garder « second » par variation, pas par règle. | Grevisse, §581. |
| « davantage » vs « d'avantage(s) » | « Davantage » = plus, adverbe. « D'avantage(s) » = de bénéfice(s). | TLFi. |
| « censé » vs « sensé » | « Censé » = supposé. « Sensé » = qui a du sens. | TLFi. |
| « solutionner » | Toléré, sonne bureaucratique. Préfère « résoudre ». | TLFi. |
| « conséquent » au sens de « important » | Glissement attesté mais critiqué. À doser. | Grevisse, TLFi. |
| « pour pas que » | Forme orale. À l'écrit : « pour que … ne … pas ». | Grevisse. |
| Accord du PP avec « avoir » + COD antéposé | Le PP s'accorde avec le COD si celui-ci précède. | Grevisse, §947. |
| « par contre » vs « en revanche » | « Par contre » réhabilité ; « en revanche » reste plus soutenu. | Grevisse, §1058. |
| « au temps pour moi » | Pas « autant pour moi ». Origine militaire. | Lacroux. |

### Découpe des paragraphes longs

Paragraphe au-delà de 400-500 mots ou avec 3 concepts indépendants : difficile à lire sur mobile, dilue la phrase importante. Couper aux changements de concept, pas par souci esthétique.

Si une phrase isolée flotte en paragraphe (1-2 lignes seules) : c'est presque toujours la conclusion du paragraphe précédent ou l'introduction du suivant. Recoller.

### Introduction des cas

Avant de zoomer sur un cas concret (un produit, un projet, un commit), une demi-phrase qui dit ce qu'il représente. Pas zoom direct sans contexte.

> NO: « PARL de Kimi K2.5 est l'exemple à creuser. Il entraîne uniquement l'orchestrateur… »
> OK: « PARL de Kimi K2.5 marque un choix précis : entraîner uniquement l'orchestrateur, garder la planification statique. Le signal de récompense se découpe en trois… »

### Ton rapport corporate FR — table complète

Tournures de cabinet de conseil et de blog SEO IA. À gauche le tic, à droite ce qu'un humain technique écrirait.

| Évite | Préfère |
|---|---|
| dans le cadre de | pour, lors de, pendant |
| à l'aune de | selon, par rapport à |
| à l'heure où | aujourd'hui, maintenant que |
| au cœur de | dans, central à |
| force est de constater que | on voit que (ou supprime) |
| il convient de noter que | (supprime) |
| il importe de souligner que | (supprime) |
| il est intéressant de remarquer | (supprime) |
| à cet égard | là-dessus, sur ce point |
| de surcroît / qui plus est | et, en plus |
| néanmoins / toutefois / cependant en début systématique | mais |
| par ailleurs (cumulé en chaîne) | et, ensuite |
| in fine | au final, à la fin (ou supprime) |
| au demeurant | d'ailleurs (ou supprime) |
| approche centrée utilisateur | on part de l'usage |
| solution clé en main | outil prêt à l'emploi |
| solution sur-mesure | outil maison, dev custom |
| écosystème (logiciel) | stack, outils, ensemble |
| levier (de croissance, de productivité) | moyen, façon |
| paradigme | approche, modèle |
| problématique (nom) | problème, question |
| thématique (nom) | sujet, thème |
| en termes de X | côté X, pour X |
| à l'échelle de | sur, dans |
| de manière générale | en général |
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
| permet de + verbe (chaîné) | verbe direct |
| mettre en place | installer, déployer, écrire |
| mettre en œuvre | appliquer, faire |
| faire en sorte que | pour que, s'assurer que |
| à des fins de | pour |
| jouer un rôle clé / central / déterminant | être central, compter |
| naviguer dans les défis | affronter, traiter, faire face à |
| en constante évolution | qui change, qui bouge |
| défis complexes | défis (tautologie) |
| enjeu majeur / crucial / stratégique | enjeu (préciser ce qui est en jeu) |
| décisions plus éclairées | mieux décider, décider sur données |
| de manière plus X | plus X-ment, plus X |
| digital(e) au sens de numérique | numérique |

### Tournures récemment refusées

Catalogue ouvert. Chaque entrée : tournure, pourquoi, alternative.

- **« Du coup » en début de phrase** : tic oral, pollue à l'écrit. Remplace par « donc », « alors », ou rien.
- **« En mode » + nom** : registre oral plaqué. « En mode debug » passe (terme exact), « en mode rapide » non.
- **« Grosso modo »** : flou. Préfère « en gros », « à peu près », ou donne le chiffre.
- **« Premièrement / deuxièmement / troisièmement »** : scolaire. Liste à puces, ou « d'abord… puis… enfin ».
- **« Véritablement »** : adverbe vide, signal IA fort. Supprime.
- **« Réellement »** : idem, sauf opposition explicite à « apparemment ».
- **« Particulièrement »** : flou. Remplace par un chiffre ou supprime.
- **« Notamment » sans précision derrière** : précise, ou coupe.
- **« De plus / en outre / par ailleurs » empilés** : connecteurs paresseux. Garde-en un seul.
- **« À la fin de la journée »** (calque de *at the end of the day*) : à proscrire.
- **« Au bout du compte »** : signal IA, surtout en clôture. Supprime.
- **« Faire en sorte que »** : tournure faible. « Pour que », « s'assurer que ».
- **« Mettre en place »** : verbe creux. Précise.
- **« Avoir un impact sur »** : flou. « Affecte », « ralentit », « casse », « double ».
- **« Un certain nombre de »** : faux compte. Donne le chiffre.
- **« Plusieurs »** quand tu connais le nombre : écris le nombre.
- **« Quelques »** vague : précise (3, 4, une dizaine).
- **« Il est possible de »** : passif IA. « Tu peux », « on peut ».
- **« On peut considérer que »** : hedge. Affirme ou supprime.
- **« Force de proposition »** : jargon RH. Supprime.
- **« Valeur ajoutée »** : corporate. Dis ce que ça apporte concrètement.
- **« Best practice » employé seul** : « bonne pratique » ou cite la pratique exacte.
- **« Robuste »** sans critère : précise.
- **« Scalable »** seul : précise l'axe.
- **« Pertinent »** : adjectif fourre-tout. Utile, adapté, juste, applicable.
- **« En somme / en définitive / pour conclure »** : redondant. Supprime.
- **« Il n'en demeure pas moins que »** : lourdeur. « Mais », « pourtant ».
- **« S'inscrire dans la lignée de »** : cliché. « Suit », « reprend », « continue ».
- **« S'inscrit dans une dynamique de »** : ouverture vide. Supprime.
- **« Dans une logique X »** : ouverture article tech business FR. Supprime ou nomme la logique.
- **« Colonne vertébrale »** comme métaphore corporate : terme technique précis ou supprime.
- **« Leurs propres + N »** quand « propres » est vide : supprime « propres ».
- **« X de leur choix »** quand calqué sur *X of their choice* : « choisir un outil ».

### Règles supplémentaires articles techniques

**Faits et vérifiabilité avant l'anti-IA-slop.** Ne pas supprimer version, plateforme, dépendance, source, condition de reproduction, limite de validité dans une chasse aux tournures.

- Conserver versions, plateformes, dépendances quand elles influent sur la conclusion.
- Quand on cite « documentation officielle », « tests indiquent », « l'équipe a mesuré », indiquer la source. Pas de source = ne pas écrire en mode verdict.
- Code, commande, configuration : pas de simple copie sans expliquer le paramètre clé.
- Conclusions perf / sécurité / stabilité : préciser cadre d'observation (données, environnement, échantillon).
- Expérience individuelle : ne pas la transformer en règle générale.
- Quand on présente une solution, ajouter une demi-phrase sur le périmètre : « marche pour X, à éviter pour Y ».

**Faits datés.** Prix, version, options, dates de sortie, commandes cachées : ajouter un marqueur temporel (« fin avril 2026 », « à ce jour », « vu sur la version 1.9.37 »).

**Vérifier les noms propres avant de les modifier.** Marque, produit, livre, personne, font : `grep` ou check officiel.

### Auto-vérification technique

Avant livraison, balayer ces questions :

- Quel problème précis cet article résout ?
- Versions, environnement, dépendances suffisants pour reproduire ?
- Chaque paragraphe apporte-t-il une nouvelle information ?
- Code, commandes, config expliqués sur les points clés ?
- Conclusions appuyées par évidence, données, source ?
- Risques, coûts, limites mentionnés ?
- Expérience individuelle pas étendue en loi générale ?

### Polish checklist post-N rondes — détaillée

Six catégories à scanner en clôture (la cohérence terminologique étant déjà couverte en core) :

1. **Mots redondants intra-phrase** : « aussi » + « également » dans la même phrase ; « très » + « extrêmement » ; « permet de » + « rend possible ».
2. **Phrases longues sans virgule** : phrase de 25+ mots sans pause = la respiration manque. Ajouter virgule après l'élément introductif.
3. **Métaphores non amorcées** : un terme métaphorique apparaît brusquement sans préparation (« le journal de bord », « la pile d'attente »). Si non amorcé, remplacer par le terme générique.
4. **Restes de prépositions parasites** : « au niveau de la mise en place » ; « en termes de performance » ; « dans l'optique de ». Supprimer ou remplacer.
5. **Précision sur les noms propres au premier emploi** : la première apparition lève toute ambiguïté (« Claude Code de Anthropic » puis « Claude Code »).

Tests 1 à 2 : scan visuel rapide. Tests 3 à 5 : lecture complète.

### Liste « par défaut interdit »

Référence finale. Doublonne intentionnellement les sections précédentes pour offrir un scan rapide en clôture de review.

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
- NO: à l'ère de (cliché d'intro)
- NO: dans le cadre de (en abus ; « pour », « lors de »)
- NO: au cœur de (métaphore vide ; « dans »)
- NO: au-delà de (en abus métaphorique ; « plus que », « hors »)
- NO: in fine (« finalement », ou supprimer)
- NO: véritable + N (« un véritable défi » : supprimer l'adjectif)
- NO: réel + N (« un réel enjeu » : supprimer)
- NO: véritablement (supprimer)
- NO: réellement (supprimer)
- NO: particulièrement (souvent vide)
- NO: notamment (à doser, une fois max par section)
- NO: résolument (registre marketing)
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
- NO: pour conclure (supprimer)
- NO: en somme (supprimer)
- NO: en conclusion (supprimer)
- NO: pour finir (supprimer)
- NO: X révolutionne Y (verbe-cliché)
- NO: X redéfinit Y (idem)
- NO: X bouleverse Y (idem)
- NO: X transforme Y (en abus ; préciser le mécanisme)
- NO: X réinvente Y (cliché)
- NO: X disrupte Y (jargon)
- NO: X chamboule Y (cliché)
- NO: leverager (« exploiter », « tirer parti de »)
- NO: actionner (en métaphore corporate)
- NO: onboarder (« intégrer », « accueillir »)
- NO: challenger (en abus)
- NO: scaler (en métaphore floue)
- NO: pusher une idée / roadmap (« proposer », « défendre »)
- NO: driver (en métaphore floue)
- NO: delivery (au sens corporate ; « livraison »)
- NO: bandwidth (au sens disponibilité mentale ; « temps »)
- NO: footprint (en abus métaphorique)
- NO: adresser un problème (calque ; « traiter »)
- NO: supporter une fonctionnalité (calque ; « prendre en charge »)
- NO: définitivement (au sens *definitely* ; « clairement »)
- NO: ça fait du sens (calque ; « ça a du sens »)
- NO: compléter une tâche (calque ; « terminer »)
- NO: être en charge de (calque ; « s'occuper de »)
- NO: à la fin de la journée (calque)
- NO: au bout du compte (en abus, supprimer)
- NO: tiret cadratin en ponctuation
- NO: tiret demi-cadratin en ponctuation (sauf plages numériques)
- NO: guillemets droits " " (utiliser « »)
- NO: emoji
- NO: Title Case en titres français
- NO: cet article a pour objectif de
- NO: dans ce qui suit, nous verrons
- NO: comme nous le verrons
- NO: comme nous l'avons vu (ou citer la section)
- NO: passons maintenant à
- NO: abordons à présent
- NO: voire même (pléonasme)
- NO: au jour d'aujourd'hui (pléonasme)
- NO: comme par exemple (pléonasme)
- NO: puis ensuite (pléonasme)
- NO: réitérer à nouveau (pléonasme)

### Publication externe (release notes, billet public, tweet, newsletter)

Trois vérifications supplémentaires.

**1. Anonymisation**

Pas d'éléments permettant de remonter à l'auteur : employeur, lieu, équipe, parcours. Les choix techniques peuvent être précis, l'identité reste discrète par défaut.

> NO: « En tant qu'ingénieur Backend chez X depuis 5 ans, je trouve… »
> NO: « Basé à Paris, j'ai testé… »
> OK: « En production, cette config tient X req/s. »

**2. Pas de tacle aux concurrents**

Présenter son outil sans dénigrer le voisin. Ce qu'on n'a pas, on le tait.

> NO: « Cursor indexe tout, ça pompe la RAM. Nous, on évite. »
> OK: « On n'indexe que les fichiers ouverts. »

**3. Ressenti utilisateur avant fonctionnalités**

Pour release notes ou tweet, pas une liste de features en ouverture. Donner un cas, un effet, ou un ressenti, puis détailler.

> NO: « v1.2.0 : ajout de X, correction de Y, optimisation de Z. »
> OK: « J'ai retravaillé deux choses qui me grattaient dans l'usage. La première… »
