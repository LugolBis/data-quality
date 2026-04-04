#import "@preview/algo:0.3.6": algo, code, comment, d, i
#import table: cell, header

#set page(
  flipped: true,
  numbering: "1",
  number-align: right + bottom,
)

#set align(left)
#set text(
  lang: "fr",
  size: 18pt,
)

#show raw.where(block: true): block.with(
  fill: luma(240),
  inset: 10pt,
  radius: 4pt,
)

#let slide_title = content => [#place(center + horizon)[#content]]
#let title = content => [#align(center)[#content #v(0.5em)]]

// Slide de présentation
#slide_title([
  = Étude de la Qualité de données d’une\ Base de données Graphe
])
#pagebreak()

// Notations et Concepts
#title([== Notations et Concepts])
#table(
  columns: (1fr, 1fr),
  align: (left, left),
  [*Node*], [*Relationship*],
  [Représente un noeud du graphe.],
  [Représente un arc du graphe, tel que cet arc a un nœud source et un nœud destination.],

  [
    - Possède 1 à plusieurs labels
    - Possède 0 à plusieurs *properties*
  ],
  [
    - Possède 1 seul label
    - Possède 0 à plusieurs *properties*
  ],
)

La base de données est désignée par le graphe : $G(V_N, E_R)$, avec $V_N$ un ensemble de *Node* et $E_R$ un ensemble de *Relationship*.

Tel que on note :
- $forall n in V_N$ (resp. $forall r in E_R$) :
  - $n [L]$, avec $L$ l'ensemble des *labels* classifiant $n$ (resp. $r [L]$).
  - $n {P}$ l'ensemble $P$ des *properties* de $n$ (resp. $r {P}$).
  - $n.p$ la *property* $p$ de $n$ (resp. $r.p$).
- $forall r in E_R$ :
  - On a $r."src"$ le nœud source et $r."dest"$ le nœud destination.
#pagebreak()

// Complétude
#title([== Complétude])
*Définition* : La Complétude mesure la quantité de données manquantes d’une base de données @cai2016challenges.

*Comment la mesurer dans une base de données Graphe* :
- *Existence de chemins élémentaires prédéfinis entre des _Nodes_ / _Relationships_*
  - Exemple : Vérifie que $forall n [A], exists r [B], n [C]$ tel que $r [B] ."src" = n [A]$ et $r [B] ."dest" = n [C]$
  - Paramètres modifiables : chemins/chaînes, longueur du chemin et label/type (des entités composantes).
- *Le degré des _Nodes_*
  - Définition : Soit $L_X$ un ensemble de labels et $D_s, D_e subset RR²$ représentant respectivement les degrés sortant et entrant, $forall n in V_N$ avec $n[L] subset.eq L_X$ on vérifie que $d^+(n) in D_s$ et $d^-(s) in D_e$.
- *Les propriétés de connexité*
  - Exemples :
    - Vérifie que $forall n [A]$, $exists$ une arborescence couvrante dont la racine est $n [A]$
    - Vérifie que $forall n [A], n [B]$ et $r$ tel que $r [B] ."src" = n [A] | n [B]$, $r [B] ."dest" = n [A] | n [B]$ constituent un DAG.
#pagebreak()

// Unicité
#title([== Unicité])
*Définition* : L’unicité mesure la redondance dans les données.

*Comment la mesurer dans une base de données Graphe* :
- *Les doublons de Relationships*
  - Définition : $forall r_1, r_2 in E_R^2$, $r_1, r_2$ sont des doublons SSI $r_1 [L_1] = r_2 [L_2]$, $r_1."src" = r_2."src"$, $r_1."dest" = r_2."dest"$, $r_1 {P_1} = r_2 {P_2}$ et $forall p in P_1$, $r_1.p = r_2.p$.
- *Les doublons de Node*
  - Définition : $forall n_1, n_2 in V_N^2$, $n_1, n_2$ sont des doublons SSI $n_1 [L_1] = n_2 [L_2]$, $n_1 {P_1} = n_2 {P_2}$, $forall p in P_1$, $n_1.p = n_2.p$ et $forall r$ tel que $r."src" = n_1 | n_2$ ou $r."dest" = n_1 | n_2$ sont des doublons si $n_1 = n_2$.
- *L’existence de Clés*
  - Définition : On note $K$ l’ensemble des *properties* formant une clé et $L_X$ les labels concernés, tel que $forall n in V_N$ tel que $n[L] subset.eq L_X$ on a $n.p | forall p in K$, $n_1.p = n_2.p$ qui est unique. @thang2026neo4j
#pagebreak()

// Cohérence
#title([== Cohérence])
*Définition* : La Cohérence mesure la validité des relations entre les données.

*Comment la mesurer dans une base de données Graphe* :
- *Dépendance Fonctionnelle (FD)*
  - Définition : $forall e in V_N union E_R$, avec $X, Y subset.eq e{P}$ et $L subset.eq e[L_e]$, on définit par $(L, X -> Y)$ une FD sur $e$.
