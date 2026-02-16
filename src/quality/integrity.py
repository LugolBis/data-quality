from collections import defaultdict
from difflib import SequenceMatcher
from typing import Any, Optional

import pandas as pd
from neo4j import Result

from driver.neo4j_driver import Neo4jSession
from quality.enums import EntityType
from quality.types import LabelStats, NodeProperties, SchemaViolation, TextSimilarity
from utils.utils import logger, some


def check_properties_consistency(session: Neo4jSession) -> Optional[list[LabelStats]]:
    """
    [Schema Integrity] Analyze if nodes with the same label combination
    share the exact same set of property keys.

    :param self: The object itself.
    """
    # print("\n1. Analyse de l'intégrité du schéma (Schema Integrity)...")

    query: str = (
        "MATCH (n) "
        "WITH labels(n) AS Labels, keys(n) AS PropertyKeys "
        "RETURN Labels, PropertyKeys, count(*) AS Nombre "
    )

    result: Result = session.run_query(query)
    df: pd.DataFrame = result.to_df()

    try:
        df["Label_Combo"] = df["Labels"].apply(lambda x: tuple(sorted(x)))
        df["Property_Keys_Set"] = df["PropertyKeys"].apply(lambda x: tuple(sorted(x)))
        labels_uniques = df["Label_Combo"].unique()
    except Exception as error:
        logger.error(error)
        return None

    # print("\nRAPPORT DE PROPRIÉTÉS (SCHEMA VIOLATION):")
    # print("=" * 60)

    analysis: list[LabelStats] = []

    for label_tuple in labels_uniques:
        groupe: pd.DataFrame = df[df["Label_Combo"] == label_tuple]
        total_nodes: int = groupe["Nombre"].sum()
        label_str: str = "&".join(label_tuple)

        properties: list[NodeProperties] = []

        # print(f"\n{label_str} (Total: {total_nodes})")

        groupe_sorted: pd.DataFrame = groupe.sort_values(by="Nombre", ascending=False)

        for index, row in groupe_sorted.iterrows():
            props: list[str] = list(row["Property_Keys_Set"])
            count: int = int(row["Nombre"])
            percent: float = float((count / total_nodes) * 100)

            properties.append(NodeProperties(props, count, percent))
            # print(f"   -> {props} : {count} ({percent:.1f}%)")

        analysis.append(
            LabelStats(label=label_str, count=total_nodes, properties=properties)
        )

    # print("\n" + "=" * 60)
    return analysis

def check_relationships_consistency(session: Neo4jSession) -> Optional[list[LabelStats]]:
    """
    [Relationship Schema Integrity]
    Analyze if relationships of the same TYPE share the exact same set of property keys.

    :param self: The object itself.
    """
    query: str = (
        "MATCH ()-[r]->() "
        "WITH type(r) AS RelType, keys(r) AS PropertyKeys "
        "RETURN RelType, PropertyKeys, count(*) AS Nombre "
    )

    result: Result = session.run_query(query)
    df: pd.DataFrame = result.to_df()

    try:
        df["Property_Keys_Set"] = df["PropertyKeys"].apply(lambda x: tuple(sorted(x)))
        types_unique = df["RelType"].unique()
    except Exception as error:
        logger.error(error)
        return None

    analysis: list[LabelStats] = []

    for r_type in types_unique:
        groupe: pd.DataFrame = df[df["RelType"] == r_type]
        total: int = groupe["Nombre"].sum()
        
        properties: list[NodeProperties] = []
        groupe_sorted = groupe.sort_values(by="Nombre", ascending=False)

        for index, row in groupe_sorted.iterrows():
            props: list[str] = list(row["Property_Keys_Set"])
            count: int = int(row["Nombre"])
            percent: float = float((count / total) * 100)
            
            properties.append(NodeProperties(props, count, percent))

        analysis.append(
            LabelStats(label=r_type, count=total, properties=properties)
        )

    return analysis

