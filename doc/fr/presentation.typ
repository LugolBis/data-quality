#import "@preview/typslides:1.3.3": *
#import "@preview/algo:0.3.6": algo, comment, d, i
#import "../assets/annexe.typ": *
#import "paper.typ": *

#show: typslides.with(
  ratio:        "16-9",
  theme:        "purply",
  font:         "Fira Sans",
  font-size:    20pt,
  link-style:   "color",
)

#front-slide(
  title: "Étude de qualité de données d'une base de données graphe",
  subtitle: [TER M1 Informatique],
  authors: [
    #grid(
      columns: (1fr, 0.9fr),
      gutter: 1em,
      [
        Loïc Desmarès, Tianyi Yang\
        #link("https://github.com/LugolBis/data-quality")
      ],
      [
        #image("../assets/img/logoups.svg", height: 30%)
      ],
    )
  ],
  info: [
    
  ],
)

#table-of-contents(title: "Sommaire")

#slide(title: "Introduction", outlined: true)[
  #align(center)[
    Présentation des bases de données graphe\
    #image("/assets/img/paradigm_presentation.png", height: 80%)
  ]
]

#slide(title: "Introduction", outlined: true)[
  Nous nous intéressons ici aux enjeux suivant  des bases de données graphe :

  - Modèle de données -- Paradigme

  - Sémantique -- Qualité de données

  - Cadre de notre étude : les graphes de propriété
]

#slide(title: "Introduction", outlined: true)[
  Un graphe de propriété est un tuple $G = (N, E, rho, lambda, sigma)$ tel que :
+ $N$ est un ensemble fini de noeuds (_nodes_), aussi appelé sommets (_vertices_).
+ $E$ est un ensemble fini d'arcs (on parlera d'arête lorsque la direction n'est pas prise en compte).
+ $rho: E -> (N times N)$ est une fonction totale qui associe pour chaque arc dans $E$ une paire $(n_"source", n_"destination")$. Cette paire de noeuds est donc non commutative car $(n_A, n_B) in rho(E)$ n'implique pas nécessairement $(n_B, n_A) in rho(E)$.
+ $lambda: (N union E) -> "SET"^+(L)$ est une fonction partielle qui associe à un noeud ou un arc un ensemble d'étiquettes incluses dans $L$ ($lambda$ est une fonction d'étiquetage des noeuds et des arcs).
+ $sigma: (N union E) times P -> "SET"^+(V)$ est une fonction partielle qui associe aux noeuds et arcs des valeurs $V$ aux propriétés $P$.
]

#slide(title: "Qualité de données", outlined: true)[
  #text(size: 25pt)[*Complétude*]\
  \
  La Complétude mesure la quantité de données manquantes d'une base de données graphe @cai2016challenges.\
  \
  \
]

#slide(title: "Complétude : Existence de composantes")[
  L'existence de composantes connexe permet de mesurer la complétude selon :

  - Des composantes connexe (ou fortement connexe) requises

  - Des chemins (ou chaînes) de longueur fixée

  - Des ensembles d'étiquettes
]

#slide(title: "Complétude : Existence de composantes")[
  Exemple :

  #fig-wrap[
    #cmp(
      Graph-211-1,
      Graph-211-2,
    )
    #figh([], [#Example-211])
  ] <fig1>
]

#slide(title: "Complétude : Le degré des noeuds")[
  L'étude du degré des noeuds permet aussi de mesurer la complétude des données.

  #fig-wrap[
    #cmp(
      Graph-212-1,
      Graph-212-2,
    )
    #figh([], [#Example-212])
  ] <fig2>
]

#slide(title: "Conformité")[
  #text(size: 25pt)[*Conformité*]\
  \
  La Conformité mesure la validité du format des données.\
  \
  \
]

#slide(title: "Conformité : Format des chaînes de caractères")[
  Conformité du format des chaînes de caractères :
  #fig-wrap[
    #cmp(
      Graph-221-1,
      Graph-221-2,
    )
    #figh([], [#Example-221])
  ] <fig3>
]

#slide(title: "Conformité : Format de dates")[
  Conformité du format des dates :
  #fig-wrap[
    #cmp(
      Graph-222-1,
      Graph-222-2,
    )
    #figh([], [#Example-222])
  ] <fig4>
]