- *Dépendance Fonctionnelle Conditionnelle (CFD)*
  - Définition : $forall e in V_N union E_R$, avec $X, Y subset.eq e{P}$, $L subset.eq e[L_e]$ et $C$ un ensemble de contraintes. Une contrainte est définie comme suit : $forall c in C$, on a $c.Z subset.eq e{P}$ l’ensemble des *properties* de $e$ devant vérifier la contrainte, $c."val" = "constant" | e.p$, $c.lambda$ la fonction permettant de vérifier la contrainte et $c."next" = emptyset | {("Condition", "boolean_operator")}$ l’ensemble des contraintes combinées avec $c$. Tel que on définit par $(L, C, X -> Y)$ une CFD sur $e$.
- *Dépendance d’un pattern de Graph (GFD)*
  - Définition : $forall e in V_N union E_R$, avec $X, Y subset.eq e{P}$, $L subset.eq e[L_e]$ et $G_p$ un pattern de graphe permettant d’appliquer la dépendance fonctionnelle au sous graphe $G' (V_N', E_R')$ induit de $G_p$ tel qu’on définit par $(L, G_p, X -> Y)$ une GFD sur $e$. Une autre approche (très différente) nommé _gFD_ @Manouvrier2024PGFD consiste a exclure tous les nodes qui n'ont pas toutes les properties définit par la _FD_.
- *Validation par Requête personnalisable*
  - Intuition : L’approche de *GFD* est intéressante mais peut rapidement devenir complexe à étendre. Une approche de validation par requête complètement écrite par l’utilisateur permettrait plus de flexibilité.
#pagebreak()

// Conformité
#title([== Conformité])
*Définition* : La Conformité mesure la conformité du format des données.

*Comment la mesurer dans une base de données Graphe* :
- *Format des chaînes de caractère*
  - Définition : $forall e in V_N union E_R$, avec $X subset.eq e{P}$ et *Regex* tel que on vérifie que $forall p in X$, $"match"(e.p, "Regex") = "true"$.
- *Format des dates*
  - Définition : $forall e in V_N union E_R$, avec $X subset.eq e{P}$ et *DateFmt* tel que on vérifie que $forall p in X$, $e,p$ est une date respectant le format *DateFmt*.
- *Labeling*
  - Méthode n°1 : Déterminer des clusters de nodes en fonction de leurs relationships entrant/sortant vers d’autres nodes (on s’intéresse ici à leur label et la mesure de distance choisie sur l’Edit distance) @Giot2015VisualGraph.
  - Méthode n°2 : Soit $L_X, L_Y$ deux ensembles de labels et $"OP"_"ENS"$ un opérateur entre deux ensembles, on vérifie que $forall n in V_N$ tel que $n[L] = L_Y$ on a $L_X$ $"OP"_"ENS"$ $n[L] = "true"$.
- *Intervalles de données*
  - Définition : $forall e in V_N union E_R$, avec $X subset.eq e{P}$, $I$ un ensemble de valeurs et $C$ une contrainte comme défini pour les CFD ; tel que on vérifie que $forall p in X$, $(e.p) in I$ AND $C = "true"$.
#pagebreak()

// Intégrité
#title([== Intégrité])
*Définition* : L’intégrité mesure la validité structurelle des données.

*Comment la mesurer dans une base de données Graphe* :
- *Validité du Property schema*
  - Exemple : Vérifie les propriétés d’intégrité _Uniqueness_, _Key_, _Existence_ et _property Type_.
  - Problème : Aucun standard DDL pour les bases de données graphe.
- *Validité des Index*
  - Définition : $forall e in V_N union E_R$, $forall p in e{P}$ si $e.p$ est indexée alors $e.p != "null"$.
  - Paramètres modifiables : Label / Type (des entités) et property.
- *Forme normale*\
  Algorithme :\
  Output : L'ensemble $D$ représentant le graphe normalisé.\

  #let PG_3FN = [#algo(
    main-text-styles: (size: 16pt),
    block-align: none,
    title: [#text(size: 20pt)[PG_3FN]],
    parameters: (
      [#text(size: 16pt)[PG. $G$, FD set $F$, Label set $L$]],
    ),
    indent-size: 10pt,
    indent-guides: 1pt + gray,
    row-gutter: 8pt,
    column-gutter: 5pt,
    inset: 10pt,
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
    main-text-styles: (size: 16pt),
    block-align: none,
    title: [#text(size: 20pt)[get_min_cover]],
    parameters: (
      [#text(size: 16pt)[FD set $F$]],
    ),
    indent-size: 10pt,
    indent-guides: 1pt + gray,
    row-gutter: 8pt,
    column-gutter: 5pt,
    inset: 10pt,
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
    columns: (1fr, 1fr),
    gutter: 1em,
    [
      #PG_3FN
    ],
    [
      #Min_cover_fn
    ],
  )

  L'algorithme est définit dans le cadre des *gFD* et *gUC* @Skavantzos2023Normalization que l'on peut facilement traduire par les *FD* mentionnées dans la section sur la *Cohérence*. Tandis que les *CFD* et les *GFD* (graph pattern FD), semblent avoir moins de sens dans un contexte de normalisation car l'algorithme normaliserai en 3NF seulement un fragment de la base de donnée.
#pagebreak()

// References
#bibliography("../references.bib")
