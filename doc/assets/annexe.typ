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
    #text(fill: ok-s, weight: "bold")[✓ #ok-txt]
    #v(5pt)
    #ok
  ],
  block(width: 100%, inset: 8pt, fill: white, stroke: (paint: err-s, thickness: 0.5pt), radius: 3pt)[
    #text(fill: err-s, weight: "bold")[✗ #err-txt]
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

// Definition figure header
#let figh(title, desc, display_desc: true) = {
  v(5pt)
  if display_desc {
    desc
    linebreak()
  }
  text(weight: "bold")[#title]
  v(40pt)
}

#let fig-wrap(body) = figure(
  kind: "custom-fig",
  supplement: "Figure",
  caption: none,
  body,
)

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

#let Example-211 = [$(G_p, O, L_O) = (({:"Order"})-[{:"ORDERED_BY"}:1]->({:"Client"}), {N}, {"Order"})$]

#let Graph-211-1 = graf((
  myn((0, 0), (":Order", "id: C1", "total: 50€"), "vc1", ok-f, ok-s),
  myn((0.5, 1), (":Order", "id: C2", "total: 120€"), "vc2", ok-f, ok-s),
  myn((2, 0), (":Client", "id: U7", "name: \"Dupont\""), "vcl", neu-f, neu-s),
  edge(<vc1>, <vcl>, "-|>", el[:ORDERED_BY]),
  edge(<vc2>, <vcl>, "-|>", el[:ORDERED_BY]),
))
#let Graph-211-2 = graf((
  myn((0, 0), (":Order", "id: C1", "total: 50€"), "kc1", err-f, err-s),
  myn((0, 1), (":Order", "id: C2", "total: 120€"), "kc2", ok-f, ok-s),
  myn((2, 1), (":Client", "id: U7", "name: \"Dupont\""), "kcl", neu-f, neu-s),
  edge(<kc2>, <kcl>, "-|>", el[ORDERED_BY]),
))

#let Example-212 = [$(L_O, D_s, D_e) = ({"Author"}, {1, 2, 3}, {0})$]

#let Graph-212-1 = graf((
  myn((0, 0), (":Author", "name: \"Zola\""), "va1", ok-f, ok-s),
  myn((0, 2), (":Author", "name: \"Hugo\""), "va2", ok-f, ok-s),
  myn((2, 0), (":Book", "title: \"Germinal\""), "vl1", neu-f, neu-s),
  myn((2, 2), (":Book", "title: \"Les Misérables\""), "vl2", neu-f, neu-s),
  edge(<va1>, <vl1>, "-|>", el[WRITE]),
  edge(<va2>, <vl2>, "-|>", el[WRITE]),
))

#let Graph-212-2 = graf((
  myn((0, 0), (":Author", "name: \"Zola\""), "ka1", err-f, err-s),
  myn((0, 2), (":Author", "name: \"Hugo\""), "ka2", ok-f, ok-s),
  myn((2, 2), (":Book", "title: \"Les Misérables\""), "kl2", neu-f, neu-s),
  edge(<ka2>, <kl2>, "-|>", el[WRITE]),
))

#let Example-221 = [$(O, L_O, X, "Regex") = (N, {"User"}, {"email"}, "\"/^[\w.]+\@[\w.]+\.[a-z]{2,}\"")$]

#let Graph-221-1 = graf((
  myn((0, 0), (":User", "email: \"alice@mail.fr\""), "n1", ok-f, ok-s),
  myn((1.5, 0), (":User", "email: \"bob@corp.com\""), "n2", ok-f, ok-s),
))

#let Graph-221-2 = graf((
  myn((0, 0), (":User", "email: \"alice_mail\""), "n1", err-f, err-s),
  myn((1.5, 0), (":User", "email: \"bob_mail\""), "n2", err-f, err-s),
))

#let Example-222 = [$(O, L_O, X, "Date"_"fmt") = (N, {"Event"}, {"date"}, "\"YYYY-MM-DD\"")$]

#let Graph-222-1 = graf((
  myn((0, 0), (":Event", "name: \"Conférence\"", "date: \"2024-06-15\""), "n1", ok-f, ok-s),
  myn((1.5, 0), (":Event", "name: \"Réunion\"", "date: \"2024-11-01\""), "n2", ok-f, ok-s),
))