#slide(title: "Conformité : Ensemble fini de valeurs")[
  On définit un ensembles d'objets (noeuds, arcs) ayant un ensemble fixé d'étiquettes $L_O$, pour lesquels un ensemble de propriétés doivent être comprises dans un ensemble fini de valeurs $I$.\
  On ajoute la possibilité de filtrer ces objets selon une à plusieurs *Condition* (decrites ci-après).
]

#slide(title: "Conformité : Ensemble fini de valeurs")[
  Exemple :
  #fig-wrap[
  #cmp(
    Graph-223-1,
    Graph-223-2,
  )
  #figh([], [#Example-223])
] <fig5>
]

#slide(title: "Conformité : Étiquetage ensembliste")[
  On définit des contraintes d'inclusion stricte, d'inclusion ou d'exclusion entre des ensembles d'étiquettes, qui doivent être vérifiées par tous les objets.\
  \
  Exemple :
  #fig-wrap[
  #cmp(
    Graph-224-1,
    Graph-224-2,
  )
  #figh([], [#Example-224])
] <fig6>
]

#slide(title: "Conformité : Étiquetage par regroupement (clustering)")[
  L'intuition est la suivante : des noeuds similaires doivent avoir le même ensemble d'étiquettes. Pour mesurer la qualité de l'étiquetage, on cherche donc à regrouper les noeuds similaires pour détecter les erreurs d'étiquetage. L'approche qui suit est inspirée d'un système d'embeddings motivé par l'article @Giot2015VisualGraph.\

  + On définit la similarité entre deux noeuds selon le sens sémantique des relations de ceux-ci. On tokenize tous les arcs entrant ou sortant de ces noeuds. Ainsi l'arc suivant :\
    #code([($"Noeud"_1$: {Étudiant,Personne})-[$"Arc"$:{Inscrit}]->($"Noeud"_2$: {Université})], font-size: 17pt)
    Serait traduit par "OU:Inscrit:Université" (que l'on nomme un _Token_) du point de vue de $"Noeud"_1$ et par "IN:Inscrit:ÉtudiantPersonne" de celui de $"Noeud"_2$.
  
  + On utilise une distance d'édition (Levenshtein) pour déterminer la similarité entre deux _Token_.

  + On calcule la similarité entre deux noeuds selon deux dimensions :
    - Leur ensemble d'étiquettes avec l'indice de *Jaccard*
    - Leur ensemble de _Token_ avec la similarité de *Monge-Elkan*

  On aplique donc la procédure suivante :
  + Tokenization et stockage de tous les arcs de tous les noeuds dans une propriété de ceux-ci.
  + Isolation de l'ensemble des _Token_ générés et calcul de la similarité de *Levenshtein* entre chaque pair de _Token_.
  + Exécution des algorithmes _Split_ et _Merge_ pour détecter les erreurs d'étiquetage.
]

#slide(title: "Conformité : Étiquetage par regroupement (clustering)")[
  On effectue donc un regroupement des noeuds selon leur similarité d'étiquettes et leur similarité de _Token_ pour détecter les deux cas possible d'erreurs d'étiquetage :

  - *Merge* : des noeuds avec des _Token_ similaire ont des ensemble trop différent d'étiquettes.

  - *Split* : des noeuds avec des _Token_ peu similaire ont des ensemble d'étiquettes très similaire.

  Le filtrage des paires de noeuds concernés par ces deux métriques peut être adapté avec deux seuils de similarité (un par dimension).
]

#slide(title: "Conformité : Étiquetage par regroupement (clustering)")[
  #block(width: 100%, inset: 8pt, fill: white, stroke: (paint: mg-s, thickness: 0.5pt), radius: 3pt)[
    #text(fill: mg-s, weight: "bold")[⊕ Suggestion MERGE]\
    _Token_ similaires ("OU:STUDY_AT:University", "OU:COMES_FROM:City").\
    On observe deux ensembles d'étiquettes avec une faible similarité, paradoxalement à la forte similarité des _Token_ de ces noeuds.
    #v(5pt)
    #Graph-225-1
  ]
]

