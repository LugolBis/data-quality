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
  lang: "en",
)

#set heading(numbering: "1.1 -")

#set par(justify: true)
#show figure.where(kind: "custom-fig"): it => it.body

#let code(content, font-size: 10pt) ={
  block(
    [#text(content, font: "JetBrains Mono", size: font-size)],
    fill: luma(230),
    radius: 4pt,
    inset: 10pt,
    width: 100%,
  )
}

#let alinea = [#h(1.5em)]

#align(center)[
  #image("../assets/img/logoups.svg", height: 16%)
  #v(2cm)

  #text(size: 25pt, weight: "bold")[
    Data Quality of Graph Databases
  ]

  #v(0.5cm)

  #text(size: 16pt)[
    M1 Computer Science — Research Report\
  ]
  #text(size: 14pt)[
    Data Quality of Graph Databases
  ]

  #v(8cm)

  #text(size: 14pt)[
    Authors: Loïc DESMARÈS and Tianyi YANG\
    Supervisors: Béatrice FINANCE and Zoubida KEDAD
  ]

  #v(0.5cm)

  #text(size: 14pt)[
    Université Paris-Saclay — UVSQ\
    Academic Year 2025–2026
  ]
]

#pagebreak()
#set par(leading: 0.50em)
#outline(
  title: "Table of Contents",
  depth: 3,
)
#set par(leading: 0.65em)
#pagebreak()

#alinea *Abstract*: The rise of digital technologies and the proliferation of heterogeneous data sources have led to an increasing adoption of graph-oriented databases, and more specifically the property graph model. This model is distinguished by its semantic richness and structural flexibility: by enabling each node and each edge to be associated with a set of labels and properties, it provides a natural and expressive representation of entities and their relationships across various domains such as social networks, bioinformatics, large-scale knowledge management, and artificial intelligence systems.\
#alinea Although the state of the art and standardization of property graphs has evolved considerably, data quality aspects remain largely unexplored. Yet, as with Big Data environments, the value extracted from a graph database fundamentally relies on the reliability, consistency, completeness, and accuracy of the data it contains. The present study proposes to analyze and adapt existing data quality assessment frameworks to the specific context of property graphs, taking into account the constraints inherent to this model — notably the absence of a rigid schema, the multiplicity of data sources, and the diversity of data types. We formulate a set of quality dimensions and indicators relevant to this context, and discuss feasible assessment methods, thereby laying the groundwork for a data quality evaluation process tailored to graph databases.

= Introduction
#label("def1")

#alinea This study aims to establish data quality criteria for graph databases. We consider here *Property Graphs* endowed with *labels*.

*Definition 1.*\
#alinea A property graph is a tuple $G = (N, E, rho, lambda, sigma)$ such that:
+ $N$ is a finite set of nodes (also referred to as vertices).
+ $E$ is a finite set of directed edges (referred to as edges when direction is not considered).
+ $rho: E -> (N times N)$ is a total function that maps each edge in $E$ to a pair $(n_"source", n_"destination")$. This node pair is non-commutative, since $(n_A, n_B) in rho(E)$ does not necessarily imply $(n_B, n_A) in rho(E)$.
+ $lambda: (N union E) -> "SET"^+(L)$ is a partial function that assigns a set of labels from $L$ to each node or edge ($lambda$ is a labeling function for nodes and edges).
+ $sigma: (N union E) times P -> "SET"^+(V)$ is a partial function that maps property values $V$ to properties $P$ of nodes and edges. We shall subsequently denote, for all $(o, p) in (N union E) times P$, the assigned values $sigma(o, p) = {v_1, ..., v_n}$ as $(o, p) = arrow(v)$.

#pagebreak()
= Data Quality of a Property Graph
== Completeness
*Definition 2.1.0*\
#alinea Completeness measures the amount of missing data in a graph database @cai2016challenges.

=== Component Existence
#label("def2.1.1")
#alinea The existence of connected or strongly connected components is a method for verifying data completeness. Indeed, edges model a large portion of the relationships between objects and carry significant semantic meaning.\
#alinea More intuitively, verifying the existence of components among sets of nodes and edges enables the expression of path (resp. walk) constraints. Naturally, adding constraints such as path lengths or the membership of a set of labels to these paths constitutes robust tools for capturing complex semantic meaning.

*Definition 2.1.1*\
#alinea Let $G_p$ be a graph pattern modeling a connected (resp. strongly connected) component, a set $O$ such that $O in {N, E, N union E}$, and $L_O subset.eq L$ a set of labels. Such that $forall (G_p, O, L_O)$, we have $forall o in O$ such that $lambda(o) = L_O$, $exists$ at least one occurrence of $G_p$ for $o$. See *@fig1[Figure]* in the appendix.

=== Node Degree
#label("def2.1.2")
#alinea Data completeness can also be expressed through node degree, thereby enabling the expression of cardinality constraints.

*Definition 2.1.2*\
#alinea Let $L_O subset.eq L$ be a set of labels, and $D_s, D_e subset RR^2$ be sets representing, respectively, the allowed out-degree and in-degree ranges. Such that $forall n in N$ such that $lambda(n) = L_O$ satisfies $d^+(n) in D_s$ and $d^-(n) in D_e$. See *@fig2[Figure]* in the appendix.

