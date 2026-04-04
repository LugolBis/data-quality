from typing import TYPE_CHECKING

from models.utils import build_match
from quality.types import _ENTITY_CONDITION_ALIAS, CFDErr, Condition, FDErr, GFDErr
from quality.utils import _graph_pattern_parser
from utils.utils import logger

if TYPE_CHECKING:
    from neo4j import Result

    from driver.neo4j_driver import Neo4jSession
    from models.enums import Entity


def fd(
    session: Neo4jSession,
    entity: Entity,
    label: str,
    x: set[str],
    y: set[str],
) -> FDErr | None:
    query: str = (
        f"{build_match(entity, label, 'e1')}, "
        f"{build_match(entity, label, 'e2').removeprefix('MATCH')} "
        "WHERE id(e1) < id(e2) "
        f"WITH e1, e2, {list(x)} AS X, {list(y)} AS Y "
        "WITH e1, e2, X, Y, "
        "[px1 in X | e1[px1]] AS X1, [px2 in X | e2[px2]] AS X2 "
        "WHERE X1 = X2 "
        "WITH e1, e2, Y, "
        "[py1 in Y | e1[py1]] AS Y1, [py2 in Y | e2[py2]] AS Y2 "
        "WHERE Y1 <> Y2 "
        "RETURN COUNT(*) AS invalid"
    )

    result: Result = session.run_query(query)  # ty:ignore[invalid-argument-type]
    record = result.single()

    if record:
        invalid: int = record.get("invalid")

        if invalid:
            return FDErr(entity, label, x, y, invalid)
        logger.error(f"Invalid record : {record}")
    return None


def cfd(  # noqa: PLR0913
    session: Neo4jSession,
    entity: Entity,
    label: str,
    condition: Condition,
    x: set[str],
    y: set[str],
) -> CFDErr | None:
    condition1 = str(condition).replace(_ENTITY_CONDITION_ALIAS, "e1")
    condition2 = str(condition).replace(_ENTITY_CONDITION_ALIAS, "e2")

    query: str = (
        f"{build_match(entity, label, 'e1')}, "
        f"{build_match(entity, label, 'e2').removeprefix('MATCH')} "
        "WHERE id(e1) < id(e2) "
        f"AND ({condition1}) AND ({condition2}) "
        f"WITH e1, e2, {list(x)} AS X, {list(y)} AS Y "
        "WITH e1, e2, X, Y, "
        "[px1 in X | e1[px1]] AS X1, [px2 in X | e2[px2]] AS X2 "
        "WHERE X1 = X2 "
        "WITH e1, e2, Y, "
        "[py1 in Y | e1[py1]] AS Y1, [py2 in Y | e2[py2]] AS Y2 "
        "WHERE Y1 <> Y2 "
        "RETURN COUNT(*) AS invalid"
    )

    result: Result = session.run_query(query)  # ty:ignore[invalid-argument-type]
    record = result.single()

    if record:
        invalid: int = record.get("invalid")

        if invalid > 0:
            return CFDErr(entity, label, str(condition), x, y, invalid)
    return None


def gfd(  # noqa: PLR0913
    session: Neo4jSession,
    entity: Entity,
    entity_alias: str,
    label: str,
    graph_pattern: str,
    x: set[str],
    y: set[str],
) -> GFDErr | None:
    query: str = (
        f"MATCH {_graph_pattern_parser(graph_pattern, entity_alias, 1, label)}, "
        f"{_graph_pattern_parser(graph_pattern, entity_alias, 2, label)} "
        f"WITH {entity_alias}1 AS e1, {entity_alias}2 AS e2 "
        "WHERE id(e1) < id(e2) "
        f"WITH e1, e2, {list(x)} AS X, {list(y)} AS Y "
        "WITH e1, e2, X, Y, "
        "[px1 in X | e1[px1]] AS X1, [px2 in X | e2[px2]] AS X2 "
        "WHERE X1 = X2 "
        "WITH e1, e2, Y, "
        "[py1 in Y | e1[py1]] AS Y1, [py2 in Y | e2[py2]] AS Y2 "
        "WHERE Y1 <> Y2 "
        "RETURN COUNT(DISTINCT [id(e1), id(e2)]) AS invalid"
    )

    result: Result = session.run_query(query)  # ty:ignore[invalid-argument-type]
    record = result.single()

    if record:
        invalid: int = record.get("invalid")

        if invalid:
            return GFDErr(entity, entity_alias, label, graph_pattern, x, y, invalid)
    return None
