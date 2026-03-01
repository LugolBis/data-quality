from collections import defaultdict
from difflib import SequenceMatcher
from typing import TYPE_CHECKING, Any

from quality.enums import Entity
from quality.types import EntityProperties, EntityStats, TextSimilarity
from quality.utils import _format_label
from utils.utils import logger

if TYPE_CHECKING:
    import pandas as pd
    from neo4j import Result

    from driver.neo4j_driver import Neo4jSession


def distr_nodes_properties(session: Neo4jSession) -> list[EntityStats] | None:
    """
    [Schema Integrity] Analyze if nodes with the same label combination
    share the exact same set of property keys.

    :param self: The object itself.
    """

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

    analysis: list[EntityStats] = []

    for label_tuple in labels_uniques:
        groupe: pd.DataFrame = df[df["Label_Combo"] == label_tuple]
        total_nodes: int = groupe["Nombre"].sum()
        label_str: str = _format_label(label_tuple)

        properties: list[EntityProperties] = []

        groupe_sorted: pd.DataFrame = groupe.sort_values(by="Nombre", ascending=False)

        for _index, row in groupe_sorted.iterrows():
            props: list[str] = list(row["Property_Keys_Set"])
            count: int = int(row["Nombre"])
            percent: float = float((count / total_nodes) * 100)

            properties.append(EntityProperties(props, count, percent))

        analysis.append(
            EntityStats(
                entity=Entity.NODE,
                label=label_str,
                count=total_nodes,
                properties=properties,
            ),
        )

    return analysis


def distr_relationships_properties(
    session: Neo4jSession,
) -> list[EntityStats] | None:
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

    analysis: list[EntityStats] = []

    for r_type in types_unique:
        groupe: pd.DataFrame = df[df["RelType"] == r_type]
        total: int = groupe["Nombre"].sum()

        properties: list[EntityProperties] = []
        groupe_sorted = groupe.sort_values(by="Nombre", ascending=False)

        for _index, row in groupe_sorted.iterrows():
            props: list[str] = list(row["Property_Keys_Set"])
            count: int = int(row["Nombre"])
            percent: float = float((count / total) * 100)

            properties.append(EntityProperties(props, count, percent))

        analysis.append(
            EntityStats(
                entity=Entity.RELATIONSHIP,
                label=r_type,
                count=total,
                properties=properties,
            ),
        )

    return analysis


def detecter_doublons_node(
    session: Neo4jSession,
    seuil_similarite: float = 0.8,
) -> list[TextSimilarity] | None:
    """
    [Duplicate Detection] Scan all nodes to find potential duplicates based
    on string property similarity using SequenceMatcher.
    :param self: The object itself.
    :param seuil_similarite: Similarity threshold between 0 and 1.
    :type seuil_similarite: float
    """

    query = (
        "MATCH (n) "
        "RETURN elementId(n) as ID, labels(n) as Labels, properties(n) as Props "
    )

    result: Result = session.run_query(query)
    nodes: list[dict[str, Any]] = [record.data() for record in result]

    detected: list[TextSimilarity] = []

    groups = defaultdict(list)
    for node in nodes:
        label_str = _format_label(node["Labels"])
        groups[label_str].append(node)

    for label_str, group_nodes in groups.items():
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

                        if val1 == val2:
                            continue

                        similarity = SequenceMatcher(None, val1, val2).ratio()

                        if similarity >= seuil_similarite:
                            detected.append(
                                TextSimilarity(
                                    entity=Entity.NODE,
                                    label=label_str,
                                    similarity=similarity,
                                    property=key,
                                    first_value=val1,
                                    second_value=val2,
                                ),
                            )

    if len(detected) == 0:
        return None

    return sorted(detected, key=lambda x: x.similarity, reverse=True)


def detecter_doublons_relationships(
    session: Neo4jSession,
    seuil_similarite: float = 0.8,
) -> list[TextSimilarity] | None:
    """
    [Relationship Duplicate Detection]
    Scan all relationships to find potential duplicates based
    on string property similarity using SequenceMatcher.
    :param session: The Neo4j session wrapper.
    :param seuil_similarite: Similarity threshold between 0 and 1.
    """

    query = (
        "MATCH ()-[r]->() "
        "RETURN elementId(r) as ID, type(r) as Type, properties(r) as Props "
    )

    result: Result = session.run_query(query)
    rels: list[dict[str, Any]] = [record.data() for record in result]

    detected: list[TextSimilarity] = []

    groups = defaultdict(list)
    for r in rels:
        type_key = r["Type"]
        groups[type_key].append(r)

    for r_type, group_rels in groups.items():
        n_count = len(group_rels)

        if n_count < 2:
            continue

        for i in range(n_count):
            for j in range(i + 1, n_count):
                r1 = group_rels[i]
                r2 = group_rels[j]

                props1 = r1["Props"]
                props2 = r2["Props"]

                common_keys = set(props1.keys()) & set(props2.keys())

                for key in common_keys:
                    val1 = props1[key]
                    val2 = props2[key]

                    if isinstance(val1, str) and isinstance(val2, str):
                        if len(val1) < 3 or len(val2) < 3:
                            continue

                        if val1 == val2:
                            continue

                        similarity = SequenceMatcher(None, val1, val2).ratio()

                        if similarity >= seuil_similarite:
                            detected.append(
                                TextSimilarity(
                                    entity=Entity.RELATIONSHIP,
                                    label=r_type,
                                    similarity=similarity,
                                    property=key,
                                    first_value=val1,
                                    second_value=val2,
                                ),
                            )

    if len(detected) == 0:
        return None
    return sorted(detected, key=lambda x: x.similarity, reverse=True)