== Validity
#label("def2.2.0")
*Definition 2.2.0*\
#alinea Validity measures the validity of data formats.

=== String Format
#label("def2.2.1")
*Definition 2.2.1*\
#alinea Let $O in {N, E, N union E}$, $L_O subset.eq L$, $X subset.eq P$, and *Regex* encoding the expected format. Such that $forall o in O$ we verify that $forall v in sigma(o, X)$, $"match"(v, "Regex") = "True"$. See *@fig3[Figure]* in the appendix.

=== Date Format
#label("def2.2.2")
*Definition 2.2.2*\
#alinea Let $O in {N, E, N union E}$, $L_O subset.eq L$, $X subset.eq P$, and *$"Date"_"fmt"$* encoding the expected date format. Such that $forall o in O$ we verify that $forall v in sigma(o, X)$, $"match"(v, "Date"_"fmt") = "True"$. See *@fig4[Figure]* in the appendix.

=== Finite Data Domain
#label("def2.2.3")
*Definition 2.2.3*\
#alinea Let $O in {N, E, N union E}$, $L_O subset.eq L$, $X subset.eq P$, $I$ a data domain (including non-atomic values), and $C$ an optional constraint (see @def2.3.2[Definition]). Such that $forall o in O$ we verify $"SET"(sigma(o, X)) subset.eq I and C(o) = "True"$. See *@fig5[Figure]* in the appendix.

=== Set-Based Labeling
#label("def2.2.4")
*Definition 2.2.4*\
#alinea Let $O in {N, E, N union E}$, $L_X, L_Y subset.eq L$, and $"Op"_"set" in { subset, subset.eq, \\ }$ a set operator. Such that $forall o in O$ such that $L_X subset.eq lambda(o)$ satisfies $lambda(o) "Op"_"set" L_Y = "True"$. See *@fig6[Figure]* in the appendix.

#alinea Note that only the partial implementation of this definition is meaningful within the *Neo4j* graph database framework, as edges (_Relationships_) may carry only a single label.

=== Clustering-Based Labeling
#label("def2.2.5")
#alinea The intuition is as follows: similar nodes should share the same label set. To measure labeling quality, we seek to group similar nodes in order to detect labeling errors. The approach described below is inspired by an embedding system motivated by @Giot2015VisualGraph. The proposed approach proceeds as follows:
+ #alinea Define a similarity criterion between two nodes: we focus here on node labels and their semantic meaning. Our interest thus lies in the relationships between different label sets. These relationships are modeled by a semantically rich concept: edges. Indeed, edges are characterized by a directional node pair and a label set. We therefore propose to encode this semantic meaning as character strings. Thus the following edge:\
  #code([($"Node"_1$: {Student,Person})-[$"Edge"$:{EnrolledIn}]->($"Node"_2$: {University})])
  Would be translated as "OU:EnrolledIn:University" (which we term a _Token_) from the perspective of $"Node"_1$, and as "IN:EnrolledIn:StudentPerson" from that of $"Node"_2$.
+ #alinea Define a method for computing similarity between two _Tokens_. Since a _Token_ encodes complex semantic relationships as a character string, the use of edit distance seems most appropriate. We therefore employ *Levenshtein* similarity to compute the similarity between two _Tokens_.
+ #alinea Define a method for computing similarity between two nodes. We consider both their relationships and their labels, combining similarity scores along these two dimensions. We use the *Jaccard* index to compute node similarity with respect to label sets, such that $forall n_1, n_2 in N^2$, $"Similarity"_"Labels" = 1-(|lambda(n_1) inter lambda(n_2)|)/(|lambda(n_1) union lambda(n_2)|)$.\
  #alinea The similarity between two nodes with respect to their _Token_ sets is computed using *Monge-Elkan* (ME) similarity, such that $forall n_1, n_2 in N^2$, $"ME"(n_1, n_2) = 1 / abs(sigma(n_1, {"Tokens"})) sum_(t_1 in sigma(n_1, {"Tokens"})) max_(t_2 in sigma(n_2, {"Tokens"})) ("Levenshtein_Similarity"(t_1, t_2))$ (resp. $"ME"(n_2, n_1)$),
  such that $"Similarity"_"Tokens" = ("ME"(n_1, n_2) + "ME"(n_2, n_1))/2$. Token similarity could alternatively be computed using the *Fuzzy Jaccard* algorithm (less precise) or the *Kuhn-Munkres* algorithm (optimal but with $O(|N|^3)$ complexity).

