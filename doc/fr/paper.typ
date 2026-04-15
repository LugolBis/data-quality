#import "@preview/algo:0.3.6": algo, code, comment, d, i
#import table: cell, header

#set page(
  numbering: "1",
  number-align: center + bottom,
)

#set align(left)
#set text(
  lang: "fr",
)

#set heading(numbering: "1.1 -")

#set par(justify: true)

#let code = content => block(
  [#text(content, font: "JetBrains Mono", size: 10pt)],
  fill: luma(230),
  radius: 4pt,
  inset: 10pt,
  width: 100%,
)

#let alinea = [#h(1.5em)]

*Abstract*: L'état de l'art des *Graphes de Propriété*...

= Introduction

#alinea Cette étude a pour objectif de déterminer des critères de qualité de donnée pour les bases de données graphe. On considerera ici les *Graphes de Propriété* (_Property Graph_) disposant d'*étiquettes* (_labels_).

*Définition 1.*\
#alinea Un graphe de propriété est un tuple $G = (N, E, rho, lambda, sigma)$ tel que :
+ $N$ est un ensemble fini de noeuds (_nodes_), aussi appellé sommets (_vertices_).
+ $E$ est un ensemble fini d'arc (on parlera d'arrête lorsque la direction n'est pas prise en compte).
+ $rho: E -> (N times N)$ est une fonction totale qui associe pour chaque arc dans $E$ une pair $(n_"source", n_"destination")$. Cette pair de noeuds est donc non commutative car $(n_A, n_B) in rho(E)$ n'implique pas nécessairement $(n_B, n_A) in rho(E)$.
+ $lambda: (N union E) -> "SET"^+(L)$ est une fonction partielle qui associe a un noeud ou un arc un ensemble d'étiquettes incluses dans $L$ ($lambda$ est une fonction d'étiquetage des noeuds et des arcs).
+ $sigma: (N union E) times P -> "SET"^+(V)$ est une fonction partielle qui associe aux noeuds et arcs des valeurs $V$ aux propriétées $P$. On notera par la suite, $forall (o, p) in (N union E) times P$ et ses valeurs assignées $sigma(o, p) = {v_1, ..., v_n}$ par $(o, p) = arrow(v)$.

= Qualité de donnée d'un Graphe de Propriété
== Complétude
*Définition 2.1.0*\
#alinea La Complétude mesure la quantité de données manquantes d'une base de données graphe @cai2016challenges.

=== Existence de composantes
#alinea L'existence de composantes connexes ou fortement connexes est une méthode pour vérifier la complétude des données. De fait les arcs modélisent une grande partie des relations entre les objets et sont porteurs d'un sens sémantique important.\
#alinea Plus intuitivement vérifier l'existance de composantes entre des ensembles de noeuds et d'arcs permet par exemple d'exprimer des contraîntes de chemins (resp. chaînes). Naturellement l'ajout de contraintes comme la longueur des chemins, l'appartenance d'un ensemble d'étiquettes à ceux-ci constitutent de solides outils pour capturer un sens sémantique complexe.

*Définition 2.1.1*\
#alinea Soit $G_p$ un graph pattern (_patron de graphe_) modélisant une composante connexe (resp. fortement connexe), un ensemble $O$ tel que $O in {N, E, N union E}$ et $L_O subset.eq L$ est un ensemble d'étiquettes. Tel que $forall (G_p, O, L_O)$ on a $forall o in O$ tel que $lambda(o) = L_O$, $exists$ au moins une occurence de $G_p$ pour $o$.

=== Le degré des noeuds
#alinea La complétude des données peut aussi s'exprimer par le degré des noeuds et ainsi exprimer des contraintes de cardinalitées.

*Définition 2.1.2*\
#alinea Soit $L_O subset.eq L$ est un ensemble d'étiquettes et les ensembles $D_s, D_e subset RR^2$, représentant respectivement l'ensemble des degrés sortant et entrant. Tel que $forall n in N$ tel que $lambda(n) = L_O$ vérifie $d^+(n) in D_s$ et $d^-(n) in D_e$.