#slide(title: "Conformité : Étiquetage par regroupement (clustering)")[
  #block(width: 100%, inset: 8pt, fill: white, stroke: (paint: sp-s, thickness: 0.5pt), radius: 3pt)[
    #text(fill: sp-s, weight: "bold")[⊖ Suggestion SPLIT]\
    Étiquettes identiques (:Person).\
    On observe des _Token_ différents pour des noeuds partageant le même ensemble d'étiquettes.
    #text(style: "italic")[\ ]
    #text(style: "italic")[\ ]
    #v(5pt)
    #Graph-225-2
  ]
]

#slide(title: "Cohérence")[
  #text(size: 25pt)[*Cohérence*]\
  \
  La Cohérence mesure la validité des relations de la base de données graphe.\
  \
  \
]

#slide(title: "Cohérence : FD")[
  On définit les *FD* comme suit : 
  #fig-wrap[
    #cmp(
      Graph-231-1,
      Graph-231-2,
    )
    #figh([], [#Example-231])
  ] <fig8>
]

#slide(title: "Cohérence : CFD")[
  Une *condition* est un tuple $C = (P_C, "VAL", f, "NEXT")$ tel que :
  + $P_C subset.eq P$ est l'ensemble des propriétés devant respecter la condition.
  + $"VAL" in {"constante", P}$ est la valeur de comparaison. La "constante" peut être tout type de données (non atomique comprises).
  + $f: (N union E, P_C, "VAL") -> "Booléen"$, est une fonction permettant de vérifier la condition sur un objet (ex. "$=$", "$<$", "$in$", etc.). On notera par la suite $C(o)$ le fait que l'objet $o$ vérifie $f(o, P_C, "VAL")$ sachant $P_C$ et $"VAL"$ définit dans $C$.
  + $"NEXT" in {emptyset, ("Condition", "Opérateur booléen")}$ est une deuxième condition (optionnelle) devant être vérifiée (permettant ainsi de la combiner avec la première avec l' "Opérateur booléen").
]

#slide(title: "Cohérence : CFD")[
  Exemple :
  #fig-wrap[
    #cmp(
      Graph-232-1,
      Graph-232-2,
    )
    #figh([], [#Example-232])
  ] <fig9>
]

#slide(title: "Cohérence : GFD")[
  Soit $G_p$ un graph pattern à partir duquel on déduit $G'(N', E')$, sous graphe de $G$ correspondant à $G_p$, $O in {N, E, N union E}$, $L_O subset.eq L$ et $X, Y subset.eq P$, on définit par $(O, L_O, G_p, X -> Y)$ une *GFD*.\
  Tel que $forall o_1, o_2 in O^2$ tel que $o_1, o_2 in G'$ vérifie $sigma(o_1, X) = sigma(o_2, X) arrow.double sigma(o_1, Y) = sigma(o_2, Y)$.
]

#slide(title: "Cohérence : GFD")[
  #fig-wrap[
    #cmp(
      Graph-233-1,
      Graph-233-2,
    )
    #figh([], [#Example-233])
  ] <fig10>
]

#slide(title: "Cohérence : Validation par requête")[
  Afin d'étendre les *FD*, *CFD* et *GFD* pour capturer l'ensemble du sens sémantique exprimé par le lanquage de requêtage, une approche par validation de requêtes -- sur le modèle de _*dbt*_ -- est envisageable.
  #fig-wrap[
    #cmp(
      Graph-234-1,
      Graph-234-2,
    )
    #figh([], [#Example-234])
  ] <fig11>
]

#slide(title: "Intégrité")[
  #text(size: 25pt)[*Intégrité*]\
  \
  L'intégrité mesure la validité structurelle d'une base de données graphe.\
  \
  \
]

#slide(title: "Intégrité : Validité du schéma de propriété")[
  Dans l'état de l'art aucun standard _DDL_ n'a émergé pour les bases de données graphe. On s'intéresse donc à trois contraintes d'intégrité :
  
  + L'unicité des propriétés des objets

  + L'existence des propriétés des objets
  
  + Le type de données des propriétés des objets


  Notons que ces contraintes peuvent être définies en *Cypher* (le langage de requêtes de *Neo4j*).
]

#slide(title: "Intégrité : Validité des Index")[
  L'intuition est la suivante : des valeurs manquantes sur des propriétés indexées peuvent être un signal de dégradation de l'intégrité de la base de données graphe.\
  \
  Exemple : 
  #fig-wrap[
    #cmp(
      Graph-242-1,
      Graph-242-2,
    )
    #figh([], [#Example-242])
  ] <fig15>
]