The following algorithms are defined:\
#alinea The _Tokenization_ algorithm generates a set of _Tokens_ (representing the relationships of a node) for all nodes possessing at least one incoming or outgoing edge. Equivalently: any node with non-zero in- or out-degree acquires a "Tokens" property storing the set of _Tokens_ generated for it.\
#alinea The _CreateTokens_ algorithm generates a set of connected nodes representing the distinct _Tokens_ produced by the _Tokenization_ algorithm. Once these nodes are created, _CreateTokens_ computes the *Levenshtein* similarity between each pair of _Tokens_ and stores it as an edge between them.

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
  #comment("Step - 1", inline: true)\
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
  #comment("Step - 2", inline: true)\
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
  #comment("We compute the similarity between the tokens.", inline: true)\
  for $(n_1, n_2)$ in $N^2$ do#i\
  if $lambda(n_1) = lambda(n_2) = {"TOKEN"}$\
  and $sigma(n_1, {"ID"}) < sigma(n_2, {"ID"})$ do#i\
  $"t1", "t2" <- sigma(n_1, {"VAL"}), sigma(n_2, {"VAL"})$\
  $"sim" <- "Levenshtein_Similarity"("t1", "t2")$\
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
    [#text(size: 12pt)[$G$ PG., $t_e$ label similarity threshold, $t_t$ Token similarity threshold]],
  ),
  indent-size: 8pt,
  indent-guides: 1pt + gray,
  row-gutter: 6pt,
  column-gutter: 5pt,
  inset: 8pt,
  stroke: 2pt + black,
  breakable: false,
)[
  #comment("Step - 3: Detection of nodes that should belong", inline: true)\
  #comment("to the same label cluster.", inline: true)\
  for $(n_1, n_2)$ in $N^2$ do#i\
  if $sigma(n_1, {"ID"}) < sigma(n_2, {"ID"})$\
  and $sigma(n_1, {"Tokens"}) != "NULL"$\
  and $sigma(n_2, {"Tokens"}) != "NULL"$ do#i\
  $"Similarity"_"Labels" <- (|lambda(n_1) inter lambda(n_2)|)/(|lambda(n_1) union lambda(n_2)|)$\
  if $"Similarity"_"Labels" >= t_e$ do#i\
  skip this iteration;#d\
  end\
  \
  $"Similarity"_"Tokens" <- ("ME"(n_1, n_2), "ME"(n_2, n_1))/2$\
  if $"Similarity"_"Tokens" >= t_t$ do#i\
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
  #comment("Line 8:", inline: true)\
  if $"Similarity"_"Labels" <= t_e$ do\
  #comment("[...]", inline: true)\
  #comment("Line 21:", inline: true)\
  if $"Similarity"_"Tokens" <= t_t$#i\
  #comment("[...]", inline: true)\
  #comment("Line 25:", inline: true)\
  $lambda(e) <- {"SPLIT"}$#d\
]]

#grid(
  columns: (0.9fr, 1.1fr),
  gutter: 1em,
  [
    #Tokenization
    #alinea The _Tokenization_ algorithm has linear time complexity $O(n)$ (where $n = |E|$) and worst-case (very rare) space complexity $O(n times m)$ (where $n = |N|$ and $m = |L|$). The _CreateTokens_ algorithm has polynomial time complexity $O(n^2)$ (where $n = |N|$) and worst-case (very rare) space complexity $O(n^2)$ (where $n = 2|E|$).
  ],
  [
    #CreateTokens
  ],
)

#alinea Once the _Tokenization_ and _CreateTokens_ algorithms have been applied, node groupings can be analyzed using Token set similarity alongside *Jaccard* similarity for label sets. Grouping is performed pairwise, storing only a single edge connecting nodes that should be "Merged" (those that should share a similar label set) or "Split" (those that should not share a similar label set). This selection is governed by two similarity thresholds: the first pertains to label similarity (used to filter node pairs that may exhibit labeling errors), and the second concerns Token similarity, determining whether a "Merge" / "Split" edge is created.

#Merge

#alinea The _Merge_ algorithm described above therefore detects all node pairs whose label similarity is $<$ the threshold $t_e$, and for which Token similarity is $>=$ the threshold $t_t$. In other words, the algorithm detects nodes that, based on their relational similarity (_Token_), should share a more similar label set (and hence should be merged). See *@fig7[Figure]* in the appendix.\
\

#grid(
  columns: (1fr, 1fr),
  gutter: 1em,
  [
    #alinea This algorithm can readily be adapted to detect the inverse: "Split" designating node pairs that should not share similar label sets. To effect the necessary changes, it suffices to modify lines [8, 21, 25] of the _Merge_ algorithm as follows.
  ],
  [
    #Split
  ],
)

#pagebreak()
== Consistency
*Definition 2.3.0*\
#alinea Consistency measures the validity of relationships within the graph database.

=== Functional Dependency (FD)
#label("def2.3.1")
*Definition 2.3.1*\
#alinea Let $O in {N, E, N union E}$, $L_O subset.eq L$, and $X, Y subset.eq P$; we define $(O, L_O, X -> Y)$ as a *FD*. Such that $forall o_1, o_2 in O^2$ such that $lambda(o_1) = L_O$ and $lambda(o_2) = L_O$ satisfies $sigma(o_1, X) = sigma(o_2, X) arrow.double sigma(o_1, Y) = sigma(o_2, Y)$. See *@fig8[Figure]* in the appendix.

