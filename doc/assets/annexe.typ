#import "@preview/fletcher:0.5.8" as fletcher: diagram, edge, node

#set page(paper: "a4", margin: (top: 1.4cm, bottom: 1.4cm, left: 1.5cm, right: 1.5cm))
#set text(font: "New Computer Modern", size: 9pt)
#set heading(numbering: none)
#set par(justify: false)

// Color Palette

#let ok-f = rgb("#d4edda")
#let ok-s = rgb("#155724")
#let err-f = rgb("#f8d7da")
#let err-s = rgb("#721c24")
#let neu-f = rgb("#d0e4f7")
#let neu-s = rgb("#1a3a6b")
#let mg-f = rgb("#f3e5f5")   // MERGE
#let mg-s = rgb("#6a0dad")
#let sp-f = rgb("#fff3e0")   // SPLIT
#let sp-s = rgb("#e65100")

// Constants
#let cmp-ok = [Respecte la contrainte]
#let cmp-err = [Viole la contrainte]

// Functions

// Node content: bold label then smaller property lines
#let pgn(lbl, ..props) = align(left, {
  text(weight: "bold", size: 8pt, lbl)
  if props.pos().len() > 0 {
    linebreak()
    props.pos().map(p => text(size: 7pt, p)).join(linebreak())
  }
})

#let myn(coord, data, name, fill, stroke) = {
  node(coord, [#pgn(..data)], name: name, corner-radius: 4pt, shape: circle, fill: fill, stroke: stroke)
}

// Edge label
#let el(s) = text(size: 6.5pt, s)

// Ok / Err two-column comparison
#let cmp(ok, err, ok-txt: cmp-ok, err-txt: cmp-err) = grid(
  columns: (1fr, 1fr),
  column-gutter: 10pt,
  block(width: 100%, inset: 8pt, fill: white, stroke: (paint: ok-s, thickness: 0.5pt), radius: 3pt)[
    #text(size: 7.5pt, fill: ok-s, weight: "bold")[✓ #ok-txt]
    #v(5pt)
    #ok
  ],
  block(width: 100%, inset: 8pt, fill: white, stroke: (paint: err-s, thickness: 0.5pt), radius: 3pt)[
    #text(size: 7.5pt, fill: err-s, weight: "bold")[✗ #err-txt]
    #v(5pt)
    #err
  ],
)

#let graf(objets) = {
  diagram(
    ..objets,
    spacing: (30pt, 30pt),
  )
}

// Definition header banner
#let dh(num, title, desc) = {
  v(10pt)
  block(
    width: 100%,
    fill: rgb("#eef2ff"),
    stroke: (paint: neu-s, thickness: 0.5pt),
    radius: 3pt,
    inset: (x: 9pt, y: 5pt),
  )[
    #text(weight: "bold")[Déf. #num — #title]\
    #text(style: "italic")[#desc]
  ]
  v(5pt)
}

// TITLE
#align(center)[
  #text(size: 13pt, weight: "bold")[
    Annexe — Exemples de Qualité de Données sur un Graphe de Propriété
  ]
  #linebreak()
  #text(size: 9pt, style: "italic", fill: rgb("#555"))[
    Illustrations des critères de la section 2 (Complétude, Conformité, Cohérence, Intégrité, Unicité)
  ]
]
#v(4pt)
#line(length: 100%, stroke: 0.6pt)
#v(8pt)

= 2.1 — Complétude
#dh("2.1.1", "Existence de composantes", [∀ nœud :Order → ∃ au moins un arc ORDERED_BY vers un nœud :Client])
#let Graph-211-1 = graf((
  myn((0, 0), (":Order", "id: C1", "total: 50€"), "vc1", ok-f, ok-s),
  myn((0.5, 1), (":Order", "id: C2", "total: 120€"), "vc2", ok-f, ok-s),
  myn((2, 0), (":Client", "id: U7", "name: \"Dupont\""), "vcl", neu-f, neu-s),
  edge(<vc1>, <vcl>, "->", el[:ORDERED_BY]),
  edge(<vc2>, <vcl>, "->", el[:ORDERED_BY]),
))
#let Graph-211-2 = graf((
  myn((0, 0), (":Order", "id: C1", "total: 50€"), "kc1", err-f, err-s),
  myn((0, 1), (":Order", "id: C2", "total: 120€"), "kc2", ok-f, ok-s),
  myn((2, 1), (":Client", "id: U7", "name: \"Dupont\""), "kcl", neu-f, neu-s),
  edge(<kc2>, <kcl>, "->", el[ORDERED_BY]),
))