#slide(title: "Intégrité : Forme normale d'un Graphe de propriété")[
  On s'intéresse maintenant à la forme normale du graphe. Et plus précisément à la 3ème forme normale (3NF).\
  \
  L'algorithme est défini dans le cadre des *gFD* et *gUC* @Skavantzos2023Normalization que l'on peut facilement traduire par les *FD* (ci-avant). Tandis que les *CFD* et les *GFD* (graph pattern FD), n'ont pas de sens dans un contexte de normalisation car l'algorithme normaliserait en 3NF seulement un fragment de la base de données.
]

#slide(title: "Intégrité : Forme normale d'un Graphe de propriété")[
  #grid(
    columns: (0.7fr, 1.3fr),
    gutter: 1em,
    [#text(size: 20pt, fill: err-s, weight: "bold")[✗ Non normalisé :]],
    [#Graph-243-2]
  )
]

#slide(title: "Intégrité : Forme normale d'un Graphe de propriété")[
  #grid(
    columns: (0.7fr, 1.3fr),
    gutter: 1em,
    [#text(size: 20pt, fill: ok-s, weight: "bold")[✓ Normalisé (3NF) :]],
    [#Graph-243-1]
  )
]

#slide(title: "Unicité")[
  #text(size: 25pt)[*Unicité*]\
  \
  L'unicité mesure la redondance d'une base de données graphe.\
  \
  \
]

#slide(title: "Unicité : Doublons d'arcs")[
  $forall e_1, e_2 in E^2$, $e_1$ et $e_2$ sont des doublons si et seulement si : $rho(e_1) = rho(e_2)$, $lambda(e_1) = lambda(e_2)$ et $sigma(e_1, P) = sigma(e_2, P)$.\
  \
  Exemple :
  #fig-wrap[
    #cmp(
      Graph-251-1,
      Graph-251-2,
    )
    #figh([], [], display_desc: false)
  ] <fig17>
]

#slide(title: "Unicité : Doublons de noeuds")[
  Deux noeuds $n_1, n_2$ sont des doublons si ils partagent le même ensemble d'étiquettes et les même valeurs de propriétés.\
  \
  Exemple :
  #fig-wrap[
    #cmp(
      Graph-252-1,
      Graph-252-2,
    )
    #figh([], [], display_desc: false)
  ] <fig18>
]

#slide(title: "Profilage de données", outlined: true)[
  L'objectif du profilage d'une base de données graphe est d'avoir un tableau de bord, une vision d'ensemble sur la distribution des données. Cette section regroupe donc des indicateurs intéressants pour caractériser les données d'un graphe de propriété.
]

#import "@preview/diagraph:0.3.0": raw-render

#slide(title: "Complétude")[
  #grid(
    columns: (1.2fr, 1fr),
    row-gutter: 3em,
    column-gutter: 2em,
    
    [
      == Composants faiblement connectés
      Détection des composantes connexes du graphe avec l'algorithme *WCC*.
    ],
    align(center + horizon)[
      #raw-render(
      ```dot
      digraph WCC {
        rankdir=TB;
        nodesep=0.3;
        ranksep=0.4;
        
        node [shape=circle, style=filled, fillcolor="#D9EAD3", fontname="Fira Sans", margin=0.05, fontsize=14];
        edge [dir=none, color="#666666", penwidth=1.5];

        Paris -> Normandie;
        Paris -> Lyon;
        Paris -> Strasbourg;

        Marseille [fillcolor="#F4CCCC"];

        Lyon -> Marseille [style=invis];
      }
      ```
      )
    ],

    [
      == Composants fortement connectés
      Détection des composantes fortement connexes du graphe avec l'algorithme *SCC* (on ne considère ici que les chemins).
    ],
    align(center + horizon)[
      #raw-render(
      ```dot
      digraph SCC {
        rankdir=LR;
        nodesep=0.5;
        ranksep=0.6;
        
        node [shape=circle, style=filled, fillcolor="#CFE2F3", fontname="Fira Sans", margin=0.05, fontsize=14];
        edge [color="#333333", penwidth=1.5, fontsize=10, fontname="Fira Sans"];

        Client [label="Client"];
        Marchand [label="Marchand"];
        Livreur [label="Livreur"];

        Client -> Marchand [label=" Paiement "];
        Marchand -> Livreur [label=" Expédition "];
        Livreur -> Client [label=" Livraison "];
      }
      ```
      )
    ]
  )
]