def detecter_doublons(
    session: Neo4jSession, seuil_similarite: float = 0.8
) -> Optional[list[TextSimilarity]]:
    """
    [Duplicate Detection] Scan all nodes to find potential duplicates based
    on string property similarity using SequenceMatcher.
    :param self: The object itself.
    :param seuil_similarite: Similarity threshold between 0 and 1.
    :type seuil_similarite: float
    """
    # print(f"\n2. Recherche de doublons (Similarity >= {seuil_similarite})...")

    query = (
        "MATCH (n) "
        "RETURN elementId(n) as ID, labels(n) as Labels, properties(n) as Props "
    )

    result: Result = session.run_query(query)
    nodes: list[dict[str, Any]] = [record.data() for record in result]

    detected: list[TextSimilarity] = []

    groups = defaultdict(list)
    for node in nodes:
        label_key = tuple(sorted(node["Labels"]))
        groups[label_key].append(node)

    # print(f"   -> {len(nodes)} noeuds chargés, répartis en {len(groups)} groupes de labels.")

    for label_key, group_nodes in groups.items():
        label_str = "&".join(label_key)
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
                            detected.append(
                                TextSimilarity(
                                    label=label_str,
                                    similarity=similarity,
                                    property=key,
                                    first_value=val1,
                                    second_value=val2,
                                )
                            )

    if len(detected) == 0:
        # print("\nAucun doublon détecté (No duplicates found).")
        return None
    else:
        """
        print(f"\nDOUBLONS POTENTIELS DÉTECTÉS (SIMILARITY >= {seuil_similarite}):")
        df_doublons = pd.DataFrame(detected)
        df_doublons = df_doublons.sort_values(by="Similarity", ascending=False)

        for idx, row in df_doublons.iterrows():
            print(f"   [{row['Similarity']}] {row['Labels']} sur '{row['Property']}':")
            print(f'       "{row["Value_1"]}"  <-->  "{row["Value_2"]}"')
        """

        return sorted(detected, key=lambda x: x.similarity, reverse=True)


def check_schema_violation(session: Neo4jSession) -> Optional[list[SchemaViolation]]:
    query: str = (
        "SHOW INDEXES "
        "YIELD entityType, labelsOrTypes, properties "
        "WHERE labelsOrTypes IS NOT NULL and properties IS NOT NULL "
        "RETURN * "
    )

    result: Result = session.run_query(query)
    df: pd.DataFrame = result.to_df()

    df["labelsOrTypes"] = df["labelsOrTypes"].apply(lambda x: "&".join(x))
    df_exploded: pd.DataFrame = df.explode("properties")

    df_grouped: pd.DataFrame = pd.DataFrame(
        df_exploded.groupby(["entityType", "labelsOrTypes"], as_index=False)[
            "properties"
        ].agg(set)
    )

    violations: list[SchemaViolation] = []
    for idx, row in df_grouped.iterrows():
        entity_type: EntityType = EntityType(row["entityType"])
        labels_str: str = row["labelsOrTypes"]
        properties: list[str] = list(row["properties"])
        sub_query: str

        match entity_type:
            case EntityType.NODE:
                sub_query = (
                    f"WITH {properties} AS requiredProps "
                    f"MATCH (n: {labels_str}) "
                    "RETURN COUNT(n) as count, "
                    "COUNT(CASE WHEN any(p IN requiredProps WHERE n[p] IS NULL) THEN 1 END) AS invalid "
                )
            case EntityType.RELATIONSHIP:
                sub_query = (
                    f"WITH {properties} AS requiredProps "
                    f"MATCH ()-[r: {labels_str}]->() "
                    "RETURN COUNT(r) as count, "
                    "COUNT(CASE WHEN any(p IN requiredProps WHERE r[p] IS NULL) THEN 1 END) AS invalid "
                )
            case default:
                logger.error(f"Unknown <EnityType> : {default}")
                continue

        result_label: Result = session.run_query(sub_query)  # type: ignore
        first_row = result_label.single()
        if some(first_row):
            invalid: int = first_row["invalid"]
            count: int = first_row["count"]

            if invalid > 0:
                percent: float = round(float((invalid / count) * 100), 2)
                violations.append(
                    SchemaViolation(
                        entity=entity_type,
                        label=labels_str,
                        count=count,
                        percent=percent,
                    )
                )

    if len(violations) > 0:
        return violations
    else:
        return None
