import re
from typing import Optional

from neo4j import Record, Result

from driver.neo4j_driver import Neo4jSession
from quality.enums import Entity
from quality.schema import _build_match
from quality.types import TextFormat
from utils.utils import some


def check_string_format(
    session: Neo4jSession,
    entity: Entity,
    label: str,
    properties: list[str],
    pattern: re.Pattern,
    case_insensitive: bool = False,
    multiline: bool = False,
    dotall: bool = False,
) -> Optional[list[TextFormat]]:
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
    for property in properties:
        query: str = (
            f"{_build_match(entity, label)} "
            f"WITH e, e[{property}] ~= '{pattern_str}' AS valid "
            "RETURN COUNT(*) as count, COUNT(CASE WHEN valid THEN 1 END) AS invalid"
        )

        result: Result = session.run_query(query)  # type: ignore
        row: Optional[Record] = result.single()

        if some(row):
            invalid: int = row["invalid"]
            count: int = row["count"]

            if invalid > 0:
                violations.append(
                    TextFormat(
                        entity=entity,
                        label=label,
                        count=count,
                        invalid=invalid,
                        property=property,
                    )
                )

    if len(violations) > 0:
        return violations
    else:
        return None