#import "@preview/diagraph:0.3.0": raw-render

#slide(title: "Conformité")[
  == Détection de types distincts pour des propriétés
  Cet indicateur détecte les propriétés dont le type de donnée stocké pour celles-ci n'est pas homogène.\
  Un tableau de bord concis listant les propriétés pour lesquelles le type n'est pas unique est construit à partir de cette détection.

  #v(2em)

  #align(center)[
    #raw-render(
    ```dot
    digraph ConformiteType {
      rankdir=LR;
      nodesep=0.8;
      
      node [shape=circle, fontname="Fira Sans", fontsize=14, style=filled, margin=0.05];
      
      P1 [label=":Product\nprice: 29.99\n(Float)", fillcolor="#D9EAD3"];
      P2 [label=":Product\nprice: \"15.50\"\n(String)", fillcolor="#F4CCCC"];
      P3 [label=":Product\nprice: \"Gratuit\"\n(String)", fillcolor="#F4CCCC"];
      
      P1 -> P2 -> P3 [style=invis];
    }
    ```
    )
  ]
]


#slide(title: "Intégrité")[
  #grid(
    columns: (1fr, 1.4fr),
    gutter: 2em,
    [
      === Distribution des propriétés des noeuds
      Analyse de la distribution des propriétés définies pour des noeuds, regroupés selon leur ensemble d'étiquettes.
    ],
    align(center + horizon)[
      #raw-render(
      ```dot
      digraph Dim1 {
        rankdir=TB;
        nodesep=0.4;
        ranksep=0.3;
        node [shape=circle, fontname="Fira Sans", fontsize=10, style=filled, margin=0.02];
        
        subgraph cluster_ok {
          label="✓ Homogène\n(Même ensemble d'étiquettes)"; fontname="Fira Sans"; fontsize=12; fontcolor="#2E7D32"; color="#2E7D32"; penwidth=2;
          ok1 [label="[:Student, :Intern]\nname\nage\nsalary", fillcolor="#D9EAD3"];
          ok2 [label="[:Student, :Intern]\nname\nage\nsalary", fillcolor="#D9EAD3"];
          ok1 -> ok2 [style=invis];
        }
        
        subgraph cluster_ko {
          label="✗ Hétérogène\n(Propriétés manquantes)"; fontname="Fira Sans"; fontsize=12; fontcolor="#C62828"; color="#C62828"; penwidth=2;
          ko1 [label="[:Student, :Intern]\nname\nage\nsalary", fillcolor="#D9EAD3"];
          ko2 [label="[:Student, :Intern]\nname\n(age manquant)\n(salaire manquant)", fillcolor="#F4CCCC"];
          ko1 -> ko2 [style=invis];
        }
      }
      ```
      )
    ]
  )
]

