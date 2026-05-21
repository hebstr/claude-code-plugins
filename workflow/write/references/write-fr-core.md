## Scénario français

Éliminer les tics d'écriture IA dans la prose en français, sans purisme ni chasse aux anglicismes idiomatiques. Cette référence s'applique à tout texte en français de France : article technique, billet de blog, communication produit, release note, communiqué interne ou externe.

**Sources retenues :** TLFi (cnrtl.fr) pour le sens, Le Grevisse et Riegel-Pellat-Rioul pour la grammaire, *Lexique des règles typographiques en usage à l'Imprimerie nationale* et Lacroux *Orthotypographie* pour la typographie.

**Étalons empiriques de prose humaine :** Bortzmeyer, sebsauvage, Maître Eolas, blogs d'ingénierie (OCTO, Sfeir, Doctolib). Aucune autorité descriptive sur les tics IA n'existe : observation sur sorties Claude/ChatGPT/Mistral en français vs prose humaine attestée.

**Tables exhaustives, hypercorrections, pléonasmes complets, cas limites typographiques, registres spécifiques (release notes, publication externe, ton rapport long) :** voir `references/write-fr-extended.md`.

### 1. Flux d'exécution

Six passes, dans l'ordre :

1. Préserver la sémantique. Faits, logique, causalité, intention de l'auteur restent inchangés.
2. Retirer les clôtures redondantes en fin de paragraphe (« ce qui montre que… », « on voit donc que… », « en somme… »). C'est le tic le plus fréquent et le plus invisible.
3. Lisser le rythme. Régler les phrases bancales et les ruptures inutiles.
4. Ajuster la ponctuation. Réduire parenthèses parasites, guillemets d'emphase, séries de phrases courtes.
5. Annoter les termes seulement à la première apparition.
6. Relire en entier. Corriger les points d'accroc, ne pas réécrire ce qui était déjà naturel.

### 2. Priorité : naturel > stylisé

Par défaut, ne pas changer. Préserver les tournures naturelles déjà présentes, même familières. Si l'auteur écrit « du coup » naturellement, ne pas le passer en « donc » pour gagner en formalisme. Ne pas plaquer un ton oral pour faire humain.

Désoraliser une prose orale est une décision éditoriale séparée, pas du nettoyage anti-IA-slop.

### 3. Adapter quand le public n'est pas technique

Trois choses à enlever en priorité quand le public est produit, business, ops, ou grand public :

- les jugements vers le bas (« pour les non-techniciens », « à destination du grand public ») ;
- le ton injonctif (« vous devez », « il faut absolument ») ;
- le jargon profond non expliqué.

Logique « voici ce que je fais, fais pareil », pas « voici l'analyse systémique du domaine ».

### 4. Ouvertures directes

Pas de mise en bouche. Conclusion d'abord, raisonnement ensuite. Cas concret avant généralisation, et seulement si la généralisation est nécessaire.

> NO: « Au cours des dernières années, l'intelligence artificielle a profondément transformé… »
> OK: « J'ai migré notre pipeline d'ingestion de pandas à polars. Le job qui prenait 40 minutes en prend 90 secondes. »

### 5. Vocabulaire formel à dégonfler

Le vocabulaire pompeux ne donne pas de l'autorité, il donne du bruit. Préférer le mot court.

| Évite | Préfère |
|---|---|
| à l'instar de | comme |
| par conséquent | donc |
| afin de, dans le but de | pour |
| dans la mesure où | parce que, puisque |
| il est nécessaire de | il faut |
| de manière significative | beaucoup, fortement |
| effectuer une vérification | vérifier |
| mettre en place | installer, configurer, écrire, déployer |
| permettre de + verbe (chaîné) | verbe direct (« permet de réduire » → « réduit ») |

### 6. Anglicismes : garde ou traduis

Le français technique de France absorbe les anglicismes idiomatiques depuis quarante ans. La cible n'est pas l'anglais, c'est l'IA-slop.

**Test de jugement, trois questions :**

