from typing import TYPE_CHECKING

from models.utils import build_match
from quality.types import TextFormat
from utils.utils import some

if TYPE_CHECKING:
    import re

    from neo4j import Record, Result

    from driver.neo4j_driver import Neo4jSession
    from models.enums import Entity


def check_string_format(  # noqa: PLR0913
    session: Neo4jSession,
    entity: Entity,
    label: str,
    properties: list[str],
    pattern: re.Pattern,
    case_insensitive: bool = False,  # noqa: FBT001, FBT002
    multiline: bool = False,  # noqa: FBT001, FBT002
    dotall: bool = False,  # noqa: FBT001, FBT002
) -> list[TextFormat] | None:
    """
    Check if there is any **Node**/**Relationship** who has one of `properties` who
     doesn't match the string `pattern`.

    :param session: A `Neo4jSession` to query the database.
    :type session: Neo4jSession
    :param entity: Entity kind.
    :type entity: Entity
    :param label: Label or Type of the entity.
    :type label: str
    :param properties: Target properties.
    :type properties: list[str]
    :param pattern: Regular expression to match the target format.
    :type pattern: re.Pattern
    :param case_insensitive: `True` if case sensitivity doesn't matter.
    :type case_insensitive: bool
    :param multiline: `True` if multiline doesn't matter.
    :type multiline: bool
    :param dotall: `True` if dotall doesn't matter.
    :type dotall: bool
    :return: DescriptionThe detailed report.
    :rtype: list[TextFormat] | None
    """
    pattern_str: str = pattern.pattern
    flags: str = ""

    if case_insensitive:
        flags += "i"
    if multiline:
        flags += "m"
    if dotall:
        flags += "d"

    if len(flags) > 0:
        pattern_str = f"(?{flags}){pattern_str}"

    violations: list[TextFormat] = []
    for p in properties:
        query: str = (
            f"{build_match(entity, label)} "
            f"WITH e, e['{p}'] =~ '{pattern_str}' AS valid "
            "RETURN COUNT(*) as count, COUNT(CASE WHEN NOT valid THEN 1 END) AS invalid"
        )

        result: Result = session.run_query(query)  # ty:ignore[invalid-argument-type]
        row: Record | None = result.single()

        if some(row):
            invalid: int = row["invalid"]
            count: int = row["count"]

            if invalid > 0:
                violations.append(TextFormat(entity, label, count, invalid, property=p))

    if len(violations) > 0:
        return violations
    return None