#cmp(
  Graph-211-1,
  Graph-211-2,
)

#dh("2.1.2", "Degré des nœuds", [∀ nœud :Author : d⁺(n) ≥ 1  (au moins un arc WRITE sortant)])
#let Graph-212-1 = graf((
  myn((0, 0), (":Author", "name: \"Zola\""), "va1", ok-f, ok-s),
  myn((0, 2), (":Author", "name: \"Hugo\""), "va2", ok-f, ok-s),
  myn((2, 0), (":Book", "title: \"Germinal\""), "vl1", neu-f, neu-s),
  myn((2, 2), (":Book", "title: \"Les Misérables\""), "vl2", neu-f, neu-s),
  edge(<va1>, <vl1>, "->", el[WRITE]),
  edge(<va2>, <vl2>, "->", el[WRITE]),
))

#let Graph-212-2 = graf((
  myn((0, 0), (":Author", "name: \"Zola\""), "ka1", err-f, err-s),
  myn((0, 2), (":Author", "name: \"Hugo\""), "ka2", ok-f, ok-s),
  myn((2, 2), (":Book", "title: \"Les Misérables\""), "kl2", neu-f, neu-s),
  edge(<ka2>, <kl2>, "->", el[WRITE]),
))

#cmp(
  Graph-212-1,
  Graph-212-2,
)

= 2.2 — Conformité
#dh(
  "2.2.1",
  "Format des chaînes de caractère",
  [Regex : ∀ nœud :User, email → match(v, /^[\w.]+\@[\w.]+\.[a-z]{2,}) = Vrai],
)
#let Graph-221-1 = graf((
  myn((0, 0), (":User", "email: \"alice@mail.fr\""), "n1", ok-f, ok-s),
  myn((1.5, 0), (":User", "email: \"bob@corp.com\""), "n2", ok-f, ok-s),
))

#let Graph-221-2 = graf((
  myn((0, 0), (":User", "email: \"alice_mail\""), "n1", err-f, err-s),
  myn((1.5, 0), (":User", "email: \"bob_mail\""), "n2", err-f, err-s),
))

#cmp(
  Graph-221-1,
  Graph-221-2,
)

#dh("2.2.2", "Format des dates", [Format attendu : ISO 8601 — YYYY-MM-DD pour les nœuds :Event])
#let Graph-222-1 = graf((
  myn((0, 0), (":Event", "name: \"Conférence\"", "date: \"2024-06-15\""), "n1", ok-f, ok-s),
  myn((1.5, 0), (":Event", "name: \"Réunion\"", "date: \"2024-11-01\""), "n2", ok-f, ok-s),
))

#let Graph-222-2 = graf((
  myn((0, 0), (":Event", "name: \"Conférence\"", "date: \"15/06/2024\""), "n1", err-f, err-s),
  myn((1.5, 0), (":Event", "name: \"Réunion\"", "date: \"2024-11-01\""), "n2", ok-f, ok-s),
))

#cmp(
  Graph-222-1,
  Graph-222-2,
)

#dh("2.2.3", "Ensemble fini de données", [status des nœuds :Account ∈ {\"Actif\", \"Inactif\", \"Suspendu\"}])
#let Graph-223-1 = graf((
  myn((0, 0), (":Account", "id: A1", "status: \"Actif\""), "n1", ok-f, ok-s),
  myn((1.5, 0), (":Account", "id: A2", "status: \"Suspendu\""), "n2", ok-f, ok-s),
))

#let Graph-223-2 = graf((
  myn((0, 0), (":Account", "id: A1", "status: \"Actif\""), "n1", ok-f, ok-s),
  myn((1.5, 0), (":Account", "id: A2", "status: \"Désactivé\""), "n2", err-f, err-s),
))

#cmp(
  Graph-223-1,
  Graph-223-2,
)

#dh("2.2.4", "Étiquetage Ensembliste", [Contrainte : λ(n) ⊇ {:Person} pour tout nœud portant l'étiquette :Student])
#let Graph-224-1 = graf((
  myn((0, 0), (":Student :Person", "name: \"Léa\""), "n1", ok-f, ok-s),
  myn((1.5, 0), (":Employé :Person", "name: \"Marc\""), "n2", ok-f, ok-s),
))

#let Graph-224-2 = graf((
  myn((0, 0), (":Student", "name: \"Léa\""), "n1", err-f, err-s),
  myn((1.5, 0), (":Student :Person", "name: \"Kim\""), "n2", ok-f, ok-s),
))