1. Le terme apparaît-il dans la prose technique de mes pairs (collègues, doc française d'outils, articles francophones, discussions Stack Overflow FR) ? Si oui, garde-le.
2. Existe-t-il un équivalent français aussi compact et précis ? Si non, garde l'anglicisme. Si oui mais que personne ne l'emploie en pratique (« cadriciel »), garde quand même l'anglicisme.
3. Est-ce un verbe en `-er` greffé sur un verbe anglais pour sonner moderne (leverager, actionner, driver, challenger) ? Si oui, traduis.

**Préservés** (échantillon) : framework, runtime, deploy, debug, push, ship, refactor, mock, scope, log, parser, build, embedding, pipeline, stack, commit, merge, rollback, prompt, token, backend, frontend, benchmark, lifecycle, payload, binding.

**Traduits** : leverager → exploiter ; onboarder → intégrer ; driver → piloter ; challenger → remettre en question ; pusher (une idée) → défendre ; scaler (en métaphore) → passer à l'échelle ; ownership → responsabilité ; mindset → état d'esprit.

### 7. Calques structurels (faux amis)

Plus pernicieux que les anglicismes lexicaux : un mot français existant prend le sens de l'anglais. Le résultat passe le filtre orthographique mais sonne traduit.

| Évite | Préfère |
|---|---|
| adresser un problème | traiter, aborder, s'attaquer à |
| supporter une fonctionnalité | prendre en charge, gérer |
| définitivement (= certainly) | certainement, clairement |
| ça fait (du) sens | c'est cohérent, ça se tient |
| en charge de | chargé de, responsable de |

### 8. Pas de surajout oral

À ne pas plaquer sur une prose neutre quand le but est de « sonner humain » : « du coup » en début de phrase, « en mode » + nom hors contexte technique, « grosso modo » (préférer un chiffre), « j'avoue », « carrément », « pour le coup », « en gros » comme cheville.

Garder ce que l'original avait déjà si naturel. Ajouter ces tournures = sur-oraliser, c'est un tic IA en miroir du tic académique.

### 9. Concrétisation prudente

Si la phrase originale est claire, ne pas la rendre « plus imagée ». Concrétiser seulement quand l'original est trop abstrait pour être compris à la première lecture par un lecteur du métier.

Une métaphore par paragraphe maximum. Jamais filée sur trois pages.

### 10. Structures de phrases

- Pas de « premièrement / deuxièmement / troisièmement » en prose. Soit liste à puces, soit « d'abord / puis / enfin » si vraiment nécessaire.
- Phrases complètes, sujet-verbe-complément. Pas de fragments pour faire dramatique.
- Pas de phrases courtes en chaîne. Quatre phrases courtes consécutives = ton télégramme. Combiner deux d'entre elles avec une virgule ou un connecteur.
- Pas de question rhétorique pour cadrer le lecteur. Affirmer.
- Pas de tiret cadratin (—) ni demi-cadratin (–) en ponctuation interne. <!-- prose-lint:ignore --> Virgule, deux-points, parenthèses, ou restructure.
- Pas de triplet forcé. Si la relation est serrée, écrire en phrase, pas en liste. Deux items suffisent souvent.

### 11. Conception des titres

Pas de Title Case anglais : capitale initiale + noms propres seulement.

Titre avec verdict, pas thème seul. Un titre devrait pouvoir tenir comme phrase brève qui prend position.

> NO: « Architecture Multi-Format Via Un Seul Fichier »
> OK: « Architecture multi-format via un seul fichier »

> NO: « Multi-agents et hallucinations » (juste un thème)
> OK: « Le multi-agents amplifie les hallucinations »

### 12. Typographie essentielle

Quatre points non négociables :

- **Capitales accentuées obligatoires.** État, École, À bientôt, Île-de-France. Le Lexique IN est explicite.
- **Pas de tiret cadratin (—) ni demi-cadratin (–) en ponctuation.** <!-- prose-lint:ignore --> Le demi-cadratin sert uniquement aux plages numériques (`pages 12–18`, `2020–2024`) et aux dialogues littéraires. <!-- prose-lint:ignore --> En prose, virgule, deux-points, parenthèses.
- **Guillemets français « » avec espace insécable interne.** Jamais `" "` ni `" "` américains en prose finale.
- **Apostrophe courbe `'` en prose, droite `'` en code.** « l'API » en prose, `data['key']` en code.

Voir `write-fr-extended.md` pour : espaces fines, sigles, énumérations, citations longues, italique, pourcentages, nombres.

### 13. Tics IA récurrents

Douze patterns à éliminer par défaut. Si ta prose en contient plus de deux ou trois, réécris.

1. **Sublimation.** L'observation technique promue en vérité universelle.
   > NO: Ce bug révèle une vérité plus profonde sur la nature même du logiciel.
   > OK: Ce bug vient d'un cache mal invalidé.

2. **Parallélisme négatif.** Le tic n°1. « Ce n'est pas X. C'est Y. »
   > NO: Ce n'est pas un simple outil. C'est une nouvelle façon de penser.
   > OK: C'est un linter avec un mode auto-fix.

3. **Question rhétorique auto-répondue.**
   > NO: Le résultat ? Spectaculaire.
   > OK: La latence passe de 800 ms à 40 ms.

4. **Triplet ou binôme symétrique vide.**
   > NO: C'est rapide, fiable et élégant. / Une technologie innovante, performante et flexible.
   > OK: C'est rapide et fiable. (ou : précise ce qu'elle fait)

