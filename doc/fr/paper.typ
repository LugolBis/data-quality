#import "@preview/algo:0.3.6": algo, code, comment, d, i
#import table: cell, header
#import "../assets/annexe.typ": *

#set page(
  numbering: "1",
  number-align: center + bottom,
)

#set align(left)
#set text(
  font: "New Computer Modern",
  lang: "fr",
)

#set heading(numbering: "1.1 -")

#set par(justify: true)
#show figure.where(kind: "custom-fig"): it => it.body

#let code = content => block(
  [#text(content, font: "JetBrains Mono", size: 10pt)],
  fill: luma(230),
  radius: 4pt,
  inset: 10pt,
  width: 100%,
)

#let alinea = [#h(1.5em)]

#let presentation = [


  #text("", size: 25pt)
]

#align(center)[
  #image("../assets/img/logoups.svg", height: 16%)
  #v(2cm)

  #text(size: 25pt, weight: "bold")[
    Étude de qualité de données d'une base de données graphe
  ]

  #v(0.5cm)

  #text(size: 16pt)[
    TER M1 Informatique\
  ]
  #text(size: 14pt)[
    Étude de qualité de données d'une base de données graphe
  ]

  #v(8cm)

  #text(size: 14pt)[
    Auteur : Loïc DESMARÈS et Tianyi YANG\
    Encadrantes : Béatrice FINANCE et Zoubida KEDAD
  ]

  #v(0.5cm)

  #text(size: 14pt)[
    Université Versailles Saint-Quentin-en-Yvelines\
    Année universitaire 2025–2026
  ]
]

#pagebreak()
#outline(
  title: "Table des matières",
  depth: 3,
)
#pagebreak()

*Abstract*: L'état de l'art des *Graphes de Propriété*...

= Introduction
#label("def1")

#alinea Cette étude a pour objectif de déterminer des critères de qualité de données pour les bases de données graphe. On considérera ici les *Graphes de Propriété* (_Property Graph_) disposant d'*étiquettes* (_labels_).

*Définition 1.*\
#alinea Un graphe de propriété est un tuple $G = (N, E, rho, lambda, sigma)$ tel que :
+ $N$ est un ensemble fini de noeuds (_nodes_), aussi appelé sommets (_vertices_).
+ $E$ est un ensemble fini d'arcs (on parlera d'arête lorsque la direction n'est pas prise en compte).
+ $rho: E -> (N times N)$ est une fonction totale qui associe pour chaque arc dans $E$ une paire $(n_"source", n_"destination")$. Cette paire de noeuds est donc non commutative car $(n_A, n_B) in rho(E)$ n'implique pas nécessairement $(n_B, n_A) in rho(E)$.
+ $lambda: (N union E) -> "SET"^+(L)$ est une fonction partielle qui associe à un noeud ou un arc un ensemble d'étiquettes incluses dans $L$ ($lambda$ est une fonction d'étiquetage des noeuds et des arcs).
+ $sigma: (N union E) times P -> "SET"^+(V)$ est une fonction partielle qui associe aux noeuds et arcs des valeurs $V$ aux propriétés $P$. On notera par la suite, $forall (o, p) in (N union E) times P$ et ses valeurs assignées $sigma(o, p) = {v_1, ..., v_n}$ par $(o, p) = arrow(v)$.

= Qualité de données d'un Graphe de Propriété
== Complétude
*Définition 2.1.0*\
#alinea La Complétude mesure la quantité de données manquantes d'une base de données graphe @cai2016challenges.

=== Existence de composantes
#label("def2.1.1")
#alinea L'existence de composantes connexes ou fortement connexes est une méthode pour vérifier la complétude des données. En effet, les arcs modélisent une grande partie des relations entre les objets et sont porteurs d'un sens sémantique important.\
#alinea Plus intuitivement vérifier l'existence de composantes entre des ensembles de noeuds et d'arcs permet par exemple d'exprimer des contraintes de chemins (resp. chaînes). Naturellement l'ajout de contraintes comme la longueur des chemins, l'appartenance d'un ensemble d'étiquettes à ceux-ci constituent de solides outils pour capturer un sens sémantique complexe.

*Définition 2.1.1*\
#alinea Soit $G_p$ un graph pattern (_patron de graphe_) modélisant une composante connexe (resp. fortement connexe), un ensemble $O$ tel que $O in {N, E, N union E}$ et $L_O subset.eq L$ est un ensemble d'étiquettes. Tel que $forall (G_p, O, L_O)$ on a $forall o in O$ tel que $lambda(o) = L_O$, $exists$ au moins une occurrence de $G_p$ pour $o$. Cf. *@fig1[Figure]* en annexe.