#let Graph-222-2 = graf((
  myn((0, 0), (":Event", "name: \"Conférence\"", "date: \"15/06/2024\""), "n1", err-f, err-s),
  myn((1.5, 0), (":Event", "name: \"Réunion\"", "date: \"2024-11-01\""), "n2", ok-f, ok-s),
))

#let Example-223 = [$(O, L_O, X, I) = (N, {"Account"}, {"status"}, {"On", "Off", "Maintenance"})$]

#let Graph-223-1 = graf((
  myn((0, 0), (":Account", "id: A1", "status: \"On\""), "n1", ok-f, ok-s),
  myn((1.5, 0), (":Account", "id: A2", "status: \"Maintenance\""), "n2", ok-f, ok-s),
))

#let Graph-223-2 = graf((
  myn((0, 0), (":Account", "id: A1", "status: \"On\""), "n1", ok-f, ok-s),
  myn((1.5, 0), (":Account", "id: A2", "status: \"Restart\""), "n2", err-f, err-s),
))

#let Example-224 = [$(O, L_X, L_Y, "Op"_"ens") = (N, {"Student"}, {"Person"}, subset)$]

#let Graph-224-1 = graf((
  myn((0, 0), (":Student :Person", "name: \"Léa\""), "n1", ok-f, ok-s),
  myn((1.5, 0), (":Employé", "name: \"Marc\""), "n2", ok-f, ok-s),
))

#let Graph-224-2 = graf((
  myn((0, 0), (":Student", "name: \"Léa\""), "n1", err-f, err-s),
  myn((1.5, 0), (":Student :Person", "name: \"Kim\""), "n2", ok-f, ok-s),
))

#let Graph-225-1 = graf((
  myn((0, 0), (":City", "name: \"Paris\""), "c1", neu-f, neu-s),
  myn((0, 2), (":City", "name: \"Versailles\""), "c2", neu-f, neu-s),
  myn((2, 0), (":Student", "name: \"Léa\""), "sm1", mg-f, mg-s),
  myn((2, 2), (":Apprentice", "surname: \"Tom\"", "age:18"), "sm2", mg-f, mg-s),
  myn((4, 1), (":University", "name: \"UVSQ\""), "smu", neu-f, neu-s),
  edge(<sm1>, <c1>, "-|>", el[COMES_FROM]),
  edge(<sm2>, <c2>, "-|>", el[COMES_FROM]),
  edge(<sm1>, <smu>, "-|>", el[STUDY_AT]),
  edge(<sm2>, <smu>, "-|>", el[STUDY_AT]),
  edge(<sm1>, <sm2>, "<->", el[MERGE ?], stroke: (paint: mg-s, dash: "dashed", thickness: 0.8pt)),
))

#let Graph-225-2 = graf((
  myn((2, 0), (":Person", "name: \"Alice\""), "ss1", sp-f, sp-s),
  myn((0, 0), (":Team", "name: \"R&D\""), "st1", neu-f, neu-s),
  myn((3.5, 0), (":Person", "name: \"Bob\""), "ss2", sp-f, sp-s),
  myn((5, 0), (":Product", "ref: \"P42\""), "st2", neu-f, neu-s),
  edge(<ss1>, <st1>, "-|>", el[MANAGE]),
  edge(<ss2>, <st2>, "-|>", el[BUY]),
  edge(<ss1>, <ss2>, "<->", el[SPLIT ?], stroke: (paint: sp-s, dash: "dashed", thickness: 0.8pt)),
))

#let Example-231 = [$(O, L_O, X -> Y) = (N, {"Adress"}, {"postal_code"} -> {"city"})$]

#let Graph-231-1 = graf((
  myn((0, 0), (":Adress", "postal_code: 75001", "city: \"Paris\""), "n1", ok-f, ok-s),
  myn((2, 0), (":Adress", "postal_code: 75001", "city: \"Paris\""), "n2", ok-f, ok-s),
))

#let Graph-231-2 = graf((
  myn((0, 0), (":Adress", "postal_code: 75001", "city: \"Paris\""), "n1", ok-f, ok-s),
  myn((2, 0), (":Adress", "postal_code: 75001", "city: \"Marseille\""), "n2", err-f, err-s),
))