5. **Conclusion impérative.** « L'enjeu est clair : … », « Une chose est sûre : … ».
   > NO: Une chose est sûre : l'observabilité n'est plus optionnelle.
   > OK: Sans logs structurés, tu débugges à l'aveugle.

6. **Clôture redondante.** Dernière phrase qui répète le paragraphe.
   > NO: …et c'est ainsi que le cache se réchauffe en arrière-plan. En somme, le cache se réchauffe sans bloquer la requête.
   > OK: Coupe la deuxième phrase.

7. **Tournures rituelles.** « Force est de constater », « il convient de noter », « il importe de souligner », « il est intéressant de remarquer ».
   > NO: Force est de constater que les tests passent.
   > OK: Les tests passent.

8. **Cadres passe-partout.** « À l'aune de », « à l'heure où », « dans le cadre de », « au cœur de ».
   > NO: À l'heure où l'IA transforme nos métiers, il convient de repenser nos pipelines.
   > OK: Les LLM changent nos pipelines de doc. Voici comment on adapte le nôtre.

9. **« Véritable » ou « réel » + nom.** Modificateur vide.
   > NO: Un véritable défi, un réel enjeu, une véritable révolution.
   > OK: Un défi. Un enjeu. (ou supprime le nom et précise)

10. **Verbes-clichés de transformation.** « Révolutionne », « redéfinit », « bouleverse », « réinvente ».
    > NO: Polars révolutionne le traitement de données en Python.
    > OK: Polars est 5 à 30 fois plus rapide que pandas sur nos jobs.

11. **Annonce de ce qu'on va dire.** « À noter que », « notons que », « précisons que », « soulignons que ».
    > NO: Notons que cette approche a un coût mémoire.
    > OK: Cette approche coûte 2 Go de RAM en plus.

12. **Adverbes d'intensité empilés.** « Particulièrement », « extrêmement », « véritablement », « résolument ».
    > NO: Cette approche est particulièrement et résolument tournée vers la performance.
    > OK: Cette approche vise la perf.

### 14. Ton inductif vs verdict

Signaler le degré de certitude. « X cause Y » claque comme verdict définitif. Préférer le ton inductif quand l'observation est partielle.

> NO: Cette pratique élimine le problème.
> OK: Sur nos jobs, cette pratique a éliminé le problème.

Préserver les pondérations de l'auteur. Si l'auteur a écrit « semble », ne pas passer en « est ».

### 15. Pléonasmes fréquents

- voire même → voire (« voire » signifie déjà « et même »)
- au jour d'aujourd'hui → aujourd'hui (triple marquage temporel)
- comme par exemple → comme OU par exemple (synonymes)
- puis ensuite → puis OU ensuite (succession temporelle redondante)
- ajouter en plus → ajouter (l'addition est dans le verbe)

### 16. Règles éprouvées

Quatre méta-règles, prioritaires sur les préférences de style :

- **Sémantique d'abord, IA-slop ensuite.** Une réécriture qui change le sens ou le degré de certitude est un échec, peu importe si elle sonne plus naturelle.
- **Supprimer une phrase entière vs réécrire.** Si une phrase ne porte que du slop (cliché, parallélisme négatif, intensifieur vide), supprimer. Si elle contient une donnée chiffrée, un nom propre, une condition technique, une cause précise, réécrire en gardant le fait.
- **Conclusion centrale dite une fois.** Si elle a été énoncée en intro, ne pas la reformuler en clôture.
- **Tensions internes de l'auteur à préserver.** Si l'auteur tient des positions apparemment contradictoires (libre vs structuré, vite vs propre), ne pas trancher pour lui.

### 17. Langue de bois corporate

Tournures de cabinet de conseil et de blog SEO IA. Cross-registre, dégradent autant un article technique qu'une release note ou un communiqué.

| Évite | Préfère |
|---|---|
| au cœur de | dans, central à |
| à l'aune de | selon, d'après |
| à l'heure où | aujourd'hui, alors que (ou supprime) |
| force est de constater | on voit que (ou supprime) |
| dans le cadre de | pour, lors de, pendant |
| mettre en place | installer, déployer, écrire |
| jouer un rôle clé / central | être central, compter |
| en constante évolution | qui change (ou supprime) |

### 18. Cohérence terminologique

Un seul terme pour un concept dans tout le texte. Pas « cache » → « mémoire tampon » → « buffer » pour la même chose. Le synonyme involontaire force le lecteur à se demander si la nuance est intentionnelle.

---

### Bilan

Prose qui se lit comme un humain qui pense à voix haute. Pas un manuel, pas un communiqué, pas un cours, pas un pitch. Si une phrase pourrait apparaître sur LinkedIn telle quelle, elle ne va probablement pas dans la prose visée, quel que soit le registre.

Une trope unique, employée une fois, ne pose pas de problème. Le tell IA apparaît quand plusieurs se cumulent, ou qu'une seule revient en boucle.