#slide(title: "Intégrité")[
  #grid(
    columns: (1fr, 1.4fr),
    gutter: 2em,
    [
      === Distribution des propriétés des noeuds par étiquette
      Analyse de la distribution des propriétés définies pour des noeuds, regroupés selon chaque étiquette attachée à ceux-ci.
    ],
    align(center + horizon)[
      #raw-render(
      ```dot
      digraph Dim2 {
        rankdir=TB;
        nodesep=0.4;
        ranksep=0.3;
        node [shape=circle, fontname="Fira Sans", fontsize=10, style=filled, margin=0.02];
        
        subgraph cluster_ok {
          label="✓ Homogène\n(Socle commun pour :Student)"; fontname="Fira Sans"; fontsize=12; fontcolor="#2E7D32"; color="#2E7D32"; penwidth=2;
          ok3 [label="[:Student, :Intern]\nname\nage\nsalary", fillcolor="#D9EAD3"];
          ok4 [label="[:Student]\nname\nage", fillcolor="#D9EAD3"];
          ok3 -> ok4 [style=invis];
        }
        
        subgraph cluster_ko {
          label="✗ Hétérogène\n(Pas de socle commun)"; fontname="Fira Sans"; fontsize=12; fontcolor="#C62828"; color="#C62828"; penwidth=2;
          ko3 [label="[:Student, :Intern]\nname\n(age manquant)\nsalary", fillcolor="#F4CCCC"];
          ko4 [label="[:Student]\nname\nage", fillcolor="#D9EAD3"];
          ko3 -> ko4 [style=invis];
        }
      }
      ```
      )
    ]
  )

  === Distribution des propriétés des arcs
    Analyse de la distribution des propriétés définies pour des noeuds, regroupés selon leur ensemble d'étiquettes.\
    Notons que cette définition restreinte est équivalente à celle de l'analyse par étiquette sous *Neo4j* car les arcs (_Relationships_) ne disposent que d'une seule étiquette.
    #align(center)[
      #raw-render(
      ```dot
      digraph Dim3 {
        rankdir=LR;
        ranksep=1.0;
        node [shape=circle, label="", width=0.15, style=filled, fillcolor="#CCCCCC"];
        edge [fontname="Fira Sans", fontsize=11, color="#333333", arrowsize=0.8];
        
        u1 -> v1 [label=" :PURCHASES \n {date, amount} "];
        u2 -> v2 [label=" :PURCHASES \n {date} "];
      }
      ```
      )
  ]
]

#import "@preview/diagraph:0.3.0": raw-render

#slide(title: "Étiquetage")[
  === Détection d'anomalies par regroupement (clustering)
  
  #grid(
    columns: (1.4fr, 1fr),
    gutter: 2em,
    [
      On génère à l'aide l'algorithme *FastRP* un _embedding_ à partir des propriétés numériques (les _features_) et de la topologie du graphe pour chaque noeud. Ces _embeddings_ sont ensuite utilisés pour déterminer des groupes (_clusters_) de noeuds avec l'algorithme *KNN*. Une fois ces groupes déterminés on filtre les résultats qui ont une similarité supérieure ou égale à un seuil donné. Enfin on compare les étiquettes (_labels_) des noeuds à celles des autres noeuds pour détecter, le cas échéant, des erreurs d'étiquetage (_labeling_).
    ],
    
    align(center + horizon)[
      #raw-render(
      ```dot
      digraph Anomaly {
        rankdir=TB;
        nodesep=0.3; 
        node [shape=circle, fontname="Fira Sans", fontsize=11, style=filled, margin=0.05];
        
        subgraph cluster_duck {
          label="Succès : Détection d'anomalie"; fontname="Fira Sans"; fontcolor="#2E7D32"; color="#2E7D32"; penwidth=2;
          n1 [label=":Company", fillcolor="#D9EAD3"];
          n2 [label=":Company", fillcolor="#D9EAD3"];
          n3 [label=":Person\n(Étiquette erronée)", fillcolor="#F4CCCC", fontcolor="#C62828"];
          n4 [label=":Company", fillcolor="#D9EAD3"];
          
          {rank=same; n1; n2;}
          {rank=same; n3; n4;}
          n1 -> n3 [style=invis];
        }
      }
      ```
      )
    ]
  )
]

#slide(title: "Étiquetage")[
  === Limites du clustering et alternatives
  Notons que cette méthode est assez fragile, notamment à cause des _embeddings_ qui peuvent être en grande partie constitués de valeurs par défaut (_padding_), entrainant un biais conséquent sur les calculs de similarité. D'autres approches comme la détection de communauté avec l'algorithme de *Louvain* seraient envisageables pour cet usage de profilage.

  #v(2em)

  #align(center)[
    #raw-render(
    ```dot
    digraph PaddingBias {
      rankdir=LR;
      nodesep=0.8;
      node [shape=circle, fontname="Fira Sans", fontsize=12, style=filled, margin=0.0];
      
      subgraph cluster_bias {
        label="Limite : Biais dû au Padding"; fontname="Fira Sans"; fontcolor="#C62828"; color="#C62828"; penwidth=2;
        n5 [label=":Product\nValeurs vides\n[0, 0, 0]", fillcolor="#EEEEEE"];
        n6 [label=":User\nValeurs vides\n[0, 0, 0]", fillcolor="#EEEEEE"];
        
        n5 -> n6 [label="  Fausse  \nsimilarité", style=dashed, color="#C62828", fontcolor="#C62828", fontsize=12, penwidth=1.5];
      }
    }
    ```
    )
  ]
]