=== Conditional Functional Dependency (CFD)
#label("def2.3.2")
*Definition 2.3.2.a*\
#alinea A *condition* is a tuple $C = (P_C, "VAL", f, "NEXT")$ such that:
+ $P_C subset.eq P$ is the set of properties that must satisfy the condition.
+ $"VAL" in {"constant", P}$ is the comparison value. The "constant" may be of any data type (including non-atomic types).
+ $f: (N union E, P_C, "VAL") -> "Boolean"$, is a function for verifying the condition on an object (e.g., "$=$", "$<$", "$in$", etc.). We shall denote by $C(o)$ the fact that object $o$ satisfies $f(o, P_C, "VAL")$, given $P_C$ and $"VAL"$ as defined in $C$.
+ $"NEXT" in {emptyset, ("Condition", "Boolean operator")}$ is an optional second condition to be verified (enabling its combination with the first via the "Boolean operator").
*Definition 2.3.2.b*\
#alinea Let $O in {N, E, N union E}$, $L_O subset.eq L$, $C$ a condition (see @def2.3.2[Definition]), and $X, Y subset.eq P$; we define $(O, L_O, C, X -> Y)$ as a *CFD*. Such that $forall o_1, o_2 in O^2$ such that $lambda(o_1) = L_O$ and $lambda(o_2) = L_O$ and $C(o_1) = "True"$ and $C(o_2) = "True"$ satisfies $sigma(o_1, X) = sigma(o_2, X) arrow.double sigma(o_1, Y) = sigma(o_2, Y)$. See *@fig9[Figure]* in the appendix.

=== Graph Pattern Functional Dependency (GFD)
#label("def2.3.3")
*Definition 2.3.3*\
#alinea Let $G_p$ be a graph pattern from which we derive $G'(N', E')$, a subgraph of $G$ corresponding to $G_p$; $O in {N, E, N union E}$, $L_O subset.eq L$, and $X, Y subset.eq P$; we define $(O, L_O, G_p, X -> Y)$ as a *GFD*. Such that $forall o_1, o_2 in O^2$ such that $o_1, o_2 in G'$ satisfies $sigma(o_1, X) = sigma(o_2, X) arrow.double sigma(o_1, Y) = sigma(o_2, Y)$. See *@fig10[Figure]* in the appendix.\
#alinea An alternative approach (fundamentally different) termed _gFD_ @Manouvrier2024PGFD consists of excluding all nodes that do not possess all properties ($X union Y$) defined by the _FD_.

=== Query-Based Validation
#label("def2.3.4")
#alinea Functional dependencies (_FD_, _CFD_, and _GFD_) are powerful tools. However, they are complex to extend so as to fully capture the semantic richness expressible by queries. For this reason, an additional validation approach — modeled after _dbt_ — would consist of validating or invalidating queries written by the user.\
*Definition 2.3.4*\
#alinea This query-based validation system is defined by a tuple _dgt_ $= (R, B)$ such that:
+ $R$ is a query, as expressive as the query language permits, that may or may not return objects.
+ $B$ is a boolean value indicating whether $R$ must return objects in order to validate the constraint it defines.\
See *@fig11[Figure]* in the appendix.

== Integrity
*Definition 2.4.0*\
#alinea Integrity measures the structural validity of a graph database.

=== Property Schema Validity
#label("def2.4.1")
#alinea No _DDL_ standard has yet emerged for graph databases. We therefore define three integrity constraints:
+ *Property Uniqueness*:\
  Let $O in {N, E, N union E}$, $L_O subset.eq L$, and $X subset.eq P$ such that $forall o_1, o_2 in O^2$ satisfies $sigma(o_1, X) = sigma(o_2, X) arrow.double o_1 = o_2$. See *@fig12[Figure]* in the appendix.
+ *Property Existence*:\
  Let $O in {N, E, N union E}$, $L_O subset.eq L$, and $X subset.eq P$ such that $forall o in O$ satisfies $"NULL" in.not sigma(o, X)$. See *@fig13[Figure]* in the appendix.
+ *Property Value Types*:\
  Let $t: (V) -> "SET"^+(T)$ be a total function assigning a set of types $T$ to a set of values $V$, $O in {N, E, N union E}$, $L_O subset.eq L$, $X subset.eq P$, and $Y subset.eq T$ such that $forall o in O$ satisfies $(t compose sigma)(o, X) subset.eq Y$. See *@fig14[Figure]* in the appendix.
Note that these constraints can be expressed in *Cypher* (the query language of *Neo4j*).

=== Index Validity
#label("def2.4.2")
#alinea The intuition is as follows: missing values on indexed properties may signal degradation of the integrity of the graph database.\
*Definition 2.4.2*\
#alinea Let $i: (N times E) -> "BITSET"$ denote indexed properties; $forall o in (N union E)$ we verify $"NULL" in.not i(o) dot.o sigma(o, P)$. See *@fig15[Figure]* in the appendix.

=== Normal Form of a Property Graph
#label("def2.4.3")
Algorithm:\

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

#alinea The algorithm is formulated within the framework of *gFD* and *gUC* @Skavantzos2023Normalization, which can readily be instantiated by *FD* (see @def2.3.1[Definition]). Whereas *CFD*s and *GFD*s (graph pattern functional dependencies) are not meaningful in a normalization context, as the algorithm would normalize to 3NF only a fragment of the database. See *@fig16[Figure]* in the appendix.