== Conformité
*Définition 2.2.0*\
#alinea La Conformité mesure la validité du format des données.

=== Format des chaînes de caractère
*Définition 2.2.1*\
#alinea Soit $O in {N, E, N union E}$, $L_O subset.eq L$, $X subset.eq P$ et *Regex* codant le format attendu. Tel que $forall o in O$ on vérifie que $forall v in sigma(o, X)$, $"match"(v, "Regex") = "Vrai"$.

=== Format des dates
*Définition 2.2.2*\
#alinea Soit $O in {N, E, N union E}$, $L_O subset.eq L$, $X subset.eq P$ et *$"Date"_"fmt"$* codant le format de date attendu. Tel que $forall o in O$ on vérifie que $forall v in sigma(o, X)$, $"match"(v, "Date"_"fmt") = "Vrai"$.

=== Ensemble fini de données
*Définition 2.2.3*\
#alinea Soit $O in {N, E, N union E}$, $L_O subset.eq L$, $X subset.eq P$, $I$ un ensemble de données (non atomique comprises) et $C$ une contrainte optionnelle (cf. @def2.3.2[Définition]). Tel que $forall o in O$ on vérifie $"SET"(sigma(o, X)) subset.eq I and C(o) = "Vrai"$.

=== Étiquetage Ensembliste
*Définition 2.2.4*\
#alinea Soit $O in {N, E, N union E}$, $L_X, L_Y subset.eq L$ et $"Op"_"ens" in { subset, subset.eq, \\ }$ un opérateur ensembliste. Tel que $forall o in O$ tel que $L_X subset.eq lambda(o)$ vérifie $lambda(o) "Op"_"ens" L_Y = "Vrai"$.

#alinea Notons que seule l'implémentation partielle de cette définition à du sens dans le cadre de la base de donnée graphe *Neo4j*, car les arcs (_Relationships_) ne peuvent avoir qu'une seule étiquette.