#cmp(
  Graph-224-1,
  Graph-224-2,
)

#dh(
  "2.2.5",
  "Étiquetage par Regroupement (Clustering)",
  [Des nœuds avec des tokens similaires devraient avoir des étiquettes similaires],
)
#let Graph-225-1 = graf((
  myn((0, 0), (":City", "name: \"Paris\""), "c1", neu-f, neu-s),
  myn((0, 2), (":City", "name: \"Versailles\""), "c2", neu-f, neu-s),
  myn((2, 0), (":Student", "name: \"Léa\""), "sm1", mg-f, mg-s),
  myn((2, 2), (":Apprentice", "surname: \"Tom\"", "age:18"), "sm2", mg-f, mg-s),
  myn((4, 1), (":University", "name: \"UVSQ\""), "smu", neu-f, neu-s),
  edge(<sm1>, <c1>, "->", el[COMES_FROM]),
  edge(<sm2>, <c2>, "->", el[COMES_FROM]),
  edge(<sm1>, <smu>, "->", el[STUDY_AT]),
  edge(<sm2>, <smu>, "->", el[STUDY_AT]),
  edge(<sm1>, <sm2>, "<->", el[MERGE ?], stroke: (paint: mg-s, dash: "dashed", thickness: 0.8pt)),
))

#let Graph-225-2 = graf((
  myn((2, 0), (":Person", "name: \"Alice\""), "ss1", sp-f, sp-s),
  myn((0, 0), (":Team", "name: \"R&D\""), "st1", neu-f, neu-s),
  myn((3.5, 0), (":Person", "name: \"Bob\""), "ss2", sp-f, sp-s),
  myn((5, 0), (":Product", "ref: \"P42\""), "st2", neu-f, neu-s),
  edge(<ss1>, <st1>, "->", el[MANAGE]),
  edge(<ss2>, <st2>, "->", el[BUY]),
  edge(<ss1>, <ss2>, "<->", el[SPLIT ?], stroke: (paint: sp-s, dash: "dashed", thickness: 0.8pt)),
))

#block(width: 100%, inset: 8pt, fill: white, stroke: (paint: mg-s, thickness: 0.5pt), radius: 3pt)[
  #text(size: 7.5pt, fill: mg-s, weight: "bold")[⊕ Suggestion MERGE]
  #text(size: 7pt, style: "italic")[\ Tokens similaires ("OUT:STUDY_AT:University", "OUT:COMES_FROM:City"),]
  #text(size: 7pt, style: "italic")[\ étiquettes différentes → candidats à unifier]
  #v(5pt)
  #Graph-225-1
]

#block(width: 100%, inset: 8pt, fill: white, stroke: (paint: sp-s, thickness: 0.5pt), radius: 3pt)[
  #text(size: 7.5pt, fill: sp-s, weight: "bold")[⊖ Suggestion SPLIT]
  #text(size: 7pt, style: "italic")[\ Étiquettes identiques (:Person),]
  #text(size: 7pt, style: "italic")[\ tokens très différents → candidats à séparer]
  #v(5pt)

  #Graph-225-2
]

= 2.3 — Cohérence
#dh(
  "2.3.1",
  "Dépendance Fonctionnelle (FD)",
  [FD : (:Adress, codePostal → city) — deux Adresss de même code_postal doivent avoir la même city],
)
#let Graph-231-1 = graf((
  myn((0, 0), (":Adress", "postal_code: 75001", "city: \"Paris\""), "n1", ok-f, ok-s),
  myn((2, 0), (":Adress", "postal_code: 75001", "city: \"Paris\""), "n2", ok-f, ok-s),
))

#let Graph-231-2 = graf((
  myn((0, 0), (":Adress", "postal_code: 75001", "city: \"Paris\""), "n1", ok-f, ok-s),
  myn((2, 0), (":Adress", "postal_code: 75001", "city: \"Marseille\""), "n2", err-f, err-s),
))

#cmp(
  Graph-231-1,
  Graph-231-2,
)

#dh(
  "2.3.2",
  "Dépendance Fonctionnelle Conditionnelle (CFD)",
  [CFD : condition C(o) = (country = \"France\") ∧ (postal_code identiques) → même region],
)
#let Graph-232-1 = graf((
  myn((0, 0), (":Adress", "country: \"FR\"", "postal_code: 75001", "region: \"IDF\""), "n1", ok-f, ok-s),
  myn((2, 0), (":Adress", "country: \"FR\"", "postal_code: 75001", "region: \"IDF\""), "n2", ok-f, ok-s),
))