=== Le degré des noeuds
#label("def2.1.2")
#alinea La complétude des données peut aussi s'exprimer par le degré des noeuds et ainsi exprimer des contraintes de cardinalités.

*Définition 2.1.2*\
#alinea Soit $L_O subset.eq L$ est un ensemble d'étiquettes et les ensembles $D_s, D_e subset RR^2$, représentant respectivement l'ensemble des degrés sortant et entrant. Tel que $forall n in N$ tel que $lambda(n) = L_O$ vérifie $d^+(n) in D_s$ et $d^-(n) in D_e$. Cf. *@fig2[Figure]* en annexe.

== Conformité
#label("def2.2.0")
*Définition 2.2.0*\
#alinea La Conformité mesure la validité du format des données.

=== Format des chaînes de caractère
#label("def2.2.1")
*Définition 2.2.1*\
#alinea Soit $O in {N, E, N union E}$, $L_O subset.eq L$, $X subset.eq P$ et *Regex* codant le format attendu. Tel que $forall o in O$ on vérifie que $forall v in sigma(o, X)$, $"match"(v, "Regex") = "Vrai"$. Cf. *@fig3[Figure]* en annexe.

=== Format des dates
#label("def2.2.2")
*Définition 2.2.2*\
#alinea Soit $O in {N, E, N union E}$, $L_O subset.eq L$, $X subset.eq P$ et *$"Date"_"fmt"$* codant le format de date attendu. Tel que $forall o in O$ on vérifie que $forall v in sigma(o, X)$, $"match"(v, "Date"_"fmt") = "Vrai"$. Cf. *@fig4[Figure]* en annexe.

=== Ensemble fini de données
#label("def2.2.3")
*Définition 2.2.3*\
#alinea Soit $O in {N, E, N union E}$, $L_O subset.eq L$, $X subset.eq P$, $I$ un ensemble de données (non atomique comprises) et $C$ une contrainte optionnelle (cf. @def2.3.2[Définition]). Tel que $forall o in O$ on vérifie $"SET"(sigma(o, X)) subset.eq I and C(o) = "Vrai"$. Cf. *@fig5[Figure]* en annexe.

=== Étiquetage Ensembliste
#label("def2.2.4")
*Définition 2.2.4*\
#alinea Soit $O in {N, E, N union E}$, $L_X, L_Y subset.eq L$ et $"Op"_"ens" in { subset, subset.eq, \\ }$ un opérateur ensembliste. Tel que $forall o in O$ tel que $L_X subset.eq lambda(o)$ vérifie $lambda(o) "Op"_"ens" L_Y = "Vrai"$. Cf. *@fig6[Figure]* en annexe.

#alinea Notons que seule l'implémentation partielle de cette définition à du sens dans le cadre des bases de données graphe *Neo4j*, car les arcs (_Relationships_) ne peuvent avoir qu'une seule étiquette.

