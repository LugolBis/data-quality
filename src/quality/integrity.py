from collections import defaultdict
from difflib import SequenceMatcher
from typing import TYPE_CHECKING, Any

from models.enums import Entity
from models.utils import format_label
from quality.types import TextSimilarity

if TYPE_CHECKING:
    from neo4j import Result

    from driver.neo4j_driver import Neo4jSession


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
        label_str = format_label(node["Labels"])
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