=== Étiquetage par Regroupement (clustering)
#alinea L'intuition est la suivante : des noeuds similaire doivent avoir le même ensemble d'étiquettes. Pour mesurer la qualité de l'étiquetage on cherche donc à regrouper les noeuds similaire pour détecter les erreurs d'étiquetage. L'approche qui suit est inspiré d'un système d'embeddings motivé par l'article @Giot2015VisualGraph. L'approche proposée est la suivante :
+ #alinea Déterminer un critère de similarité entre deux noeuds : on s'intéresse ici aux étiquettes des noeuds donc au sens sémantique de celles-ci. Notre intérêt se porte donc sur les relations entre les différents ensembles d'étiquettes. Ces relations sont ici modélisées par un concept riche en sémantique : les arcs. En effet les arcs sont caractérisés par une pair de noeuds (disposant d'une direction) et un ensemble d'étiquettes. On propose donc de traduire ce sens sémantique par des chaînes de caractère. Ainsi l'arc suivant :\
  #code([($"Noeud"_1$: {Étudiant,Personne})-[$"Arc"$:{Inscrit}]->($"Noeud"_2$: {Université})])
  Serait traduit par "OUT:Inscrit:Université" (que l'on nomme un _Token_) du point de vu de $"Noeud"_1$ et par "IN:Inscrit:ÉtudiantPersonne" de celui de $"Noeud"_2$.
+ #alinea Déterminer une méthode de calcul de similarité entre deux _Token_. Sachant qu'un _Token_ traduit des relations sémantiques complexe par une chaîne de caractère, l'utilisation de distance d'édition (_Edit distance_) semble le plus adapté. On utilise donc la similarité de *Levenshtein* pour calculer la similarité entre deux _Token_.
+ #alinea Déterminer une méthode de calcul de similarité entre deux noeuds. On s'intéresse à leurs relations et à leurs étiquettes on va donc combiner un score de similarité de ces deux dimensions. On utilise l'indice de *Jacard* pour calculer la similarité entre deux noeuds sur le critère des ensembles détiquettes, tel qu'on a $forall n_1, n_2 in N^2$, $"Similarité"_"Étiquettes" = (|lambda(n_1) inter lambda(n_2)|)/(|lambda(n_1) union lambda(n_2)|)$.\
  On définit $"tokens": N -> "SET"("Tokens")$ une fonction partielle qui associe à un noeud son ensemble de _Tokens_. La similarité entre deux noeuds sur le critère des _Tokens_ est calculée comme suit, $forall n_1, n_2 in N^2$, $"Similarité"_"Tokens" = (sum_(i = 0)^(|"tokens"(n_1)|) sum_(j = 0)^(|"tokens"(n_2)|) "Similarité_Levenshtein"("tokens"(n_1)_i, "tokens"(n_2)_j))/(|"tokens"(n_1)| + |"tokens"(n_2)|)$.

On définit donc les algorithmes suivant :\
#alinea L'algorithme _Tokenization_ permet de générer un ensemble de _Token_ (représentant les relations d'un noeud) pour tous les noeuds tel qu'il existe un arc entrant ou sortant de ceux-ci. Autrement formulé : tout noeud ayant un degré entrant ou sortant non nul dispose d'une propriété "Tokens" sauvegardant l'ensemble de des _Token_ générés le concernant.\
#alinea L'algorithme _CreateTokens_ quant à lui génère un ensemble de noeud connexe représentant l'ensemble des _Token_ distinct générés par l'algorithme _Tokenization_. Une fois ces noeuds créés l'algorithme _CreateTokens_ calcule la similarité de *Levenshtein* entre chaque pair de _Token_ et la sauvegarde sous forme d'arc entre ceux-ci.

#let Tokenization = [#algo(
  main-text-styles: (size: 11pt),
  block-align: none,
  title: [#text(size: 12pt)[Tokenization]],
  parameters: (
    [#text(size: 12pt)[$G$ PG.]],
  ),
  indent-size: 8pt,
  indent-guides: 1pt + gray,
  row-gutter: 6pt,
  column-gutter: 5pt,
  inset: 8pt,
  stroke: 2pt + black,
  breakable: false,
)[
  #comment("Étape - 1", inline: true)\
  for $e$ in $E$ do#i\
  $(n_s, n_d) <- rho(e)$\
  $c_s <-$ 'OUT:' $+ lambda(e) +$ ':' $+ lambda(n_d)$\
  $c_d <-$ 'IN:' $+ lambda(e) +$ ':' $+ lambda(n_s)$\
  $t_s <- sigma(n_s, {"Tokens"})$\
  $t_d <- sigma(n_d, {"Tokens"})$\
  $sigma(n_s, {"Tokens"}) <- t_s union c_s$\
  $sigma(n_d, {"Tokens"}) <- t_d union c_d$#d\
  end
]]

#let CreateTokens = [#algo(
  main-text-styles: (size: 11pt),
  block-align: none,
  title: [#text(size: 12pt)[CreateTokens]],
  parameters: (
    [#text(size: 12pt)[$G$ PG.]],
  ),
  indent-size: 8pt,
  indent-guides: 1pt + gray,
  row-gutter: 6pt,
  column-gutter: 5pt,
  inset: 8pt,
  stroke: 2pt + black,
  breakable: false,
)[
  #comment("Étape - 2", inline: true)\
  $"vocab" <- emptyset$\
  for $n$ in $N$ do#i\
  $"tokens" <- sigma(n, {"Tokens"})$\
  if $"tokens" eq.not "NULL"$ do#i\
  $"vocab" <- "vocab" union "tokens"$#d#d\
  for $"idx"$ in $[0;|"tokens"|-1]$ do#i\
  $n <- "newNode"()$\
  $N <- N union {n}$\
  $lambda(n) <- {"TOKEN"}$\
  $sigma(n, {"VAL", "ID"}) <- ("vocab"["idx"], "idx")$#d\
  #comment("On calcule la similarité entre les tokens.", inline: true)\
  for $(n_1, n_2)$ in $N^2$ do#i\
  if $lambda(n_1) = lambda(n_2) = {"TOKEN"}$\
  and $sigma(n_1, {"ID"}) < sigma(n_2, {"ID"})$ do#i\
  $"t1", "t2" <- sigma(n_1, {"VAL"}), sigma(n_2, {"VAL"})$\
  $"sim" <- "Similarité_Levenshtein"("t1", "t2")$\
  $e <- "newEdge"()$\
  $E <- E union {e}$\
  $rho(e) <- (n_1, n_2)$\
  $lambda(e) <- {"SIMILAR"}$\
  $sigma(e, {"SCORE"}) <- "sim"$#d#d\
  end
]]

#let Merge = [#algo(
  main-text-styles: (size: 11pt),
  block-align: none,
  title: [#text(size: 12pt)[Merge]],
  parameters: (
    [#text(size: 12pt)[$G$ PG., $t_e$ seuil similarité étiquettes, $t_t$ seuil similarité Tokens]],
  ),
  indent-size: 8pt,
  indent-guides: 1pt + gray,
  row-gutter: 6pt,
  column-gutter: 5pt,
  inset: 8pt,
  stroke: 2pt + black,
  breakable: false,
)[
  #comment("Étape - 3 : Détection de noeuds qui devraient appartenir", inline: true)\
  #comment("au même cluster d'étiquettes.", inline: true)\
  for $(n_1, n_2)$ in $N^2$ do#i\
  if $sigma(n_1, {"ID"}) < sigma(n_2, {"ID"})$\
  and $sigma(n_1, {"Tokens"}) != "NULL"$\
  and $sigma(n_2, {"Tokens"}) != "NULL"$ do#i\
  $"Similarité"_"Étiquettes" <- (|lambda(n_1) inter lambda(n_2)|)/(|lambda(n_1) union lambda(n_2)|)$\
  if $"Similarité"_"Étiquettes" >= t_e$ do#i\
  skip this iteration;#d\
  end\
  \
  $"Similarité"_"Tokens" <- 0.0$\
  for $"token"_1$ in $sigma(n_1, {"Tokens"})$ do#i\
  $"nt"_1 <- n in N "where" lambda(n) = {"Token"} and sigma(n, {"VAL"}) = "token"_1$\
  for $"token"_2$ in $sigma(n_2, {"Tokens"})$ do#i\
  $"nt"_2 <- n in N "where" lambda(n) = {"Token"} and sigma(n, {"VAL"}) = "token"_2$\
  $e <- e in E "where" rho(e) in {("nt"_1, "nt"_2), ("nt"_2, "nt"_1)}$\
  $"Similarité"_"Tokens" <- "Similarité"_"Tokens" + sigma(e, {"SCORE"})$#d#d\
  end\
  $"Similarité"_"Tokens" <- "Similarité"_"Tokens" + sigma(e, {"SCORE"})$\
  if $"Similarité"_"Tokens" >= t_t$ do#i\
  $e <- "newEdge"()$\
  $E <- E union {e}$\
  $rho(e) <- (n_1, n_2)$\
  $lambda(e) <- {"MERGE"}$#d#d\
  end#d\
  end
]]

#let Split = [#algo(
  main-text-styles: (size: 11pt),
  block-align: none,
  title: [#text(size: 12pt)[Split]],
  parameters: (
    [#text(size: 12pt)[$G$ PG., $t_e$, $t_t$]],
  ),
  indent-size: 8pt,
  indent-guides: 1pt + gray,
  row-gutter: 6pt,
  column-gutter: 5pt,
  inset: 8pt,
  stroke: 2pt + black,
  breakable: false,
)[
  #comment("[...]", inline: true)\
  #comment("Ligne 8 :", inline: true)\
  if $"Similarité"_"Étiquettes" <= t_e$ do\
  #comment("[...]", inline: true)\
  #comment("Ligne 21 :", inline: true)\
  if $"Similarité"_"Tokens" >= t_t$#i\
  #comment("[...]", inline: true)\
  #comment("Ligne 25 :", inline: true)\
  $lambda(e) <- {"SPLIT"}$#d\
]]

#grid(
  columns: (0.9fr, 1.1fr),
  gutter: 1em,
  [
    #Tokenization
    #alinea L'algorithme _Tokenization_ à une complexité temporelle linéaire en $O(n)$ (avec $n = |E|$) et une complexité spatiale dans le pire cas en $O(n times m)$ (avec $n = |N|$ et $m = |L|$). L'algorithme _CreateTokens_ à une complexité temporelle polynomiale en $O(n^2)$ (avec $n = |N|$) et une complexité spatiale dans le pire cas (très rare) en $O(n^2)$ (avec $n = |N| + |E|$).
  ],
  [
    #CreateTokens
  ],
)

