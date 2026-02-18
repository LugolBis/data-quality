from typing import Optional

import pandas as pd
from neo4j import Record, Result

from driver.neo4j_driver import Neo4jSession
from quality.enums import Constraint, Entity
from quality.types import ConstraintViolation, IndexViolation
from quality.utils import _build_match, _format_label
from utils.utils import logger, some


def check_index_violation(session: Neo4jSession) -> Optional[list[IndexViolation]]:
    """
    Check if there is any **Node**/**Relationship** who's a `NULL` value on an indexed property.

    :param session: A `Neo4jSession` to query the database.
    :type session: Neo4jSession
    :return: The detailed report.
    :rtype: list[ConstraintViolation] | None
    """

    query: str = (
        "SHOW INDEXES "
        "YIELD entityType, labelsOrTypes, properties "
        "WHERE labelsOrTypes IS NOT NULL and properties IS NOT NULL "
        "RETURN * "
    )

    result: Result = session.run_query(query)
    df: pd.DataFrame = result.to_df()

    df["labelsOrTypes"] = df["labelsOrTypes"].apply(_format_label)
    df_exploded: pd.DataFrame = df.explode("properties")

    df_grouped: pd.DataFrame = pd.DataFrame(
        df_exploded.groupby(["entityType", "labelsOrTypes"], as_index=False)[
            "properties"
        ].agg(set)
    )

    violations: list[IndexViolation] = []
    for idx, row in df_grouped.iterrows():
        entity: Entity = Entity(row["entityType"])
        label: str = row["labelsOrTypes"]
        properties: list[str] = list(row["properties"])

        sub_query: str = (
            f"WITH {properties} AS requiredProps "
            f"{_build_match(entity, label)} "
            "RETURN COUNT(e) as count, "
            "COUNT(CASE WHEN any(p IN requiredProps WHERE e[p] IS NULL) THEN 1 END) AS invalid "
        )

        result_label: Result = session.run_query(sub_query)  # type: ignore
        first_row = result_label.single()
        if some(first_row):
            invalid: int = first_row["invalid"]
            count: int = first_row["count"]

            if invalid > 0:
                violations.append(IndexViolation(entity, label, count, invalid))

    if len(violations) > 0:
        return violations
    else:
        return None


def check_constraint_violation(
    session: Neo4jSession,
) -> Optional[list[ConstraintViolation]]:
    """
    Check if there is any **Node**/**Relationship** constraint who's violated.\n
    !!! CAUTION !!! : When it's `Constraint.UNIQUENESS` or `Constraint.KEY`, `ConstraintViolation.count` is the number of distinct pair of entity who violate the constraint.

    :param session: A `Neo4jSession` to query the database.
    :type session: Neo4jSession
    :return: The detailed report.
    :rtype: list[ConstraintViolation] | None
    """
    query: str = (
        "SHOW CONSTRAINTS "
        "YIELD type, entityType, labelsOrTypes, properties, ownedIndex, propertyType "
        "RETURN * "
    )

    result: Result = session.run_query(query)
    df: pd.DataFrame = result.to_df()

    df["type"] = df["type"].apply(lambda x: x.split("_")[-1])
    df["labelsOrTypes"] = df["labelsOrTypes"].apply(_format_label)

    violations: list[ConstraintViolation] = []
    for idx, row in df.iterrows():
        constraint: Constraint = Constraint(row["type"])
        entity: Entity = Entity(row["entityType"])
        label: str = row["labelsOrTypes"]
        properties: list[str] = row["properties"]
        sub_query: str

        match constraint:
            case Constraint.UNIQUENESS:
                sub_query = (
                    f"WITH {properties} AS requiredProps "
                    f"{_build_match(entity, label, 'e1')} "
                    f"{_build_match(entity, label, 'e2')} "
                    "WHERE elementId(e1) < elementId(e2) "
                    "WITH e1, e2, any(p IN requiredProps WHERE e1[p] <> e2[p]) AS is_valid "
                    "RETURN COUNT(*) AS count, "
                    "COUNT(CASE WHEN NOT is_valid THEN 1 END) AS invalid"
                )
            case Constraint.EXISTENCE:
                sub_query = (
                    f"WITH {properties} AS requiredProps "
                    f"{_build_match(entity, label)} "
                    "WITH e, any(p IN requiredProps WHERE e[p] IS NULL) AS is_invalid "
                    "RETURN COUNT(*) AS count, "
                    "COUNT(CASE WHEN is_invalid THEN 1 END) as invalid"
                )
            case Constraint.TYPE:
                sub_query = (
                    f"WITH {properties} AS requiredProps"
                    f"{_build_match(entity, label)} "
                    "WITH e, "
                    f"any(p IN requiredProps WHERE NOT valueType(e[p]) STARTS WITH '{row['propertyType']} ') AS is_invalid"
                    "RETURN COUNT(*) AS count, "
                    "COUNT(CASE WHEN is_invalid THEN 1 END) as invalid"
                )
            case Constraint.KEY:
                sub_query = (
                    f"WITH {properties} AS requiredProps "
                    f"{_build_match(entity, label, 'e1')} "
                    f"{_build_match(entity, label, 'e2')} "
                    "WHERE elementId(e1) < elementId(e2) "
                    "WITH e1, e2, "
                    "any(p IN requiredProps WHERE e1 IS NULL OR e2 IS NULL OR valueType(e1[p]) <> valueType(e2[p])) AS is_invalid, "
                    "any(p IN requiredProps WHERE e1[p] <> e2[p]) AS is_valid "
                    "RETURN COUNT(*) AS count, "
                    "COUNT(CASE WHEN (NOT is_valid) AND (is_invalid) THEN 1 END) AS invalid"
                )
            case default:
                logger.error(f"Unknown <EntityType> : {default}")
                continue

        result_label: Result = session.run_query(sub_query)  # type: ignore
        print(result_label.data())
        first_row: Optional[Record] = result_label.single()
        if some(first_row):
            invalid: int = first_row["invalid"]
            count: int = first_row["count"]

            if invalid > 0:
                violations.append(
                    ConstraintViolation(
                        entity, label, count, invalid, constraint, properties
                    )
                )

    if len(violations) > 0:
        return violations
    else:
        return None