== Uniqueness
*Definition 2.5.0*\
#alinea Uniqueness measures the redundancy of a graph database.

=== Edge Duplicates
#label("def2.5.1")
*Definition 2.5.1*\
#alinea $forall e_1, e_2 in E^2$, $e_1$ and $e_2$ are duplicates if and only if: $rho(e_1) = rho(e_2)$, $lambda(e_1) = lambda(e_2)$, and $sigma(e_1, P) = sigma(e_2, P)$. See *@fig17[Figure]* in the appendix.

=== Node Duplicates
#label("def2.5.2")
*Definition 2.5.2*\
#alinea $forall n_1, n_2 in N^2$, $n_1$ and $n_2$ are duplicates if and only if: $lambda(n_1) = lambda(n_2)$ and $sigma(n_1, P) = sigma(n_2, P)$. See *@fig18[Figure]* in the appendix.\
#alinea This definition could be relaxed by also taking into account the edges incident to nodes, stipulating that nodes sharing more than a given threshold of common edges are considered duplicates.

#pagebreak()
= Profiling of a Property Graph
#alinea The purpose of profiling a graph database is to obtain a dashboard view of the data distribution. This section therefore collects indicators of interest for characterizing the data of a property graph. These indicators do not constitute data quality metrics per se, as their general-purpose nature cannot capture the domain-specific use cases intrinsic to a graph database.
== Completeness
=== Weakly Connected Components
*Definition 3.1.1*\
#alinea Detection of connected components in the graph using the *WCC* algorithm.
=== Strongly Connected Components
*Definition 3.1.2*\
#alinea Detection of strongly connected components in the graph using the *SCC* algorithm (paths only are considered here).
== Validity
=== Detection of Inconsistent Property Types
*Definition 3.2.1*\
#alinea $forall p in P$ we verify that $forall o in N$ (resp. $E$), such that $sigma(o, {p}) eq.not "NULL"$, $exists$ a unique type $t_x$ such that $(t compose sigma)(o, {p}) = t_x$ (see @def2.4.1[Definition]). A concise dashboard listing properties for which the type is not unique is constructed from this detection.
== Integrity
=== Node Property Distribution
*Definition 3.3.1*\
#alinea Analysis of the distribution of properties defined for nodes, grouped by their label set.
=== Node Property Distribution by Label
*Definition 3.3.2*\
#alinea Analysis of the distribution of properties defined for nodes, grouped by each label individually attached to them.
=== Edge Property Distribution
#label("def3.3.3")
*Definition 3.3.3*\
#alinea Analysis of the distribution of properties defined for edges, grouped by their label set.\
#alinea Note that this restricted definition is equivalent to the per-label analysis under *Neo4j*, as edges (_Relationships_) carry only a single label.
== Labeling
=== Anomaly Detection via Clustering
*Definition 3.4.1*\
#alinea Using the *FastRP* algorithm, an _embedding_ is generated for each node from its numerical properties (_features_) and the graph topology. These _embeddings_ are then used to identify node clusters via the *KNN* algorithm. Once these clusters have been identified, results are filtered to retain those whose similarity meets or exceeds a given threshold. Finally, the labels of each node are compared against those of other nodes within the same cluster to detect potential labeling errors.\
#alinea It should be noted that this method is somewhat fragile, particularly because the _embeddings_ may be largely composed of default values (_padding_), thereby introducing significant bias into similarity computations. Alternative approaches, such as community detection using the *Louvain* algorithm, would also be applicable for this profiling use case.
== Readability
=== Node Degree Distribution
*Definition 3.5.1*\
#alinea Analysis of the degree distribution (in-degree and out-degree) of nodes grouped by their label set.
=== Multi-edge Detection
*Definition 3.5.2*\
#alinea Detection of edges sharing the same source and destination nodes, thereby forming a multigraph. A concise dashboard summarizing the label sets of the source and destination nodes, as well as the edge label sets, is constructed from this detection.
=== Graph Eccentricity Analysis
*Definition 3.5.3*\
#alinea Analysis of graph eccentricity: computation of the graph's radius and diameter.\
One can readily envision leveraging this information to analyze a graph modeling a network, for instance.
== Outliers
=== Numerical Outlier Detection
*Definition 3.6.1*\
#alinea Detection of numerical outliers in node and edge properties.\
This likewise enables data characterization and the detection, where applicable, of invalid values.
=== Transitive Node Influence Analysis
*Definition 3.6.2*\
#alinea The transitive influence of a node is determined by computing its _Eigenvector Centrality_, a measure from graph theory used to assess the importance of a node. This metric is computed by taking into account both the number of connections of a node and the importance of the nodes to which it is connected.\
#alinea This analysis enables measurement of node influence and the detection, where applicable, of nodes whose influence is inconsistent with the modeled domain.
=== Average Transitive Influence Analysis
*Definition 3.6.3*\
#alinea Analysis of the average transitive influence across the nodes of the graph.