=== Étiquetage par Regroupement (clustering)
#label("def2.2.5")
#alinea L'intuition est la suivante : des noeuds similaires doivent avoir le même ensemble d'étiquettes. Pour mesurer la qualité de l'étiquetage on cherche donc à regrouper les noeuds similaires pour détecter les erreurs d'étiquetage. L'approche qui suit est inspirée d'un système d'embeddings motivé par l'article @Giot2015VisualGraph. L'approche proposée est la suivante :
+ #alinea Déterminer un critère de similarité entre deux noeuds : on s'intéresse ici aux étiquettes des noeuds donc au sens sémantique de celles-ci. Notre intérêt se porte donc sur les relations entre les différents ensembles d'étiquettes. Ces relations sont ici modélisées par un concept riche en sémantique : les arcs. En effet les arcs sont caractérisés par une paire de noeuds (disposant d'une direction) et un ensemble d'étiquettes. On propose donc de traduire ce sens sémantique par des chaînes de caractère. Ainsi l'arc suivant :\
  #code([($"Noeud"_1$: {Étudiant,Personne})-[$"Arc"$:{Inscrit}]->($"Noeud"_2$: {Université})])
  Serait traduit par "OU:Inscrit:Université" (que l'on nomme un _Token_) du point de vu de $"Noeud"_1$ et par "IN:Inscrit:ÉtudiantPersonne" de celui de $"Noeud"_2$.
+ #alinea Déterminer une méthode de calcul de similarité entre deux _Token_. Sachant qu'un _Token_ traduit des relations sémantiques complexes par une chaîne de caractère, l'utilisation de distance d'édition (_Edit distance_) semble le plus adapté. On utilise donc la similarité de *Levenshtein* pour calculer la similarité entre deux _Token_.
+ #alinea Déterminer une méthode de calcul de similarité entre deux noeuds. On s'intéresse à leurs relations et à leurs étiquettes on va donc combiner un score de similarité de ces deux dimensions. On utilise l'indice de *Jaccard* pour calculer la similarité entre deux noeuds sur le critère des ensembles d'étiquettes, tel qu'on a $forall n_1, n_2 in N^2$, $"Similarité"_"Étiquettes" = 1-(|lambda(n_1) inter lambda(n_2)|)/(|lambda(n_1) union lambda(n_2)|)$.\
  #alinea La similarité entre deux noeuds sur le critère des _Tokens_ est calculée avec la similarité *Monge-Elkan* (ME), tel qu'on a $forall n_1, n_2 in N^2$, $"ME"(n_1, n_2) = 1 / abs(sigma(n_1, {"Tokens"})) sum_(t_1 in sigma(n_1, {"Tokens"})) max_(t_2 in sigma(n_2, {"Tokens"})) ("simimarité_levenshtein"(t_1, t_2))$ (resp. $"ME"(n_2, n_1)$),
  tel que $"Similarité"_"Tokens" = ("ME"(n_1, n_2) + "ME"(n_2, n_1))/2$. La similarité des _Tokens_ pourrait aussi être calculée à l'aide de l'algorithme *Fuzzy Jaccard* (moins précis) ou encore de l'algorithme de *Kuhn-Munkres* (optimal mais en $O(|N|^3)$).

On définit donc les algorithmes suivants :\
#alinea L'algorithme _Tokenization_ permet de générer un ensemble de _Token_ (représentant les relations d'un noeud) pour tous les noeuds tel qu'il existe un arc entrant ou sortant de ceux-ci. Autrement formulé : tout noeud ayant un degré entrant ou sortant non nul dispose d'une propriété "Tokens" sauvegardant l'ensemble de des _Token_ générés le concernant.\
#alinea L'algorithme _CreateTokens_ quant à lui génère un ensemble de noeuds connexes représentant l'ensemble des _Token_ distincts générés par l'algorithme _Tokenization_. Une fois ces noeuds créés l'algorithme _CreateTokens_ calcule la similarité de *Levenshtein* entre chaque paire de _Token_ et la sauvegarde sous forme d'arc entre ceux-ci.

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
  $c_s <-$ 'OU:' $+ lambda(e) +$ ':' $+ lambda(n_d)$\
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
  for $"idx"$ in $[0;|"tokens"| -1]$ do#i\
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
  $"Similarité"_"Tokens" <- ("ME"(n_1, n_2), "ME"(n_2, n_1))/2$\
  if $"Similarité"_"Tokens" >= t_t$ do#i\
  $e <- "newEdge"()$\
  $E <- E union {e}$\
  $rho(e) <- (n_1, n_2)$\
  $lambda(e) <- {"MERGE"}$#d\
  end#d\
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
  if $"Similarité"_"Tokens" <= t_t$#i\
  #comment("[...]", inline: true)\
  #comment("Ligne 25 :", inline: true)\
  $lambda(e) <- {"SPLIT"}$#d\
]]

#grid(
  columns: (0.9fr, 1.1fr),
  gutter: 1em,
  [
    #Tokenization
    #alinea L'algorithme _Tokenization_ a une complexité temporelle linéaire en $O(n)$ (avec $n = |E|$) et une complexité spatiale dans le pire cas (très rare) en $O(n times m)$ (avec $n = |N|$ et $m = |L|$). L'algorithme _CreateTokens_ a une complexité temporelle polynomiale en $O(n^2)$ (avec $n = |N|$) et une complexité spatiale dans le pire cas (très rare) en $O(n^2)$ (avec $n = 2|E|$).
  ],
  [
    #CreateTokens
  ],
)

