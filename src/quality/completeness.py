from typing import TYPE_CHECKING

from models.enums import Degree
from models.utils import build_match
from quality.types import Component, DegreeErr
from utils.utils import logger

if TYPE_CHECKING:
    from neo4j import Result

    from driver.neo4j_driver import Neo4jSession
    from models.enums import Entity


def existence_component(
    session: Neo4jSession,
    entity: Entity,
    entity_alias: str,
    label: str,
    graph_pattern: str,
) -> Component | None:
    query: str = (
        f"{build_match(entity, label, entity_alias)} "
        "WHERE NOT EXISTS { "
        f"   MATCH {graph_pattern} "
        "} "
        "RETURN count(*) AS invalid "
    )

    try:
        result = session.run_query(query)  # ty:ignore[invalid-argument-type]
        record = result.single()
    except Exception as error:
        return logger.error(error)

    if record is None:
        return logger.error("No result found.")

    invalid = record.get("invalid")
    if invalid > 0:
        return Component(entity, entity_alias, label, graph_pattern, invalid)
    return None


def node_degree(
    session: Neo4jSession,
    degree: Degree,
    label: str,
    expected: set[int],
) -> DegreeErr | None:
    opt_pattern: str
    if degree == Degree.INCOMING:
        opt_pattern = "OPTIONAL MATCH ()-[r]->(n)"
    else:
        opt_pattern = "OPTIONAL MATCH ()<-[r]-(n)"

    query: str = (
        f"MATCH (n:{label}) "
        f"{opt_pattern} "
        "WITH id(n) AS k, COUNT(r) AS rels "
        f"WHERE NOT rels IN {list(expected)} "
        "RETURN collect(rels) AS invalid "
    )
    result: Result = session.run_query(query)  # ty:ignore[invalid-argument-type]
    record = result.single()

    if record:
        invalid: list[int] | None = record.get("invalid")

        if invalid:
            return DegreeErr(degree, label, set(invalid))
    return None