#pagebreak()
= Implementation — Neo4j
#alinea *Neo4j* is a graph database offering a flexible implementation of the property graph model. Nodes are referred to as "Nodes" and edges as "Relationships". All concepts in *Neo4j* are consistent with the definition established in the introduction (see @def1[Definition]), with the exception that "Relationships" may carry only a single label. The implementation of the data quality framework established in this study is publicly available at @lugolbis2026github.
== Testing Methods
#alinea In order to evaluate the relevance of the data quality criteria we have defined, these criteria were tested on a variety of graph databases. These include graph databases of impeccable quality, such as those used in the official *Neo4j* documentation. For more chaotic, less synthetic data, we employed graph databases derived from the transformation of knowledge bases (such as the _YAGO3 Knowledge Base_) and artificially degraded their data.\


#alinea We deliberately avoided graph databases derived from relational database transformations, in order to decouple our evaluation from the relational model. Furthermore, no in-depth testing was conducted on *RDF* databases such as _DBpedia_, which proved semantically insufficient due to its limited label and property diversity.\

== Test Results
=== Northwind
#label("northwind")
#alinea The _Northwind_ database, prominently featured in the official *Neo4j* documentation, was used for evaluation. This dataset presents numerous advantages, including semantic richness — particularly in terms of labels — enabling the evaluation of some of the most complex indicators (e.g., @def2.2.5[Clustering-Based Labeling]). The data were therefore degraded to simulate a dynamic, non-synthetic database.\
#alinea These degradations include the deletion of 5% of edges, the corruption of 5% of date formats, the violation of 5% of constraints (*FD*, existence, type, and uniqueness), and the modification of the label set for 2% of nodes in each distinct label group.\
\
#alinea Results for _seed_ 42 were conclusive for the detection of missing edges via the approach of @def2.1.1[Definition], as well as for the indicators defined in: @def2.2.2[], @def2.3.1[], @def2.3.2[], @def2.3.3[], @def2.3.4[], @def2.4.1[]. Clustering-Based Labeling also proved conclusive, although experimentation revealed certain limitations in its approach.\
\
#alinea Indeed, for a graph database in which all nodes are associated with a single label, the label similarity filtering for the _Merge_ and _Split_ algorithms becomes polarized, restricting the possible values of $"Similarity"_"Labels"$ to 0.0 and 1.0. This reduces the flexibility of the indicator and may inevitably lead to false positives (i.e., the erroneous detection of errors). Nevertheless, this approach remains effective in the majority of cases for capturing complex semantic meaning and detecting labeling errors.\
#alinea *@fig19[Figure]* shows an execution of the _Merge_ algorithm, in which each distinct node color corresponds to a distinct label set. It is noteworthy that labeling error detection manifests as nodes with high degree. Note that the graph shown is restricted to edges $e$ such that $lambda(e) = {"Merge"}$. A more detailed examination of *@fig20[Figure]* and *@fig21[Figure]* clearly demonstrates that nodes whose labeling was degraded are detected as highly similar to their true labeling, through the intact semantic dimension of their relationships — the edges. Although our indicator constructs the full graph without excluding any similarity relation, one could readily envision an analytical solution based, for instance, on mean node degree or a clustering method to reduce the number of nodes to be analyzed.\
\
#alinea Finally, *@fig22[Figure]* clearly illustrates the labeling error detected by the _Split_ algorithm. The central node to which all others are connected exhibits a clear labeling error, as all nodes linked to it share the same label set. In other words, the nodes from which edges $e$ such that $lambda(e) = {"Split"}$ are outgoing are pairwise similar. In any case, the indicator we have defined constitutes a robust tool for analyzing the labeling quality of a graph database.

=== YAGO3
#label("yago3")
#alinea The second database used to evaluate our data quality criteria is _Yago3_ @mahdisoltani2014yago3. To provide a meaningful point of comparison, only a minimal set of degradations was applied. Specifically, the values of $1%$ of edges were degraded, and the dataset was restricted to the first $50 000$ lines (yielding $63 563$ nodes and $50 000$ edges). Furthermore, edge predicates were used as edge labels.\
\
#alinea The test results were particularly conclusive: our indicators detected no data quality issues on the non-degraded portion of the dataset. Unsurprisingly, the data quality of this knowledge base is exemplary. *@fig23[]*, *@fig24[]*, and *@fig25[]* present a small yet representative sample of the data. The data homogeneity is such that the _Merge_ and _Split_ algorithms of the Clustering-Based Labeling indicator detected no errors.\
\
#alinea The profiling carried out via @def3.3.3[Edge Property Distribution] revealed the absence of a key property for a negligible fraction of edges (\~$0.40%$), as illustrated in *@fig26[Figure]*. Finally, *@fig27[Figure]* illustrates the use of @def2.3.4[Query-Based Validation] to detect the previously degraded data.

= Conclusion
#alinea This study has identified a substantial number of data quality indicators that prove both relevant and well-suited to the property graph model. Moreover, when combined with a profiling system, they provide a comprehensive overview of graph database content. The semi-structured nature of property graphs constitutes a powerful tool for expressing complex semantic concepts. Fully capturing the semantic richness of graph databases remains a significant challenge, given the diversity of their application contexts.\
#alinea Significant challenges therefore remain, whether in the analysis of labeling quality, data validity (for which many complex checks could be standardized via a dedicated _DDL_), or the normal forms of a property graph.