#alinea Une fois les algorithmes _Tokenization_ et _CreateTokens_ on peut analyser les regroupements de noeuds avec leur similarité entre ensemble de _Token_, et sur la similarité de *Jaccard* pour calculer la similarité entre leur étiquettes. Le regroupement s'effectue par paire de noeuds et on ne sauvegarde qu'un simple arc liant les noeuds qui devraient être "Merge" (ceux-ci devraient avoir un ensemble similaire d'étiquettes) ou "Split" (ceux-ci ne devraient pas avoir un ensemble similaire d'étiquettes). Cette sélection est déterminée avec deux seuils de similarité, le premier concerne la similarité entre les étiquettes (cela permet de filtrer les paires de noeuds qui pourraient présenter des erreurs d'étiquetage). Ainsi qu'un deuxième seuil concernant la similarité des _Tokens_, déterminant la création (ou non) d'un arc "Merge" / "Split".

#Merge

#alinea L'algorithme _Merge_ détaillé ci-dessus permet donc de détecter toutes les paires de noeuds dont la similarité des étiquettes est $<$ au seuil $t_e$; et pour lesquelles la similarité des _Token_ est $>=$ au seuil $t_t$. En d'autres termes l'algorithme détecte les noeuds qui de par leur similarité de relations (_Token_), devraient avoir un ensemble d'étiquettes plus similaire (donc ils devraient être rassemblés). Cf. *@fig7[Figure]* en annexe.\
\

#grid(
  columns: (1fr, 1fr),
  gutter: 1em,
  [
    #alinea Cet algorithme peut être aisément adapté pour détecter l'inverse : "Split" désignant les paires de noeuds qui ne devraient pas avoir des ensembles d'étiquettes similaires. Pour opérer les changements nécessaires il suffirait de modifier comme suit les lignes [8, 21, 25] de l'algorithme _Merge_.
  ],
  [
    #Split
  ],
)

#pagebreak()
== Cohérence
*Définition 2.3.0*\
#alinea La Cohérence mesure la validité des relations de la base de données graphe.

=== Dépendance Fonctionnelle (FD)
#label("def2.3.1")
*Définition 2.3.1*\
#alinea Soit $O in {N, E, N union E}$, $L_O subset.eq L$ et $X, Y subset.eq P$, on définit par $(O, L_O, X -> Y)$ une *FD*. Tel que $forall o_1, o_2 in O^2$ tel que $lambda(o_1) = L_O$ et $lambda(o_2) = L_O$ vérifie $sigma(o_1, X) = sigma(o_2, X) arrow.double sigma(o_1, Y) = sigma(o_2, Y)$. Cf. *@fig8[Figure]* en annexe.