#slide(title: "Lisibilité")[
  === Distribution du degré des noeuds
  Analyse de la distribution des degrés (entrant et sortant), des noeuds regroupés selon leur ensemble d'étiquettes.
  === Détection des arcs formant un multigraphe
  Détection d'arcs partageant le même noeud source et le même noeud destination, formant ainsi un multigraphe. Un tableau de bord concis sur l'ensemble d'étiquettes du noeud source et celui du noeud destination, ainsi que l'ensemble des étiquettes des arcs est construit à partir de cette détection.
  === Analyse de l'excentricité du graphe
  Analyse de l'excentricité du graphe : calcul du rayon et du diamètre du graphe.\
  On peut aisément imaginer utiliser ces informations pour analyser un graphe modélisant un réseau par exemple.
]

#import "@preview/diagraph:0.3.0": raw-render

#slide(title: "Valeurs aberrantes (outliers)")[
  === Détection des valeurs numériques aberrantes
  Détection de valeurs numériques aberrantes pour les propriétés des noeuds et des arcs.\
  De nouveau cela permet de caractériser les données et de détecter, le cas échéant, des valeurs invalides.

  #v(3em) 

  #align(center)[
    #raw-render(
    ```dot
    digraph NumOutlier {
      rankdir=LR; 
      nodesep=0.6;
      node [shape=circle, fontname="Fira Sans", fontsize=14, style=filled];
      
      n1 [label=":User\nage: 25", fillcolor="#D9EAD3"];
      n2 [label=":User\nage: 32", fillcolor="#D9EAD3"];
      n3 [label=":User\nage: 999", fillcolor="#F4CCCC", fontcolor="#C62828", color="#C62828", penwidth=2];
      
      n1 -> n2 -> n3 [style=invis];
    }
    ```
    )
  ]
]

#slide(title: "Valeurs aberrantes (outliers)")[
  #grid(
    columns: (1.2fr, 1fr),
    gutter: 2em,
    [
      === Analyse de l'influence transitive des noeuds
      L'influence transitive d'un noeud est déterminée en calculant sa centralité de vecteur propre (_Eigenvector Centrality_); qui est une mesure utilisée en théorie des graphes pour évaluer l'influence d'un noeud. Celle-ci est calculée en tenant compte du nombre de connexions d'un noeud et de l'importance des noeuds auxquels il est connecté.\
      Cette analyse permet ainsi de mesurer l’influence des nœuds et de détecter, le cas échéant, ceux dont l’influence ne correspond pas au domaine modélisé.
    ],
    align(center + horizon)[
      #raw-render(
      ```dot
      digraph Eigen {
        rankdir=BT; 
        nodesep=0.6; 
        ranksep=0.5;
        node [shape=circle, fontname="Fira Sans", style=filled, margin=0.05];
        
        CEO [label="CEO\nScore: 0.9", fillcolor="#D9EAD3", width=0.9, fontsize=13];
        CTO [label="CTO\nScore: 0.8", fillcolor="#D9EAD3", width=0.7, fontsize=11];
        
        Stag [label="Stagiaire\nScore: 0.85\n(Anomalie)", fillcolor="#F4CCCC", fontcolor="#C62828", width=0.9, fontsize=11, color="#C62828", penwidth=2];
        Dev [label="Dev\nScore: 0.2", fillcolor="#D9EAD3", width=0.5, fontsize=10];

        Stag -> CEO [color="#666666", penwidth=1.5];
        Stag -> CTO [color="#666666", penwidth=1.5];
        Dev -> CTO [color="#666666", penwidth=1.5];
      }
      ```
      )
    ]
  )
]

#slide(title: "Valeurs aberrantes (outliers)")[
  === Analyse de l'influence transitive moyenne
  Analyse de l'influence transitive moyenne à travers les noeuds du graphe.

  #v(4em)

  #align(center)[
    #raw-render(
    ```dot
    digraph AvgEigen {
      rankdir=TB; 
      nodesep=0.5;
      node [shape=Mrecord, fontname="Fira Sans", fontsize=15, style=filled, fillcolor="#CFE2F3", color="#4A86E8", penwidth=2];
      edge [style=invis];
      
      L1 [label="{ Ligne de base (Baseline) | Étiquette :Company | Score moyen : 0.88 }"];
      L2 [label="{ Ligne de base (Baseline) | Étiquette :Person | Score moyen : 0.42 }"];
      
      L1 -> L2;
    }
    ```
    )
  ]
]

