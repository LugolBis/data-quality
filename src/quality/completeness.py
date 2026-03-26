from typing import TYPE_CHECKING

from models.utils import build_match
from quality.types import ElementaryPath
from utils.utils import logger

if TYPE_CHECKING:
    from driver.neo4j_driver import Neo4jSession
    from models.enums import Entity


def existence_path(
    session: Neo4jSession,
    entity: Entity,
    entity_alias: str,
    label_start: str,
    graph_pattern: str,
) -> ElementaryPath | None:
    query: str = (
        f"{build_match(entity, label_start, entity_alias)} "
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

    count = record.get("invalid")
    if count > 0:
        return ElementaryPath(entity, entity_alias, label_start, graph_pattern, query)
    return None