#alinea Une fois les algorithmes _Tokenization_ et _CreateTokens_ ont peut analyser les regroupement de noeuds avec leur similarité entre ensemble de _Token_, et sur la similarité de *Jacard* pour calculer la similarité entre leur étiquettes. Le regroupement s'effectue par paire de noeuds et on ne sauvegarde qu'un simple arc liant les noeuds qui devraient être "Merge" (ceux-ci devraient avoir un ensemble similaire d'étiquettes) ou "Split" (ceux-ci ne devraient pas avoir un ensemble similaire d'étiquettes). Cette sélection est déterminée à partir de deux seuils de similarité, le premier concerne la similarité entre les étiquettes (cela permet de filtrer les pairs de noeuds qui pourraient être intéressantes). Ainsi qu'un deuxième seuil concernant la similarité des _Tokens_ et qui à un impact direct sur la création ou non d'un arc "Merge" / "Split".

#Merge

#alinea L'algorithme _Merge_ détaillé ci-dessus permet donc de détecter toutes les pairs de noeuds dont la similarité des étiquettes est $<$ au seuil $t_e$; et pour lesquelles la similarité des _Token_ est $>=$ au seuil $t_t$. En d'autre terme l'algorithme détecte les noeuds qui de part leur similarité de relations (_Token_), devraient avoir un ensemble d'étiquettes plus similaire (donc ils devraient être rassemblés).