#let Example-232 = [$(O, L_O, C, X -> Y) = (N, {"Adress"}, ({"country"}, "\"FR\"", =, emptyset), {"postal_code"} -> {"city"})$]

#let Graph-232-1 = graf((
  myn((0, 0), (":Adress", "country: \"FR\"", "postal_code: 75001", "region: \"IDF\""), "n1", ok-f, ok-s),
  myn((1, 0), (":Adress", "country: \"FR\"", "postal_code: 75001", "region: \"IDF\""), "n2", ok-f, ok-s),
))

#let Graph-232-2 = graf((
  myn((0, 0), (":Adress", "country: \"FR\"", "postal_code: 75001", "region: \"IDF\""), "n1", ok-f, ok-s),
  myn((1, 0), (":Adress", "country: \"FR\"", "postal_code: 75001", "region: \"PACA\""), "n2", err-f, err-s),
))

#let Example-233 = [$(G_p, O, L_O, X -> Y) = (({:"Movie"})-[{:"DIRECTED_BY"}:1]->({:"Director"}), {N}, {"language"} -> {"VO"})$]

#let Graph-233-1 = graf((
  myn((0, 0), (":Movie", "title: \"Amélie\"", "language: \"FR\"", "VO: \"FR\""), "n1", ok-f, ok-s),
  myn((2, 0), (":Director", "name: \"Jeunet\""), "n2", neu-f, neu-s),
  edge(<n1>, <n2>, "-|>", el[DIRECTED_BY]),
))

#let Graph-233-2 = graf((
  myn((0, 0), (":Movie", "title: \"Amélie\"", "language: \"FR\"", "VO: \"EN\""), "n1", err-f, err-s),
  myn((2, 0), (":Director", "name: \"Jeunet\""), "n2", err-f, err-s),
  edge(<n1>, <n2>, "-|>", el[DIRECTED_BY]),
))

#let Example-234 = [$(R, B) = ("\"MATCH (n:Product) WHERE n.prix IS NULL\"", "False")$]

#let Graph-234-1 = graf((
  myn((0, 0), (":Product", "ref: \"P01\"", "prix: 29.99"), "n1", ok-f, ok-s),
  myn((2, 0), (":Product", "ref: \"P02\"", "prix: 14.50"), "n2", ok-f, ok-s),
))

#let Graph-234-2 = graf((
  myn((0, 0), (":Product", "ref: \"P01\"", "prix: 29.99"), "n1", ok-f, ok-s),
  myn((2, 0), (":Product", "ref: \"P02\""), "n2", err-f, err-s),
))

#let Example-241a = [$(O, L_O, X) = (N, {"Person"}, {"id"})$]

#let Graph-241-1 = graf((
  myn((0, 0), (":Person", "id: 1", "name: \"Alice\""), "n1", ok-f, ok-s),
  myn((2, 0), (":Person", "id: 2", "name: \"Bob\""), "n2", ok-f, ok-s),
))

#let Graph-241-2 = graf((
  myn((0, 0), (":Person", "id: 1", "name: \"Alice\""), "n1", err-f, err-s),
  myn((2, 0), (":Person", "id: 1", "name: \"Bob\""), "n2", err-f, err-s),
))

#let Example-241b = [$(O, L_O, X) = (N, {"Person"}, {"name"})$]

#let Graph-241-3 = graf((
  myn((0, 0), (":Person", "name: \"Alice\"", "age: 30"), "n1", ok-f, ok-s),
))

#let Graph-241-4 = graf((
  myn((0, 0), (":Person", "age: 30"), "n1", err-f, err-s),
))

#let Example-241c = [$(O, L_O, X, Y) = (N, {"Person"}, {"age"}, {"Integer"})$]

#let Graph-241-5 = graf((
  myn((0, 0), (":Person", "name: \"Alice\"", "age: 30"), "n1", ok-f, ok-s),
))

#let Graph-241-6 = graf((
  myn((0, 0), (":Person", "name: \"Bob\"", "age: 17"), "n1", err-f, err-s),
))

#let Example-242 = [$(O, L_O, "Index", X) = (N, {"User"}, {"email"}, {"email"})$]

#let Graph-242-1 = graf((
  myn((0, 0), (":User", "email: \"a@g.com\"", "name: \"Alice\""), "n1", ok-f, ok-s),
))

