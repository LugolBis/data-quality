import os
from collections import defaultdict
from difflib import SequenceMatcher
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from neo4j import Result

from driver.neo4j import Neo4jSession
from utils import some


def verifier_coherence_proprietes(session: Neo4jSession) -> None:
    """
    [Schema Integrity] Analyze if nodes with the same label combination
    share the exact same set of property keys.

    :param self: The object itself.
    """
    print("\n1. Analyse de l'intégrité du schéma (Schema Integrity)...")

    requete = """
    MATCH (n)
    WITH labels(n) AS Labels, keys(n) AS PropertyKeys
    RETURN Labels, PropertyKeys, count(*) AS Nombre
    """

    resultat = session.run_query(requete)
    donnees = [record.data() for record in resultat]

    if not donnees:
        print("Aucune donnée trouvée.")
        return

    df = pd.DataFrame(donnees)
    df["Label_Combo"] = df["Labels"].apply(lambda x: tuple(sorted(x)))
    df["Property_Keys_Set"] = df["PropertyKeys"].apply(lambda x: tuple(sorted(x)))
    labels_uniques = df["Label_Combo"].unique()

    print("\nRAPPORT DE PROPRIÉTÉS (SCHEMA VIOLATION):")
    print("=" * 60)

    for label_tuple in labels_uniques:
        groupe = df[df["Label_Combo"] == label_tuple]
        total_noeuds = groupe["Nombre"].sum()
        label_str = ":" + ":".join(label_tuple)

        print(f"\n{label_str} (Total: {total_noeuds})")

        groupe = groupe.sort_values(by="Nombre", ascending=False)

        for index, row in groupe.iterrows():
            props = list(row["Property_Keys_Set"])
            count = row["Nombre"]
            percent = (count / total_noeuds) * 100
            print(f"   -> {props} : {count} ({percent:.1f}%)")

    print("\n" + "=" * 60)


def detecter_doublons(session: Neo4jSession, seuil_similarite: float = 0.8) -> None:
    """
    [Duplicate Detection] Scan all nodes to find potential duplicates based
    on string property similarity using SequenceMatcher.
    :param self: The object itself.
    :param seuil_similarite: Similarity threshold between 0 and 1.
    :type seuil_similarite: float
    """
    print(f"\n2. Recherche de doublons (Similarity >= {seuil_similarite})...")

    requete = """
    MATCH (n)
    RETURN elementId(n) as ID, labels(n) as Labels, properties(n) as Props
    """

    resultat: Result = session.run_query(requete)
    nodes = [record.data() for record in resultat]

    detectes = []

    groups = defaultdict(list)
    for node in nodes:
        label_key = tuple(sorted(node["Labels"]))
        groups[label_key].append(node)

    print(
        f"   -> {len(nodes)} noeuds chargés, répartis en {len(groups)} groupes de labels."
    )

    for label_key, group_nodes in groups.items():
        label_str = ":" + ":".join(label_key)
        n_count = len(group_nodes)

        if n_count < 2:
            continue

        for i in range(n_count):
            for j in range(i + 1, n_count):
                n1 = group_nodes[i]
                n2 = group_nodes[j]

                props1 = n1["Props"]
                props2 = n2["Props"]

                common_keys = set(props1.keys()) & set(props2.keys())

                for key in common_keys:
                    val1 = props1[key]
                    val2 = props2[key]

                    if isinstance(val1, str) and isinstance(val2, str):
                        if len(val1) < 3 or len(val2) < 3:
                            continue
                        similarity = SequenceMatcher(None, val1, val2).ratio()

                        if similarity >= seuil_similarite:
                            detectes.append(
                                {
                                    "Labels": label_str,
                                    "Property": key,
                                    "Value_1": val1,
                                    "Value_2": val2,
                                    "Similarity": f"{similarity:.2f}",
                                }
                            )

    if not detectes:
        print("\nAucun doublon détecté (No duplicates found).")
    else:
        print(f"\nDOUBLONS POTENTIELS DÉTECTÉS (SIMILARITY >= {seuil_similarite}):")
        df_doublons = pd.DataFrame(detectes)
        df_doublons = df_doublons.sort_values(by="Similarity", ascending=False)

        for idx, row in df_doublons.iterrows():
            print(f"   [{row['Similarity']}] {row['Labels']} sur '{row['Property']}':")
            print(f'       "{row["Value_1"]}"  <-->  "{row["Value_2"]}"')


if __name__ == "__main__":
    load_dotenv()

    uri: Optional[str] = os.environ.get("URI")
    db_user: Optional[str] = os.environ.get("DB_USER")
    db_password: Optional[str] = os.environ.get("DB_PW")
    db_name: Optional[str] = os.environ.get("DB_NAME")

    if some(uri) and some(db_user) and some(db_password) and some(db_name):
        with Neo4jSession(uri, db_user, db_password, db_name) as session:
            verifier_coherence_proprietes(session)
            detecter_doublons(session, seuil_similarite=0.6)
