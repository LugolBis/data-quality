from typing import TYPE_CHECKING, LiteralString

from models.enums import WILDCARD, Entity
from models.utils import build_match, format_label
from quality.types import MultivaluedDuplicate, NodeDuplicate, RelationshipDuplicate
from utils.utils import logger, some

if TYPE_CHECKING:
    from neo4j import Result

    from driver.neo4j_driver import Neo4jSession

_RELS_DUPLICATE_QUERY: LiteralString = (
    "MATCH (n1)-[r1]->(n2), (n1)-[r2]->(n2) "
    "WHERE type(r1) = type(r2) "
    "AND id(r1) < id(r2) "
    "AND properties(r1) = properties(r2) "
    "RETURN type(r1) as Label, COUNT(*) AS Duplicates"
)


def duplicate_relationships(
    session: Neo4jSession,
) -> list[RelationshipDuplicate] | None:
    result: Result = session.run_query(_RELS_DUPLICATE_QUERY)
    records = result.to_eager_result().records

    if len(records) == 0:
        return None
    analysis = []
    for record in records:
        label: str = record.get("Label")
        invalid_pair: int = record.get("Duplicates")

        if some(label) and some(invalid_pair):
            analysis.append(
                RelationshipDuplicate(label, invalid_pair),
            )
        else:
            logger.error(f"Invalid record : {record}")

    if len(analysis) > 0:
        return analysis
    return None


def duplicate_nodes(
    session: Neo4jSession,
    label: str,
    treshold: float,
) -> list[NodeDuplicate] | None:
    if label != WILDCARD:
        match_clause = f"MATCH (n1:{label}), (n2:{label})"
    else:
        match_clause = "MATCH (n1), (n2)"

    nodes_duplicate_query: str = (
        f"{match_clause} "
        "WHERE id(n1) < id(n2) "
        "AND properties(n1) = properties(n2) "
        "OPTIONAL MATCH (n1)-[r1]-() "
        "WITH n1, n2, collect(r1) AS rels1 "
        "OPTIONAL MATCH (n2)-[r2]-() "
        "WITH n1, n2, rels1, collect(r2) AS rels2 "
        "WITH n1, n2, "
        "[r in rels1 | [type(r), properties(r), CASE WHEN startNode(r) = n1 "
        "THEN id(endNode(r)) ELSE id(startNode(r)) END]] AS norm1, "
        "[r in rels2 | [type(r), properties(r), CASE WHEN startNode(r) = n2 "
        "THEN id(endNode(r)) ELSE id(startNode(r)) END]] AS norm2 "
        "WITH n1, n2, norm1, norm2, [r1 IN norm1 WHERE r1 IN norm2] AS shared, "
        "size(norm1) AS size1, size(norm2) AS size2 "
        "WITH n1, n2, size(shared) AS shared_count, "
        "size1 + size2 - 2 * size(shared) AS unique_count "
        "WITH n1, n2, shared_count / (shared_count + unique_count) AS treshold "
        f"WHERE treshold >= {treshold} "
        "RETURN labels(n1) AS Label, elementId(n1) AS n1_id, elementId(n2) AS n2_id "
    )

    result: Result = session.run_query(nodes_duplicate_query)  # ty:ignore[invalid-argument-type]
    records = result.to_eager_result().records

    if len(records) == 0:
        return None
    analysis = []
    for record in records:
        label: list[str] = record.get("Label")
        node_id_x: int = record.get("n1_id")
        node_id_y: int = record.get("n2_id")

        if some(label) and some(node_id_x) and some(node_id_y):
            label: str = format_label(label)
            analysis.append(
                NodeDuplicate(label, node_id_x, node_id_y),
            )
        else:
            logger.error(f"Invalid record : {record}")

    if len(analysis) > 0:
        return analysis
    return None


def duplicate_multivalued(
    session: Neo4jSession,
    entity: Entity,
    label: str,
    properties: set[str],
) -> list[MultivaluedDuplicate] | None:
    query: str = (
        f"{build_match(entity, label)} "
        f"UNWIND {list(properties)} AS prop "
        "WITH prop, size(e[prop]) AS values_count, "
        "size(collect(DISTINCT e[prop])) AS set_count "
        "WHERE values_count <> set_count "
        "RETURN prop AS property, COUNT(*) AS invalid"
    )

    result: Result = session.run_query(query)  # ty:ignore[invalid-argument-type]
    records = result.to_eager_result().records

    if len(records) == 0:
        return None
    analysis = []
    for record in records:
        property_: str = record.get("property")
        invalid: int = record.get("invalid")

        if some(label) and some(invalid):
            analysis.append(
                MultivaluedDuplicate(entity, label, property_, invalid),
            )
        else:
            logger.error(f"Invalid record : {record}")

    if len(analysis) > 0:
        return analysis
    return None