#grid(
  columns: (1fr, 1fr),
  gutter: 1em,
  [
    #alinea Cet algorithme peut être aisément modifié pour détecter l'inverse : "Split" désignant les pairs de noeuds qui ne devraient pas avoir des ensemble d'étiquettes aussi similaire. Pour opérer les changement nécessaire il suffirait de modifier comme suit les lignes [8, 21, 25] de l'algorithme _Merge_.
  ],
  [
    #Split
  ],
)

== Cohérence
*Définition 2.3.0*\
#alinea La Cohérence mesure la validité des relations de la base de données graphe.

=== Dépendance Fonctionnelle (FD)
#label("def2.3.1")
*Définition 2.3.1*\
#alinea Soit $O in {N, E, N union E}$, $L_O subset.eq L$ et $X, Y subset.eq P$, on définit par $(O, L_O, X -> Y)$ une *FD*. Tel que $forall o_1, o_2 in O^2$ tel que $lambda(o_1) = L_O$ et $lambda(o_2) = L_O$ vérifie $sigma(o_1, X) = sigma(o_2, X) arrow.double sigma(o_1, Y) = sigma(o_2, Y)$.

=== Dépendance Fonctionnelle Conditionnelle (CFD)
#label("def2.3.2")
*Définition 2.3.2*\
#alinea Une *condition* est un tuple $C = (P_C, "VAL", f, "NEXT")$ tel que :
+ $P_C subset.eq P$ est l'ensemble des propriétées devant respecter la condition.
+ $"VAL" in {"constante", P}$ est la valeur de comparaison. La "constante" peut être tout type de données (non atomique comprises).
+ $f: (N union E, P_C, "VAL") -> "Booléen"$, est une fonction permetant de vérifier la condition sur un objet (ex. "$=$", "$<$", "$in$", etc.). On notera par la suite $C(o)$ le fait que l'objet $o$ vérifie $f(o, P_C, "VAL")$ sachant $P_C$ et $"VAL"$ définit dans $C$.
+ $"NEXT" in {emptyset, ("Condition", "Opérateur booléen")}$ est une deuxième condition (optionnelle) devant être vérifiée (permettant ainsi de la combiner avec la première avec l' "Opérateur booléen").
*Définition 2.3.3*\
#alinea Soit $O in {N, E, N union E}$, $L_O subset.eq L$, $C$ une condition (cf. @def2.3.2[Définition]) et $X, Y subset.eq P$, on définit par $(O, L_O, C, X -> Y)$ une *CFD*. Tel que $forall o_1, o_2 in O^2$ tel que $lambda(o_1) = L_O$ et $lambda(o_2) = L_O$ et $C(o_1) = "Vrai"$ et $C(o_2) = "Vrai"$ vérifie $sigma(o_1, X) = sigma(o_2, X) arrow.double sigma(o_1, Y) = sigma(o_2, Y)$.

=== Dépendance d’un Graph pattern (GFD)
*Définition 2.3.4*\
#alinea Soit $G_p$ un graph pattern à partir duquel on déduit $G'(N', E')$, sous graphe de $G$ correspondant à $G_p$; $O in {N, E, N union E}$, $L_O subset.eq L$ et $X, Y subset.eq P$, on définit par $(O, L_O, G_p, X -> Y)$ une *GFD*. Tel que $forall o_1, o_2 in O^2$ tel que $o_1, o_2 in G'$ vérifie $sigma(o_1, X) = sigma(o_2, X) arrow.double sigma(o_1, Y) = sigma(o_2, Y)$.\
Une autre approche (très différente) nommé _gFD_ @Manouvrier2024PGFD consiste a exclure tous les noeuds qui n'ont pas toutes les propriétées ($X union Y$) définit par la _FD_.

=== Validation par requête
#alinea Les dépendances fonctionnelles (_FD_, _CFD_ et _GFD_) sont des outils très puissant. Mais ils sont complexe à étendre pour parvenir à capturer l'ensemble du sens sémantique offert par les requêtes. C'est pourquoi une approche de validation supplémentaire consisterai --- sur le modèle de _dbt_ --- à valider ou invalider des requêtes écrites par l'utilisateur.\
*Définition 2.3.5*\
#alinea Ce système de validation par requête est défini par un tuple _dgt_ $= (R, B)$ tel que :
+ $R$ est une requête, aussi riche que le language de requêtage le permet; qui renvoie (ou non) des objets.
+ $B$ est un booléen indiquant si $R$ doit renvoyer des objets pour valider la contrainte définit par celle-ci.

== Intégrité
*Définition 2.4.0*\
#alinea L’intégrité mesure la validité structurelle d'une base de données graphe.

=== Validité du schéma de propriété
#alinea Dans l'état de l'art aucun standard _DDL_ n'a émergé pour les bases de données graphe. On va donc définir trois contraintes d'intégrité :
+ *Unicité de propriétés* :\
  Soit $O in {N, E, N union E}$, $L_O subset.eq L$ et $X subset.eq P$ tel que on vérifie que $forall o_1, o_2 in O^2$ vérifie $sigma(o_1, X) = sigma(o_2, X) arrow.double o_1 = o_2$.
+ *Existence de propriétés* :\
  Soit $O in {N, E, N union E}$, $L_O subset.eq L$ et $X subset.eq P$ tel que on vérifie que $forall o in O$ vérifie $"NULL" in.not sigma(o, X)$.
+ *Type des valeurs de propriétés* :\
  Soit $t: (V) -> "SET"^+(T)$ une fonction totale qui attribut un ensemble de type $T$ à un ensemble de valeurs $V$, $O in {N, E, N union E}$, $L_O subset.eq L$, $X subset.eq P$ et $Y subset.eq T$ tel que on vérifie que $forall o in O$ vérifie $(t compose sigma)(o, X) subset.eq Y$.
Notons que ces contraintes peuvent être définies en *Cypher* (le language de requếtes de *Neo4j*).
=== Validité des Index
#alinea L'intuition est la suivante : des valeurs manquante sur des propriétés indexées peuvent être un signal de dégradation de l'intégrité de la base de donnée graphe.\
*Définition 2.4.1*\
#alinea Soit $i: (N times E) -> "BITSET"$ des propriétées indexées, $forall o in (N union E)$ on vérifie $"NULL" in.not i(o) dot.o sigma(o, P)$.

=== Forme normale d'un Graphe de propriété
Algorithme :\

#let PG_3FN = [#algo(
  main-text-styles: (size: 11pt),
  block-align: none,
  title: [#text(size: 12pt)[PG_3FN]],
  parameters: (
    [#text(size: 12pt)[$G$ PG.,$F$ FD set,$L$ Label set]],
  ),
  indent-size: 8pt,
  indent-guides: 1pt + gray,
  row-gutter: 6pt,
  column-gutter: 5pt,
  inset: 8pt,
  stroke: 2pt + black,
  breakable: false,
)[
  $F_min <- "get_min_cover"(F)$\
  $D <- emptyset$\
  $forall (X -> A)$ in $F_min$:#i\
  $F_x <- F_min - {(X->A)}$\
  if ($F_x models X -> A$):#i\
  $F_min <- F_x$#d\
  else#i\
  $D <- D union {("XA", F_min."projection"("XA"))}$#d#d\
  $F^+ <- "atomic_closure"(F)$\
  $'"LoopA" forall R_p$ in $F^+$:#i\
  $forall (R, F_r)$#i\
  if $(R -> "RP") in F^+$:#i\
  continue $'"LoopA"$#d#d\
  $"key" <- "find_key"(R_p, F^+)$\
  $D <- D union {("key", F_min."projection"("key"))}$
]]

#let Min_cover_fn = [#algo(
  main-text-styles: (size: 11pt),
  block-align: none,
  title: [#text(size: 12pt)[get_min_cover]],
  parameters: (
    [#text(size: 12pt)[$F$ FD set]],
  ),
  indent-size: 8pt,
  indent-guides: 1pt + gray,
  row-gutter: 6pt,
  column-gutter: 5pt,
  inset: 8pt,
  stroke: 2pt + black,
  breakable: false,
)[
  $F_min <-$ min_cover($F$)\
  $forall$ $(X -> A)$ in $F_min$:#i\
  $F_x <- F_min - {(X->A)}$\
  $forall$ $(X -> B)$ in $F_x$:#i\
  if ($"YB" subset.eq "XA"$)\ and ($"XA" subset.eq.not Y^+$)\ and ($F_x models X -> A$):#i\
  $F_min <- F_x$#d#d#d\
  return $F_min$
]]

#grid(
  columns: (1.2fr, 0.8fr),
  gutter: 1em,
  [
    #PG_3FN
  ],
  [
    #Min_cover_fn
  ],
)

