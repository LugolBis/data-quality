import re
from typing import Optional, Set, Tuple

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
    """
    Check if there is any pair of **Node**/**Relationship** who has one property with different type.

    :param session: A `Neo4jSession` to query the database.
    :type session: Neo4jSession
    :return: The list of pair who has one or more shared properties with different type.
    :rtype: list[PairPropertiesType] | None
    """

    query: str = (
        "CALL () { "
        "CALL db.schema.nodeTypeProperties() "
        "YIELD nodeLabels, propertyName "
        "RETURN nodeLabels AS label, 'NODE' AS elementType, propertyName "
        "UNION ALL "
        "CALL db.schema.relTypeProperties() "
        "YIELD relType, propertyName "
        "RETURN relType AS label, 'RELATIONSHIP' AS elementType, propertyName "
        "} RETURN label, elementType, collect(propertyName) AS properties "
    )

    result: Result = session.run_query(query)
    df: pd.DataFrame = result.to_df()

    inconsistencies: list[PairPropertiesType] = []
    for idx, row in df.iterrows():
        entity: Entity = Entity(row["elementType"])
        properties: list[str] = row["properties"]

        if len(properties) == 0:
            continue

        label: str
        match entity:
            case Entity.NODE:
                label = "&".join(row["label"])
            case Entity.RELATIONSHIP:
                label = str(row["label"]).split(":")[-1].replace("`", "")

        query_sub: str = (
            f"{_build_match(entity, label, 'e')} \n"
            "WITH collect(e) AS entities, COUNT(e) AS total_entities \n"
            "UNWIND entities AS e1 \n"
            "UNWIND entities AS e2 \n"
            "WITH e1, e2, \n"
            "   (total_entities * (total_entities - 1)) / 2 AS count \n"
            "WHERE elementId(e1) < elementId(e2) \n"
            f"UNWIND {properties} AS property \n"
            "WITH e1, e2, count, property, \n"
            "   e1[property] AS v1, e2[property] AS v2 \n"
            "WHERE v1 IS NOT NULL AND v2 IS NOT NULL \n"
            "   AND SPLIT(valueType(v1), ' ')[0] <> SPLIT(valueType(v2), ' ')[0] \n"
            "WITH property, count, [SPLIT(valueType(v1), ' ')[0], SPLIT(valueType(v2), ' ')[0]] AS types \n"
            "RETURN property, count, COUNT(*) AS invalid, collect(DISTINCT types) AS type_pairs \n"
        )

        result_sub: Result = session.run_query(query_sub)  # type: ignore
        df_sub: pd.DataFrame = result_sub.to_df()

        for idx, row_sub in df_sub.iterrows():
            invalid: int = row_sub["invalid"]

            if invalid > 0:
                count: int = row_sub["count"]
                property: str = row_sub["property"]
                types: Set[Tuple[str, str]] = {
                    tuple(sorted(types)) for types in row_sub["type_pairs"]
                }

                inconsistencies.append(
                    PairPropertiesType(entity, label, count, invalid, property, types)
                )

    if len(inconsistencies) > 0:
        return inconsistencies
    else:
        return None