#let Graph-232-2 = graf((
  myn((0, 0), (":Adress", "country: \"FR\"", "postal_code: 75001", "region: \"IDF\""), "n1", ok-f, ok-s),
  myn((2, 0), (":Adress", "country: \"FR\"", "postal_code: 75001", "region: \"PACA\""), "n2", err-f, err-s),
))

#cmp(
  Graph-232-1,
  Graph-232-2,
)

#dh(
  "2.3.3",
  "GFD — Dépendance sur Graph Pattern",
  [Pattern (:Movie)→[DIRECTED_BY]→(:DIRECTOR) → film.language = réalisateur.nationality],
)
#let Graph-233-1 = graf((
  myn((0, 0), (":Movie", "title: \"Amélie\"", "language: \"FR\""), "n1", ok-f, ok-s),
  myn((2, 0), (":DIRECTOR", "name: \"Jeunet\"", "nationality: \"FR\""), "n2", ok-f, ok-s),
  edge(<n1>, <n2>, "->", el[DIRECTED_BY]),
))

#let Graph-233-2 = graf((
  myn((0, 0), (":Movie", "title: \"Amélie\"", "language: \"FR\""), "n1", err-f, err-s),
  myn((2, 0), (":DIRECTOR", "name: \"Jeunet\"", "nationality: \"EN\""), "n2", err-f, err-s),
  edge(<n1>, <n2>, "->", el[DIRECTED_BY]),
))

#cmp(
  Graph-233-1,
  Graph-233-2,
)

#dh(
  "2.3.4",
  "Validation par requête",
  [dgt = (R, B=Faux) — R : MATCH (n:Product) WHERE n.prix IS NULL → R doit retourner ∅],
)
#let Graph-234-1 = graf((
  myn((0, 0), (":Product", "ref: \"P01\"", "prix: 29.99"), "n1", ok-f, ok-s),
  myn((2, 0), (":Product", "ref: \"P02\"", "prix: 14.50"), "n2", ok-f, ok-s),
))

#let Graph-234-2 = graf((
  myn((0, 0), (":Product", "ref: \"P01\"", "prix: 29.99"), "n1", ok-f, ok-s),
  myn((2, 0), (":Product", "ref: \"P02\""), "n2", err-f, err-s),
))

#cmp(
  Graph-234-1,
  Graph-234-2,
)

= 2.4 — Intégrité
#dh("2.4.1a", "Unicité de propriété", [∀ n₁ ≠ n₂ ∈ :Person : σ(n₁, {id}) = σ(n₂, {id}) ⇒ n₁ = n₂])
#let Graph-241-1 = graf((
  myn((0, 0), (":Person", "id: 1", "name: \"Alice\""), "n1", ok-f, ok-s),
  myn((2, 0), (":Person", "id: 2", "name: \"Bob\""), "n2", ok-f, ok-s),
))

#let Graph-241-2 = graf((
  myn((0, 0), (":Person", "id: 1", "name: \"Alice\""), "n1", err-f, err-s),
  myn((2, 0), (":Person", "id: 1", "name: \"Bob\""), "n2", err-f, err-s),
))

#cmp(
  Graph-241-1,
  Graph-241-2,
)

#dh(
  "2.4.1b",
  "Existence de propriété",
  [∀ n ∈ :Person : NULL ∉ σ(n, {nom})  (la propriété nom doit toujours être définie)],
)
#let Graph-241-3 = graf((
  myn((0, 0), (":Person", "name: \"Alice\"", "age: 30"), "n1", ok-f, ok-s),
))

#let Graph-241-4 = graf((
  myn((0, 0), (":Person", "age: 30"), "n1", err-f, err-s),
))

#cmp(
  Graph-241-3,
  Graph-241-4,
)

#dh("2.4.1c", "Type des valeurs de propriété", [∀ n ∈ :Person : (t ∘ σ)(n, {age}) ⊆ {18, 19, 20, 21, 22, 23, 24, 25}])
#let Graph-241-5 = graf((
  myn((0, 0), (":Person", "name: \"Alice\"", "age: 30"), "n1", ok-f, ok-s),
))

#let Graph-241-6 = graf((
  myn((0, 0), (":Person", "name: \"Bob\"", "age: 17"), "n1", err-f, err-s),
))