#alinea L'algorithme est définit dans le cadre des *gFD* et *gUC* @Skavantzos2023Normalization que l'on peut facilement traduire par les *FD* (cf. @def2.3.1[Définition]). Tandis que les *CFD* et les *GFD* (graph pattern FD), semblent avoir moins de sens dans un contexte de normalisation car l'algorithme normaliserai en 3NF seulement un fragment de la base de donnée.

== Unicité
*Définition 2.5.0*\
#alinea L'unicité mesure la redondance d'une base de données graphe.

=== Doublons d'arcs
*Définition 2.5.1*\
#alinea $forall e_1, e_2 in E^2$, $e_1$ et $e_2$ sont des doublons si et seulement si : $rho(e_1) = rho(e_2)$, $lambda(e_1) = lambda(e_2)$ et $sigma(e_1, P) = sigma(e_2, P)$.

=== Doublons de noeuds
*Définition 2.5.2*\
#alinea $forall n_1, n_2 in N^2$, $n_1$ et $n_2$ sont des doublons si et seulement si : $lambda(n_1) = lambda(n_2)$ et $sigma(n_1, P) = sigma(n_2, P)$.\
Cette définition pourrait être assouplie en prenant aussi en compte les arcs des noeuds et ainsi stipuler qu'au dessus d'un certain seuil d'arcs en commun, ceux-ci sont considérés comme des doublons.

= Profilage d'un Graphe de Propriété

= Preuve de concept (Neo4j)

== Méthodes de test
== Exemples

= Questions ouvertes

= Conclusion

= Annexe ?

// References
#pagebreak()
#bibliography("../references.bib", title: "Bibliographie")
