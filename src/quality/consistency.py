import re
from typing import Optional

import pandas as pd
from neo4j import Record, Result

from driver.neo4j_driver import Neo4jSession
from quality.enums import Entity
from quality.schema import _build_match
from quality.types import PairPropertiesType, TextFormat
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
    """
    Check if there is any **Node**/**Relationship** who has one of `properties` who doesn't match the string `pattern`.

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
    for property in properties:
        query: str = (
            f"{_build_match(entity, label)} "
            f"WITH e, e['{property}'] =~ '{pattern_str}' AS valid "
            "RETURN COUNT(*) as count, COUNT(CASE WHEN valid THEN 1 END) AS invalid"
        )

        result: Result = session.run_query(query)  # type: ignore
        row: Optional[Record] = result.single()

        if some(row):
            invalid: int = row["invalid"]
            count: int = row["count"]

            if invalid > 0:
                violations.append(TextFormat(entity, label, count, invalid, property))

    if len(violations) > 0:
        return violations
    else:
        return None


def check_properties_type(session: Neo4jSession) -> Optional[list[PairPropertiesType]]:
    query: str = (
        "CALL () { "
        "CALL db.schema.nodeTypeProperties() "
        "YIELD nodeLabels, propertyName, propertyTypes "
        "RETURN nodeLabels AS label, 'NODE' AS elementType, propertyName, propertyTypes AS type "
        "UNION ALL "
        "CALL db.schema.relTypeProperties() "
        "YIELD relType, propertyName, propertyTypes "
        "RETURN relType AS label, 'RELATIONSHIP' AS elementType, propertyName, propertyTypes AS type "
        "} RETURN label, elementType, type, collect(propertyName) AS properties "
    )

    result: Result = session.run_query(query)
    df: pd.DataFrame = result.to_df()

    inconsistencies: list[PairPropertiesType] = []
    for idx, row in df.iterrows():
        entity: Entity = Entity(row["elementType"])
        properties: list[str] = row["properties"]
        type: str = row["type"][0]

        if len(properties) == 0:
            continue

        label: str
        match entity:
            case Entity.NODE:
                label = "&".join(row["label"])
            case Entity.RELATIONSHIP:
                label = str(row["label"]).split(":")[-1].replace("`", "")

        sub_query: str = (
            f"WITH {properties} AS requiredProps "
            f"{_build_match(entity, label, 'e1')} "
            f"{_build_match(entity, label, 'e2')} "
            "WHERE elementId(e1) < elementId(e2) "
            "WITH e1, e2, "
            "any( p IN requiredProps"
            "   WHERE e1[p] IS NOT NULL AND e2[p] IS NOT NULL "
            f"   AND ((valueType(e1[p]) STARTS WITH '{type} ') <> (valueType(e2[p]) STARTS WITH '{type} '))"
            ") AS is_invalid "
            "RETURN COUNT(*) AS count, "
            "COUNT(CASE WHEN is_invalid THEN 1 END) AS invalid"
        )

        print(sub_query)

        sub_result: Result = session.run_query(sub_query)  # type: ignore
        sub_row: Optional[Record] = sub_result.single()

        if some(sub_row):
            count: int = sub_row["count"]
            invalid: int = sub_row["invalid"]

            if invalid > 0:
                inconsistencies.append(
                    PairPropertiesType(entity, label, count, invalid)
                )

    if len(inconsistencies) > 0:
        return inconsistencies
    else:
        return None