=== Dépendance Fonctionnelle Conditionnelle (CFD)
#label("def2.3.2")
*Définition 2.3.2.a*\
#alinea Une *condition* est un tuple $C = (P_C, "VAL", f, "NEXT")$ tel que :
+ $P_C subset.eq P$ est l'ensemble des propriétés devant respecter la condition.
+ $"VAL" in {"constante", P}$ est la valeur de comparaison. La "constante" peut être tout type de données (non atomique comprises).
+ $f: (N union E, P_C, "VAL") -> "Booléen"$, est une fonction permettant de vérifier la condition sur un objet (ex. "$=$", "$<$", "$in$", etc.). On notera par la suite $C(o)$ le fait que l'objet $o$ vérifie $f(o, P_C, "VAL")$ sachant $P_C$ et $"VAL"$ définit dans $C$.
+ $"NEXT" in {emptyset, ("Condition", "Opérateur booléen")}$ est une deuxième condition (optionnelle) devant être vérifiée (permettant ainsi de la combiner avec la première avec l' "Opérateur booléen").
*Définition 2.3.2.b*\
#alinea Soit $O in {N, E, N union E}$, $L_O subset.eq L$, $C$ une condition (cf. @def2.3.2[Définition]) et $X, Y subset.eq P$, on définit par $(O, L_O, C, X -> Y)$ une *CFD*. Tel que $forall o_1, o_2 in O^2$ tel que $lambda(o_1) = L_O$ et $lambda(o_2) = L_O$ et $C(o_1) = "Vrai"$ et $C(o_2) = "Vrai"$ vérifie $sigma(o_1, X) = sigma(o_2, X) arrow.double sigma(o_1, Y) = sigma(o_2, Y)$. Cf. *@fig9[Figure]* en annexe.

=== Dépendance d’un Graph pattern (GFD)
#label("def2.3.3")
*Définition 2.3.3*\
#alinea Soit $G_p$ un graph pattern à partir duquel on déduit $G'(N', E')$, sous graphe de $G$ correspondant à $G_p$; $O in {N, E, N union E}$, $L_O subset.eq L$ et $X, Y subset.eq P$, on définit par $(O, L_O, G_p, X -> Y)$ une *GFD*. Tel que $forall o_1, o_2 in O^2$ tel que $o_1, o_2 in G'$ vérifie $sigma(o_1, X) = sigma(o_2, X) arrow.double sigma(o_1, Y) = sigma(o_2, Y)$. Cf. *@fig10[Figure]* en annexe.\
#alinea Une autre approche (très différente) nommée _gFD_ @Manouvrier2024PGFD consiste à exclure tous les noeuds qui n'ont pas toutes les propriétés ($X union Y$) définies par la _FD_.

=== Validation par requête
#label("def2.3.4")
#alinea Les dépendances fonctionnelles (_FD_, _CFD_ et _GFD_) sont des outils très puissants. Mais ils sont complexes à étendre pour parvenir à capturer l'ensemble du sens sémantique offert par les requêtes. C'est pourquoi une approche de validation supplémentaire consisterait --- sur le modèle de _dbt_ --- à valider ou invalider des requêtes écrites par l'utilisateur.\
*Définition 2.3.4*\
#alinea Ce système de validation par requête est défini par un tuple _dgt_ $= (R, B)$ tel que :
+ $R$ est une requête, aussi riche que le langage de requêtage le permet; qui renvoie (ou non) des objets.
+ $B$ est un booléen indiquant si $R$ doit renvoyer des objets pour valider la contrainte définie par celle-ci.\
Cf. *@fig11[Figure]* en annexe.

== Intégrité
*Définition 2.4.0*\
#alinea L’intégrité mesure la validité structurelle d'une base de données graphe.

=== Validité du schéma de propriété
#label("def2.4.1")
#alinea Dans l'état de l'art aucun standard _DDL_ n'a émergé pour les bases de données graphe. On va donc définir trois contraintes d'intégrité :
+ *Unicité de propriétés* :\
  Soit $O in {N, E, N union E}$, $L_O subset.eq L$ et $X subset.eq P$ tel que on vérifie que $forall o_1, o_2 in O^2$ vérifie $sigma(o_1, X) = sigma(o_2, X) arrow.double o_1 = o_2$. Cf. *@fig12[Figure]* en annexe.
+ *Existence de propriétés* :\
  Soit $O in {N, E, N union E}$, $L_O subset.eq L$ et $X subset.eq P$ tel que on vérifie que $forall o in O$ vérifie $"NULL" in.not sigma(o, X)$. Cf. *@fig13[Figure]* en annexe.
+ *Type des valeurs de propriétés*  :\
  Soit $t: (V) -> "SET"^+(T)$ une fonction totale qui attribut un ensemble de type $T$ à un ensemble de valeurs $V$, $O in {N, E, N union E}$, $L_O subset.eq L$, $X subset.eq P$ et $Y subset.eq T$ tel que on vérifie que $forall o in O$ vérifie $(t compose sigma)(o, X) subset.eq Y$. Cf. *@fig14[Figure]* en annexe.
Notons que ces contraintes peuvent être définies en *Cypher* (le langage de requếtes de *Neo4j*).

=== Validité des Index
#label("def2.4.2")
#alinea L'intuition est la suivante : des valeurs manquantes sur des propriétés indexées peuvent être un signal de dégradation de l'intégrité de la base de données graphe.\
*Définition 2.4.2*\
#alinea Soit $i: (N times E) -> "BITSET"$ des propriétés indexées, $forall o in (N union E)$ on vérifie $"NULL" in.not i(o) dot.o sigma(o, P)$. Cf. *@fig15[Figure]* en annexe.

=== Forme normale d'un Graphe de propriété
#label("def2.4.3")
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

#alinea L'algorithme est défini dans le cadre des *gFD* et *gUC* @Skavantzos2023Normalization que l'on peut facilement traduire par les *FD* (cf. @def2.3.1[Définition]). Tandis que les *CFD* et les *GFD* (graph pattern FD), n'ont pas de sens dans un contexte de normalisation car l'algorithme normaliserait en 3NF seulement un fragment de la base de donnée. Cf. *@fig16[Figure]* en annexe.

== Unicité
*Définition 2.5.0*\
#alinea L'unicité mesure la redondance d'une base de données graphe.

=== Doublons d'arcs
#label("def2.5.1")
*Définition 2.5.1*\
#alinea $forall e_1, e_2 in E^2$, $e_1$ et $e_2$ sont des doublons si et seulement si : $rho(e_1) = rho(e_2)$, $lambda(e_1) = lambda(e_2)$ et $sigma(e_1, P) = sigma(e_2, P)$. Cf. *@fig17[Figure]* en annexe.

=== Doublons de noeuds
#label("def2.5.2")
*Définition 2.5.2*\
#alinea $forall n_1, n_2 in N^2$, $n_1$ et $n_2$ sont des doublons si et seulement si : $lambda(n_1) = lambda(n_2)$ et $sigma(n_1, P) = sigma(n_2, P)$. Cf. *@fig18[Figure]* en annexe.\
Cette définition pourrait être assouplie en prenant aussi en compte les arcs des noeuds et ainsi stipuler qu'au-dessus d'un certain seuil d'arcs en commun, ceux-ci sont considérés comme des doublons.

#pagebreak()
= Profilage d'un Graphe de Propriété
#alinea L'objectif du profilage d'une base de données graphe est d'avoir un tableau de bord sur la distribution des données. Cette section regroupe donc des indicateurs intéressants pour caractériser les données d'un graphe de propriété. Ces indicateurs ne constituent pas des éléments de qualité de données car la nature généraliste de ceux-ci ne saurait capturer les usages métier intrinsèques à une base de données graphe.
== Complétude
=== Composants faiblement connectés
*Définition 3.1.1*\
#alinea Détection des composantes connexes du graphe avec l'algorithme *WCC*.
=== Composants fortement connectés
*Définition 3.1.2*\
#alinea Détection des composantes fortement connexes du graphe avec l'algorithme *SCC* (on ne considère ici que les chemins).
== Conformité
=== Détection de types distincts pour des propriétés
*Définition 3.2.1*\
#alinea $forall p in P$ on vérifie que $forall o in N$ (resp. $E$), tel que $sigma(o, {p}) eq.not "NULL"$, $exists$ un unique type $t_x$ tel que $(t compose sigma)(o, {p}) = t_x$ (cf. @def2.4.1[Définition]). Un tableau de bord concis listant les propriétés pour lesquelles le type n'est pas unique est construit à partir de cette détection.
== Intégrité
=== Distribution des propriétés des noeuds
*Définition 3.3.1*\
#alinea Analyse de la distribution des propriétés définies pour des noeuds, regroupés selon leur ensemble d'étiquettes.
=== Distribution des propriétés des noeuds par étiquette
*Définition 3.3.2*\
#alinea Analyse de la distribution des propriétés définies pour des noeuds, regroupés selon chaque étiquette attachée à ceux-ci.
=== Distribution des propriétés des arcs
*Définition 3.3.3*\
#alinea Analyse de la distribution des propriétés définies pour des noeuds, regroupés selon leur ensemble d'étiquettes.\
#alinea Notons que cette définition restreinte est équivalente à celle de l'analyse par étiquette sous *Neo4j* car les arcs (_Relationships_) ne disposent que d'une seule étiquette.
== Étiquetage
=== Détection d'anomalies par regroupement (clustering)
*Définition 3.4.1*\
#alinea On génère à l'aide l'algorithme *FastRP* un _embedding_ à partir des propriétés numériques (les _features_) et de la topologie du graphe pour chaque noeud. Ces _embeddings_ sont en suite utilisés pour déterminer des groupes (_clusters_) de noeuds avec l'algorithme *KNN*. Une fois ces groupes déterminé on filtre les résultats qui ont une similarité supérieure ou égale à un seuil donné. Enfin on compare les étiquettes (_labels_) des noeuds à ceux des autres noeuds pour détecter, le cas échéant, des erreurs d'étiquetage (_labeling_).\
#alinea Notons que cette méthode est assez fragile, notamment à cause des _embeddings_ qui peuvent être en grande partie constitué de valeurs par défaut (_padding_), entrainant un biais conséquent sur les calculs de similarité. D'autres approches comme la détection de communauté avec l'algorithme de *Louvain* seraient envisageable pour cet usage de profilage.
== Lisibilité
=== Distribution du degré des noeuds
*Définition 3.5.1*\
#alinea Analyse de la distribution des degrés (entrant et sortant), des noeuds regroupés selon leur ensemble d'étiquettes.
=== Détection des arcs formant un multi-graphe
*Définition 3.5.2*\
#alinea Détection d'arcs partageant le même noeud source et le même noeud destination, formant ainsi un multi-graphe. Un tableau de bord concis sur l'ensemble d'étiquettes du noeud source et celui du noeud destination, ainsi que l'ensemble des étiquettes des arcs est construit à partir de cette détection.
=== Analyse de l'excentricité du graphe
*Définition 3.5.3*\
#alinea Analyse de l'excentricité du graphe : calcul du rayon et du diamètre du graphe.\
On peut aisément imaginer utiliser ces informations pour analyser un graphe modélisant un réseau par exemple.
== Valeurs aberrantes (_Outlier_)
=== Détection des valeurs numériques aberrantes
*Définition 3.6.1*\
#alinea Détection de valeurs numériques aberrantes pour les propriétés des noeuds et des arcs.\
De nouveau cela permet de caractériser les données et de détecter, le cas échéant, des valeurs invalides.
=== Analyse de l'influence transitive des noeuds
*Définition 3.6.2*\
#alinea L'influence transitive d'un noeud est déterminée en calculant sa centralité de vecteur propre (_Eigenvector Centrality_); qui est une mesure utilisée en théorie des graphes pour évaluer l'influence d'un noeud. Celle-ci est calculée en tenant compte du nombre de connexions d'un noeud et de l'importance des noeuds auxquels il est connecté.\
#alinea Cette analyse permet ainsi de mesurer l’influence des nœuds et de détecter, le cas échéant, ceux dont l’influence ne correspond pas au domaine modélisé.
=== Analyse de l'influence transitive moyenne
*Définition 3.6.3*\
#alinea Analyse de l'influence transitive moyenne à travers les noeuds du graphe.
= Implémentation - Neo4j
#alinea *Neo4j* est une base de données graphe proposant une implémentation flexible des graphes de propriété. Les noeuds sont ainsi nommé des "Nodes" et les arcs sont nommés des "Relationships". L'ensemble des concepts de *Neo4j* est identique à la définition établie en introduction (cf. @def1[Définition]), à l'exception près que les "Relationships" ne peuvent avoir qu'une seule étiquette.
== Méthodes de test

= Questions ouvertes ?

= Conclusion
#alinea Au terme de cette études de nombreux indicateurs de qualité de données se sont révélés intéressants et adaptés a un graphe de propriété. De plus lorsque ceux-ci sont couplés avec un système de profilage cela offre une vision d'ensemble sur les données des bases de données graphe. La structure semi-structurée de celles-ci offre un outil puissant pour exprimer des concepts sémantique complexe. Parvenir à capturer l'ensemble du sens sémantique des bases de données graphe est un enjeu de taille du fait de la pluralité des usages de celles-ci.\
#alinea Néanmoins certains défis subsistent, que ce soit l'analyse de la qualité de l'étiquetage (_labeling_), la conformité des données (de nombreuses vérifications complexe pourraient être standardisées avec un _DDL_) ou encore les formes normales d'une base de données graphe.

= Annexe
#alinea Cette annexe rassemble des figures de graphes mettant en lumière les définitions précédemment établies.

#fig-wrap[
  #cmp(
    Graph-211-1,
    Graph-211-2,
  )
  #figh([Figure 1 : Exemple pour la _@def2.1.1[Définition]_], [#Example-211])
] <fig1>