#pagebreak()
= Appendix
#alinea This appendix collects graph figures illustrating the definitions established in the preceding sections.

#let cmp-ok-en = "Respects the constraint"
#let cmp-err-en = "Violates the constraint"

#fig-wrap[
  #cmp(
    Graph-211-1,
    Graph-211-2,
    ok-txt: cmp-ok-en,
    err-txt: cmp-err-en
  )
  #figh([Figure 1: Example for _@def2.1.1[Definition]_], [#Example-211])
] <fig1>

#fig-wrap[
  #cmp(
    Graph-212-1,
    Graph-212-2,
    ok-txt: cmp-ok-en,
    err-txt: cmp-err-en
  )
  #figh([Figure 2: Example for _@def2.1.2[Definition]_], [#Example-212])
] <fig2>

#fig-wrap[
  #cmp(
    Graph-221-1,
    Graph-221-2,
    ok-txt: cmp-ok-en,
    err-txt: cmp-err-en
  )
  #figh([Figure 3: Example for _@def2.2.1[Definition]_], [#Example-221])
] <fig3>

#fig-wrap[
  #cmp(
    Graph-222-1,
    Graph-222-2,
    ok-txt: cmp-ok-en,
    err-txt: cmp-err-en
  )
  #figh([Figure 4: Example for _@def2.2.2[Definition]_], [#Example-222])
] <fig4>

#fig-wrap[
  #cmp(
    Graph-223-1,
    Graph-223-2,
    ok-txt: cmp-ok-en,
    err-txt: cmp-err-en
  )
  #figh([Figure 5: Example for _@def2.2.3[Definition]_], [#Example-223])
] <fig5>

#fig-wrap[
  #cmp(
    Graph-224-1,
    Graph-224-2,
    ok-txt: cmp-ok-en,
    err-txt: cmp-err-en
  )
  #figh([Figure 6: Example for _@def2.2.4[Definition]_], [#Example-224])
] <fig6>


#fig-wrap[
  #block(width: 100%, inset: 8pt, fill: white, stroke: (paint: mg-s, thickness: 0.5pt), radius: 3pt)[
    #text(fill: mg-s, weight: "bold")[⊕ MERGE Suggestion]\
    Similar _Token_ sets ("OU:STUDY_AT:University", "OU:COMES_FROM:City").\
    Two label sets with low similarity are observed, in contrast to the high _Token_ similarity of these nodes.
    #v(5pt)
    #Graph-225-1
  ]

  #block(width: 100%, inset: 8pt, fill: white, stroke: (paint: sp-s, thickness: 0.5pt), radius: 3pt)[
    #text(fill: sp-s, weight: "bold")[⊖ SPLIT Suggestion]\
    Identical labels (:Person).\
    Distinct _Token_ sets are observed for nodes sharing the same label set.
    #text(style: "italic")[\ ]
    #text(style: "italic")[\ ]
    #v(5pt)
    #Graph-225-2
  ]
  #figh([Figure 7: Example for _@def2.2.5[Definition]_], [], display_desc: false)
] <fig7>

#fig-wrap[
  #cmp(
    Graph-231-1,
    Graph-231-2,
    ok-txt: cmp-ok-en,
    err-txt: cmp-err-en
  )
  #figh([Figure 8: Example for _@def2.3.1[Definition]_], [#Example-231])
] <fig8>

#fig-wrap[
  #cmp(
    Graph-232-1,
    Graph-232-2,
    ok-txt: cmp-ok-en,
    err-txt: cmp-err-en
  )
  #figh([Figure 9: Example for _@def2.3.2[Definition]_], [#Example-232])
] <fig9>

#fig-wrap[
  #cmp(
    Graph-233-1,
    Graph-233-2,
    ok-txt: cmp-ok-en,
    err-txt: cmp-err-en
  )
  #figh([Figure 10: Example for _@def2.3.3[Definition]_], [#Example-233])
] <fig10>


#fig-wrap[
  #cmp(
    Graph-234-1,
    Graph-234-2,
    ok-txt: cmp-ok-en,
    err-txt: cmp-err-en
  )
  #figh([Figure 11: Example for _@def2.3.4[Definition]_], [#Example-234])
] <fig11>

#fig-wrap[
  #cmp(
    Graph-241-1,
    Graph-241-2,
    ok-txt: cmp-ok-en,
    err-txt: cmp-err-en
  )
  #figh([Figure 12: Example for _@def2.4.1[Definition 1 of]_], [#Example-241a])
] <fig12>

#fig-wrap[
  #cmp(
    Graph-241-3,
    Graph-241-4,
    ok-txt: cmp-ok-en,
    err-txt: cmp-err-en
  )
  #figh([Figure 13: Example for _@def2.4.1[Definition 2 of]_], [#Example-241b])
] <fig13>

#pagebreak()
#fig-wrap[
  #cmp(
    Graph-241-5,
    Graph-241-6,
    ok-txt: cmp-ok-en,
    err-txt: cmp-err-en
  )
  #figh([Figure 14: Example for _@def2.4.1[Definition 3 of]_], [#Example-241c])
] <fig14>