#let Graph-242-2 = graf((
  myn((0, 0), (":User", "name: \"Bob\""), "n1", err-f, err-s),
))

#let Graph-243-1 = graf((
  myn((0, 1), (":Person", "name: \"Neo\""), "n1", neu-f, neu-s),
  myn((1, 3), ([:Event\ :Confimed],), "n3", ok-f, ok-s),
  myn((1, 0), (":Event",), "n2", ok-f, ok-s),
  myn((3, 3), (":Evt_Comp", "company: \"Cactus\"", "venue: \"Vault\"", "date: 13/07"), "n33", ok-f, ok-s),
  myn((3, 2), (":Evt_Detail", "name: \"No Socks\"", "venue: \"Vault\"", "date: 13/07"), "n32", ok-f, ok-s),
  myn((1, 1), (":Evt_Mgt", "name: \"No Socks\"", "company: \"Cactus\""), "n231", ok-f, ok-s),
  myn((3, 1), (":Evt_Detail", "name: \"No Socks\"", "venue: \"Vault\"", "date: 06/01"), "n22", ok-f, ok-s),
  myn((3, 0), (":Evt_Comp", "company: \"Cactus\"", "venue: \"Vault\"", "date: 06/01"), "n23", ok-f, ok-s),
  edge(<n1>, <n2>, "-|>", el[ATTENDS]),
  edge(<n1>, <n3>, "-|>", el[ATTENDS]),
  edge(<n23>, <n2>, "-|>", el[_l_]),
  edge(<n22>, <n2>, "-|>", el[_l_]),
  edge(<n231>, <n2>, "-|>", el[_l_]),
  edge(<n231>, <n3>, "-|>", el[_l_]),
  edge(<n32>, <n3>, "-|>", el[_l_]),
  edge(<n33>, <n3>, "-|>", el[_l_]),
))

#let Graph-243-2 = graf((
  myn((3, 0), (":Person", "name: \"Neo\""), "n1", neu-f, neu-s),
  myn(
    (0, 0),
    (":Event", "name: \"No Socks\"", "company: \"Cactus\"", "venue: \"Vault\"", "date: 06/01"),
    "n2",
    err-f,
    err-s,
  ),
  myn(
    (6, 0),
    (":Event:Confirmed", "name: \"No Socks\"", "company: \"Cactus\"", "venue: \"Vault\"", "date: 13/07"),
    "n3",
    err-f,
    err-s,
  ),
  edge(<n1>, <n2>, "-|>", el[ATTENDS]),
  edge(<n1>, <n3>, "-|>", el[ATTENDS]),
))

#let Graph-251-1 = graf((
  myn((0, 0), (":Person", "name: \"Alice\""), "n1", ok-f, ok-s),
  myn((2, 0), (":Movie", "title: \"Matrix\""), "n2", ok-f, ok-s),
  edge(<n1>, <n2>, "-|>", el[AIME]),
))

#let Graph-251-2 = graf((
  myn((0, 0), (":Person", "name: \"Alice\""), "n1", err-f, err-s),
  myn((2, 0), (":Movie", "title: \"Matrix\""), "n2", err-f, err-s),
  edge(<n1>, <n2>, "-|>", el[AIME], bend: 18deg),
  edge(<n1>, <n2>, "-|>", el[AIME], bend: -18deg),
))

#let Graph-252-1 = graf((
  myn((0, 0), (":Person", "name: \"Alice\"", "email: \"a@x.fr\""), "n1", ok-f, ok-s),
  myn((2, 0), (":Person", "name: \"Bob\"", "email: \"b@x.fr\""), "n2", ok-f, ok-s),
))

#let Graph-252-2 = graf((
  myn((0, 0), (":Person", "name: \"Alice\"", "email: \"a@x.fr\""), "n1", err-f, err-s),
  myn((2, 0), (":Person", "name: \"Alice\"", "email: \"a@x.fr\""), "n1", err-f, err-s),
))

#let Merge_A = image("img/fig_merge_a.png")
#let Merge_B = image("img/fig_merge_b.png", height: 30%)
#let Merge_C = image("img/fig_merge_c.png", height: 30%)

#let Split_Img = image("img/fig_split.png")