#slide(title: "Implémentation avec Neo4j", outlined: true)[
  *Neo4j* est une base de données graphe proposant une implémentation flexible des graphes de propriété. Les noeuds sont ainsi nommés des "Nodes" et les arcs sont nommés des "Relationships".
  
  L'ensemble des concepts de *Neo4j* est identique à la définition établie en introduction, à l'exception près que les "Relationships" ne peuvent avoir qu'une seule étiquette. Notons que l'implémentation du _framework_ de qualité de données établi dans la présente étude a été implémentée cf. @lugolbis2026github.
]

#slide(title: "Résultats", outlined: true)[
  == Northwind
  Les expérimentations sur la base de donnée graphe *Northwind* avec une partie des données dégradées (avec la _seed_ 42) se sont révélées particulièrement concluante concernant la pertinance des critères de qualité de données établis précédemment.

  L'Étiquetage par regroupement c'est révélé être un outil puissant pour détecter les erreurs le cas échéant. Bien que cette approche présente une faiblesse : la forte polarisation des ensembles de noeuds dont les ensembles d'étiquettes sont très petit.
]

#slide(title: "Résultats")[
  #align(center)[
    #grid(
      columns: (1.3fr, 0.7fr),
      gutter: 1em,
      [#Merge_A],
      [_Merge_ exécuté avec les arguments $(t_e, t_t) = (0.4, 0.6)$]
    )
  ]
]

#slide(title: "Résultats")[
  #align(center)[
    #grid(
      columns: (1.3fr, 0.7fr),
      gutter: 1em,
      [#Merge_B(height: 90%)],
      [_Merge_ exécuté avec les arguments $(t_e, t_t) = (0.4, 0.6)$]
    )
  ]
]

#slide(title: "Résultats")[
  #align(center)[
    #Merge_C(height: 80%)
    _Merge_ exécuté avec les arguments $(t_e, t_t) = (0.4, 0.6)$
  ]
]

#slide(title: "Résultats")[
  #align(left)[
    #grid(
      columns: (1.5fr, 1fr),
      gutter: 1em,
      [#Split_Img],
      [_Split_ exécuté avec les arguments $(t_e, t_t) = (0.4, 0.6)$]
    )
  ]
]

#slide(title: "Résultats")[
  == YAGO3
  La seconde base de données que nous avons utilisée pour tester nos critères de qualité de données est _Yago3_ @mahdisoltani2014yago3. Nous n'avons dégradé qu'un poucent des arcs de celle-ci.

  Les tests conduit démontrent que nos indicateurs de qualité de données ne détectent pas d'erreurs. Les indicateurs de profilage quant à eux détectent les dégradation des arcs.
]

#slide(title: "Résultats")[
  #align(left)[
    #grid(
      columns: (1.2fr, 1fr),
      gutter: 1em,
      [#Yago2],
      [Échantillon de la base de données.\ Les segments blanc modélisent les arcs et les noeuds forment le cercle.]
    )
  ]
]

#slide(title: "Résultats")[
  #fig-wrap[
    #Profiling_Properties
    #figh(
      [Profilage des propriétés des arcs de la base de données YAGO],
      [Illustration de l'interface utilisateur de *data-quality* @lugolbis2026github.],
    )
  ] <fig26>
]

#slide(title: "Résultats")[
  #grid(
    columns: (1.4fr, 0.6fr),
    gutter: 1em,
    [#Query_Validation],
    [Validation par requête -- de la base de données YAGO\ Illustration de l'interface utilisateur de *data-quality* @lugolbis2026github.]
  )
]

#slide(title: "Conclusion", outlined: true)[
  = Conclusion
  - Intérêt des indicateur de qualité de données et des indicateurs de profilage

  - Problèmes ouvert : analyse de l'étiquetage, standard _DDL_ et formes normales (NF).
]

// Bibliography
#bibliography-slide(bibliography("../references.bib"))