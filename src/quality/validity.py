from typing import TYPE_CHECKING

from models.enums import Entity
from models.utils import build_match
from quality.enums import SetRelation
from quality.types import DateErr, LblgSetErr, TextFormat
from utils.utils import logger, some

if TYPE_CHECKING:
    import re

    from neo4j import Record, Result

    from driver.neo4j_driver import Neo4jSession
    from quality.enums import DateFmt


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


def check_date_format(  # noqa: PLR0913
    session: Neo4jSession,
    entity: Entity,
    label: str,
    properties: list[str],
    date_fmt: DateFmt,
    skip_null: bool = True,  # noqa: FBT001, FBT002
) -> list[DateErr] | None:
    query: str = (
        f"{build_match(entity, label)}"
        f"UNWIND {properties} AS targetProperty "
        "WITH e, targetProperty "
        f"WHERE e[targetProperty] IS NOT :: {date_fmt!s} "
        f"{'AND e[targetProperty] IS NOT NULL ' if skip_null else ''} "
        "RETURN targetProperty, "
        "collect(valueType(e[targetProperty])) AS fmt_found "
    )

    result: Result = session.run_query(query)  # ty:ignore[invalid-argument-type]
    records = result.to_eager_result().records

    analysis: list[DateErr] = []
    for record in records:
        target_prop: str | None = record.get("targetProperty")
        fmt_found: list[str] | None = record.get("fmt_found")

        if some(target_prop) and some(fmt_found):
            analysis.append(
                DateErr(entity, label, target_prop, set(fmt_found)),
            )
        else:
            logger.error(f"Invalid record {record}")

    if len(analysis) > 0:
        return analysis
    return None


def labeling_set(
    session: Neo4jSession,
    label: str,
    set_rel: SetRelation,
    cmp_set: set[str],
) -> LblgSetErr | None:
    match set_rel:
        case SetRelation.EXCLUDE:
            where_clause: str = "any(l IN L WHERE l IN X)"
        case SetRelation.INCLUDE:
            where_clause: str = "(NOT any(l IN L WHERE l IN X)) OR size(X) = size(L)"
        case SetRelation.INCLUDE_EQ:
            where_clause: str = "NOT any(l IN L WHERE l IN X)"
        case default:
            logger.error(f"Inconsistant set relation : {default}")
            return None

    query: str = (
        f"{build_match(Entity.NODE, label, 'n')} "
        f"WITH n, {'labels(n) AS L'}, "
        f"{list(cmp_set)} AS X "
        f"WHERE {where_clause} "
        "RETURN COUNT(*) AS invalid"
    )

    result: Result = session.run_query(query)  # ty:ignore[invalid-argument-type]
    record = result.single()

    if record:
        invalid: int = record.get("invalid")
        if invalid > 0:
            return LblgSetErr(label, cmp_set, set_rel, invalid)
    return None
