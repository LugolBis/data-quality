from typing import Optional

import pandas as pd
from neo4j import Result

from driver.neo4j_driver import Neo4jSession
from quality.enums import Entity
from quality.types import IndexViolation
from utils.utils import logger, some


def check_index_violation(session: Neo4jSession) -> Optional[list[IndexViolation]]:
    query: str = (
        "SHOW INDEXES "
        "YIELD Entity, labelsOrTypes, properties "
        "WHERE labelsOrTypes IS NOT NULL and properties IS NOT NULL "
        "RETURN * "
    )

    result: Result = session.run_query(query)
    df: pd.DataFrame = result.to_df()

    df["labelsOrTypes"] = df["labelsOrTypes"].apply(lambda x: "&".join(x))
    df_exploded: pd.DataFrame = df.explode("properties")

    df_grouped: pd.DataFrame = pd.DataFrame(
        df_exploded.groupby(["Entity", "labelsOrTypes"], as_index=False)[
            "properties"
        ].agg(set)
    )

    violations: list[IndexViolation] = []
    for idx, row in df_grouped.iterrows():
        entity_type: Entity = Entity(row["Entity"])
        labels_str: str = row["labelsOrTypes"]
        properties: list[str] = list(row["properties"])
        sub_query: str

        match entity_type:
            case Entity.NODE:
                sub_query = (
                    f"WITH {properties} AS requiredProps "
                    f"MATCH (n: {labels_str}) "
                    "RETURN COUNT(n) as count, "
                    "COUNT(CASE WHEN any(p IN requiredProps WHERE n[p] IS NULL) THEN 1 END) AS invalid "
                )
            case Entity.RELATIONSHIP:
                sub_query = (
                    f"WITH {properties} AS requiredProps "
                    f"MATCH ()-[r: {labels_str}]->() "
                    "RETURN COUNT(r) as count, "
                    "COUNT(CASE WHEN any(p IN requiredProps WHERE r[p] IS NULL) THEN 1 END) AS invalid "
                )
            case default:
                logger.error(f"Unknown <EnityType> : {default}")
                continue

        result_label: Result = session.run_query(sub_query)  # type: ignore
        first_row = result_label.single()
        if some(first_row):
            invalid: int = first_row["invalid"]
            count: int = first_row["count"]

            if invalid > 0:
                percent: float = round(float((invalid / count) * 100), 2)
                violations.append(
                    IndexViolation(
                        entity=entity_type,
                        label=labels_str,
                        count=count,
                        percent=percent,
                    )
                )

    if len(violations) > 0:
        return violations
    else:
        return None