#fig-wrap[
  #cmp(
    Graph-212-1,
    Graph-212-2,
  )
  #figh([Figure 2 : Exemple pour la _@def2.1.2[Définition]_], [#Example-212])
] <fig2>

#fig-wrap[
  #cmp(
    Graph-221-1,
    Graph-221-2,
  )
  #figh([Figure 3 : Exemple pour la _@def2.2.1[Définition]_], [#Example-221])
] <fig3>

#fig-wrap[
  #cmp(
    Graph-222-1,
    Graph-222-2,
  )
  #figh([Figure 4 : Exemple pour la _@def2.2.2[Définition]_], [#Example-222])
] <fig4>

#fig-wrap[
  #cmp(
    Graph-223-1,
    Graph-223-2,
  )
  #figh([Figure 5 : Exemple pour la _@def2.2.3[Définition]_], [#Example-223])
] <fig5>

#fig-wrap[
  #cmp(
    Graph-224-1,
    Graph-224-2,
  )
  #figh([Figure 6 : Exemple pour la _@def2.2.4[Définition]_], [#Example-224])
] <fig6>


#fig-wrap[
  #block(width: 100%, inset: 8pt, fill: white, stroke: (paint: mg-s, thickness: 0.5pt), radius: 3pt)[
    #text(fill: mg-s, weight: "bold")[⊕ Suggestion MERGE]\
    _Token_ similaires ("OU:STUDY_AT:University", "OU:COMES_FROM:City").\
    On observe deux ensembles d'étiquettes avec une faible similarité, paradoxalement à la forte similarité des _Token_ de ces noeuds.
    #v(5pt)
    #Graph-225-1
  ]

  #block(width: 100%, inset: 8pt, fill: white, stroke: (paint: sp-s, thickness: 0.5pt), radius: 3pt)[
    #text(fill: sp-s, weight: "bold")[⊖ Suggestion SPLIT]\
    Étiquettes identiques (:Person).\
    On observe des _Token_ différents pour des noeuds partageant le même ensemble d'étiquettes.
    #text(style: "italic")[\ ]
    #text(style: "italic")[\ ]
    #v(5pt)
    #Graph-225-2
  ]
  #figh([Figure 7 : Exemple pour la _@def2.2.5[Définition]_], [], display_desc: false)
] <fig7>