#fig-wrap[
  #cmp(
    Graph-242-1,
    Graph-242-2,
    ok-txt: cmp-ok-en,
    err-txt: cmp-err-en
  )
  #figh([Figure 15: Example for _@def2.4.2[Definition]_], [#Example-242])
] <fig15>

#pagebreak()
#fig-wrap[
  #block(width: 100%, inset: 8pt, fill: white, stroke: (paint: err-s, thickness: 0.5pt), radius: 3pt)[
    #text(size: 7.5pt, fill: err-s, weight: "bold")[✗ Not normalized]
    #v(5pt)
    #Graph-243-2
  ]
  #block(width: 100%, inset: 8pt, fill: white, stroke: (paint: ok-s, thickness: 0.5pt), radius: 3pt)[
    #text(size: 7.5pt, fill: ok-s, weight: "bold")[✓ Normalized (3NF)]
    #v(5pt)
    #Graph-243-1
  ]
  #figh([Figure 16: Example for _@def2.4.3[Definition]_], [], display_desc: false)
] <fig16>

#fig-wrap[
  #cmp(
    Graph-251-1,
    Graph-251-2,
    ok-txt: cmp-ok-en,
    err-txt: cmp-err-en
  )
  #figh([Figure 17: Example for _@def2.5.1[Definition]_], [], display_desc: false)
] <fig17>

#fig-wrap[
  #cmp(
    Graph-252-1,
    Graph-252-2,
    ok-txt: cmp-ok-en,
    err-txt: cmp-err-en
  )
  #figh([Figure 18: Example for _@def2.5.2[Definition]_], [], display_desc: false)
] <fig18>

#fig-wrap[
  #block(width: 100%, inset: 8pt, fill: white, stroke: (paint: mg-s, thickness: 0.5pt), radius: 3pt)[
    #text(fill: mg-s, weight: "bold")[⊕ MERGE Suggestion]\
    #Merge_A
  ]
  #figh(
    [Figure 19: Execution of the _Merge_ algorithm on the _Northwind_ database],
    [_Northwind_ database (@northwind[see ]) degraded with _seed_ 42 and\ _Merge_ executed with arguments $(t_e, t_t) = (0.4, 0.6)$.],
  )
] <fig19>

#fig-wrap[
  #block(width: 100%, inset: 8pt, fill: white, stroke: (paint: mg-s, thickness: 0.5pt), radius: 3pt)[
    #text(fill: mg-s, weight: "bold")[⊕ MERGE Suggestion]\
    #Merge_B()
  ]
  #figh(
    [Figure 20: Execution of the _Merge_ algorithm on the _Northwind_ database],
    [_Northwind_ database (@northwind[see ]) degraded with _seed_ 42 and\ _Merge_ executed with arguments $(t_e, t_t) = (0.4, 0.6)$.],
  )
] <fig20>

#fig-wrap[
  #block(width: 100%, inset: 8pt, fill: white, stroke: (paint: mg-s, thickness: 0.5pt), radius: 3pt)[
    #text(fill: mg-s, weight: "bold")[⊕ MERGE Suggestion]\
    #Merge_C()
  ]
  #figh(
    [Figure 21: Execution of the _Merge_ algorithm on the _Northwind_ database],
    [_Northwind_ database (@northwind[see ]) degraded with _seed_ 42 and\ _Merge_ executed with arguments $(t_e, t_t) = (0.4, 0.6)$.],
  )
] <fig21>

#fig-wrap[
  #block(width: 100%, inset: 8pt, fill: white, stroke: (paint: sp-s, thickness: 0.5pt), radius: 3pt)[
    #text(fill: sp-s, weight: "bold")[⊖ SPLIT Suggestion]\
    #Split_Img
  ]
  #figh(
    [Figure 22: Execution of the _Split_ algorithm on the _Northwind_ database],
    [_Northwind_ database (@northwind[see ]) degraded with _seed_ 42 and\ _Split_ executed with arguments $(t_e, t_t) = (0.7, 0.4)$.],
  )
] <fig22>

#fig-wrap[
  #Yago1
  #figh(
    [Figure 23: Sample from the @yago3[_YAGO3_] database],
    [],
    display_desc: false,
  )
] <fig23>

#fig-wrap[
  #Yago2
  #figh(
    [Figure 24: Sample from the @yago3[_YAGO3_] database],
    [White segments represent edges, and nodes form the outer circle.],
  )
] <fig24>

#fig-wrap[
  #Yago3
  #figh(
    [Figure 25: Sample from the @yago3[_YAGO3_] database],
    [],
    display_desc: false,
  )
] <fig25>

#fig-wrap[
  #Profiling_Properties
  #figh(
    [Figure 26: Edge property profiling of the @yago3[_YAGO3_] database],
    [Screenshot of the *data-quality* user interface @lugolbis2026github.],
  )
] <fig26>

#fig-wrap[
  #Query_Validation
  #figh(
    [Figure 27: @def2.3.4[Query-Based Validation] of the @yago3[_YAGO3_] database],
    [Screenshot of the *data-quality* user interface @lugolbis2026github.],
  )
] <fig27>

// References
#pagebreak()
#bibliography("../references.bib", title: "Bibliography")
