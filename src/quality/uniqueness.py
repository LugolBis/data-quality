from typing import TYPE_CHECKING, LiteralString

from quality.types import RelationshipDuplicate
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