#fig-wrap[
  #cmp(
    Graph-231-1,
    Graph-231-2,
  )
  #figh([Figure 8 : Exemple pour la _@def2.3.1[Définition]_], [#Example-231])
] <fig8>

#fig-wrap[
  #cmp(
    Graph-232-1,
    Graph-232-2,
  )
  #figh([Figure 9 : Exemple pour la _@def2.3.2[Définition]_], [#Example-232])
] <fig9>

#fig-wrap[
  #cmp(
    Graph-233-1,
    Graph-233-2,
  )
  #figh([Figure 10 : Exemple pour la _@def2.3.3[Définition]_], [#Example-233])
] <fig10>


#fig-wrap[
  #cmp(
    Graph-234-1,
    Graph-234-2,
  )
  #figh([Figure 11 : Exemple pour la _@def2.3.4[Définition]_], [#Example-234])
] <fig11>

#fig-wrap[
  #cmp(
    Graph-241-1,
    Graph-241-2,
  )
  #figh([Figure 12 : Exemple pour la _@def2.4.1[Définition 1 de]_], [#Example-241a])
] <fig12>

#fig-wrap[
  #cmp(
    Graph-241-3,
    Graph-241-4,
  )
  #figh([Figure 13 : Exemple pour la _@def2.4.1[Définition 2 de]_], [#Example-241b])
] <fig13>