#cmp(
  Graph-241-5,
  Graph-241-6,
)

#dh("2.4.2", "Validité des Index", [Index Ⓘ sur email : NULL ∉ i(n) ⊙ σ(n, P) pour tout nœud :User])
#let Graph-242-1 = graf((
  myn((0, 0), (":User", "email: \"a@g.com\"", "name: \"Alice\""), "n1", ok-f, ok-s),
))

#let Graph-242-2 = graf((
  myn((0, 0), (":User", "name: \"Bob\""), "n1", ok-f, ok-s),
))

#cmp(
  Graph-242-1,
  Graph-242-2,
)

#dh(
  "2.4.3",
  "Forme Normale d'un Graphe de Propriété (3NF)",
  [Décomposer pour éliminer les dépendances transitives : id → nameStudent],
)
#let Graph-243-1 = graf((
  myn((0, 0), (":Student", "id: E1", "name: \"Léa\""), "n1", ok-f, ok-s),
  myn((2, 0), (":Registration", "date: 2024-09"), "n2", neu-f, neu-s),
  myn((1, 1), (":Cours", "idLecture: C1", "title: \"BDD\""), "n3", ok-f, ok-s),
  edge(<n1>, <n2>, "->", el[ENROLLED]),
  edge(<n2>, <n3>, "->", el[REFERENCE]),
))

#let Graph-243-2 = graf((
  myn(
    (0, 0),
    (":Registration", "id: E1", "nameStudent: \"Léa\"", "idLecture: C1", "tittleLecture: \"BDD\"", "date: 2024-09"),
    "n1",
    err-f,
    err-s,
  ),
))

#grid(
  columns: (1fr, 1fr),
  column-gutter: 10pt,
  block(width: 100%, inset: 8pt, fill: white, stroke: (paint: ok-s, thickness: 0.5pt), radius: 3pt)[
    #text(size: 7.5pt, fill: ok-s, weight: "bold")[✓ Normalisé (3NF)]
    #text(size: 7pt, style: "italic")[\ Chaque nœud ne contient que ses propres attributs]
    #v(5pt)
    #Graph-243-1
  ],
  block(width: 100%, inset: 8pt, fill: white, stroke: (paint: err-s, thickness: 0.5pt), radius: 3pt)[
    #text(size: 7.5pt, fill: err-s, weight: "bold")[✗ Non normalisé]
    #text(size: 7pt, style: "italic")[\ Dép. transitive : id → nameStudent dans :Registration]
    #v(5pt)
    #Graph-243-2
  ],
)

= 2.5 — Unicité
#dh("2.5.1", "Doublons d'arcs", [e₁ ≠ e₂ sont des doublons ssi ρ(e₁) = ρ(e₂) ∧ λ(e₁) = λ(e₂) ∧ σ(e₁,P) = σ(e₂,P)])
#let Graph-251-1 = graf((
  myn((0, 0), (":Person", "name: \"Alice\""), "n1", ok-f, ok-s),
  myn((2, 0), (":Movie", "title: \"Matrix\""), "n2", ok-f, ok-s),
  edge(<n1>, <n2>, "->", el[AIME]),
))

#let Graph-251-2 = graf((
  myn((0, 0), (":Person", "name: \"Alice\""), "n1", err-f, err-s),
  myn((2, 0), (":Movie", "title: \"Matrix\""), "n2", err-f, err-s),
  edge(<n1>, <n2>, "->", el[AIME], bend: 18deg),
  edge(<n1>, <n2>, "->", el[AIME], bend: -18deg),
))

#cmp(
  Graph-251-1,
  Graph-251-2,
)

#dh("2.5.2", "Doublons de nœuds", [n₁ ≠ n₂ sont des doublons ssi λ(n₁) = λ(n₂) ∧ σ(n₁,P) = σ(n₂,P)])
#let Graph-252-1 = graf((
  myn((0, 0), (":Person", "name: \"Alice\"", "email: \"a@x.fr\""), "n1", ok-f, ok-s),
  myn((2, 0), (":Person", "name: \"Bob\"", "email: \"b@x.fr\""), "n2", ok-f, ok-s),
))

#let Graph-252-2 = graf((
  myn((0, 0), (":Person", "name: \"Alice\"", "email: \"a@x.fr\""), "n1", err-f, err-s),
  myn((2, 0), (":Person", "name: \"Alice\"", "email: \"a@x.fr\""), "n1", err-f, err-s),
))

#cmp(
  Graph-252-1,
  Graph-252-2,
)