#fig-wrap[
  #cmp(
    Graph-241-5,
    Graph-241-6,
  )
  #figh([Figure 14 : Exemple pour la _@def2.4.1[Définition 3 de]_], [#Example-241c])
] <fig14>

#fig-wrap[
  #cmp(
    Graph-242-1,
    Graph-242-2,
  )
  #figh([Figure 15 : Exemple pour la _@def2.4.2[Définition]_], [#Example-242])
] <fig15>

#pagebreak()
#fig-wrap[
  #block(width: 100%, inset: 8pt, fill: white, stroke: (paint: err-s, thickness: 0.5pt), radius: 3pt)[
    #text(size: 7.5pt, fill: err-s, weight: "bold")[✗ Non normalisé]
    #v(5pt)
    #Graph-243-2
  ]
  #block(width: 100%, inset: 8pt, fill: white, stroke: (paint: ok-s, thickness: 0.5pt), radius: 3pt)[
    #text(size: 7.5pt, fill: ok-s, weight: "bold")[✓ Normalisé (3NF)]
    #v(5pt)
    #Graph-243-1
  ]
  #figh([Figure 16 : Exemple pour la _@def2.4.3[Définition]_], [], display_desc: false)
] <fig16>

#fig-wrap[
  #cmp(
    Graph-251-1,
    Graph-251-2,
  )
  #figh([Figure 17 : Exemple pour la _@def2.5.1[Définition]_], [], display_desc: false)
] <fig17>

#fig-wrap[
  #cmp(
    Graph-252-1,
    Graph-252-2,
  )
  #figh([Figure 18 : Exemple pour la _@def2.5.2[Définition]_], [], display_desc: false)
] <fig18>


// References
#pagebreak()
#bibliography("../references.bib", title: "Bibliographie")
