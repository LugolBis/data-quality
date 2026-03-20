from typing import TYPE_CHECKING

from models.enums import Entity
from models.utils import build_match, format_label
from profiling.types import PairPropertiesType

if TYPE_CHECKING:
    import pandas as pd
    from neo4j import Result

    from driver.neo4j_driver import Neo4jSession


def check_properties_type(session: Neo4jSession) -> list[PairPropertiesType] | None:
    """
    Check if there is any pair of **Node**/**Relationship** who has one property with
     different type.

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
    for _idx, row in df.iterrows():
        entity: Entity = Entity(row["elementType"])
        properties: list[str] = row["properties"]

        if len(properties) == 0:
            continue

        label: str
        match entity:
            case Entity.NODE:
                label = format_label(row["label"])
            case Entity.RELATIONSHIP:
                label = str(row["label"]).split(":")[-1].replace("`", "")

        query_sub: str = (
            f"{build_match(entity, label, 'e')} \n"
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
            "WITH property, count, [SPLIT(valueType(v1), ' ')[0], SPLIT(valueType(v2), ' ')[0]] AS types \n"  # noqa: E501
            "RETURN property, count, COUNT(*) AS invalid, collect(DISTINCT types) AS type_pairs \n"  # noqa: E501
        )

        result_sub: Result = session.run_query(query_sub)  # ty:ignore[invalid-argument-type]
        df_sub: pd.DataFrame = result_sub.to_df()

        for _, row_sub in df_sub.iterrows():
            invalid: int = row_sub["invalid"]

            if invalid > 0:
                count: int = row_sub["count"]
                p: str = row_sub["property"]
                types: set[tuple[str, str]] = {
                    tuple(sorted(types)) for types in row_sub["type_pairs"]
                }

                inconsistencies.append(
                    PairPropertiesType(entity, label, count, invalid, p, types),
                )

    if len(inconsistencies) > 0:
        return inconsistencies
    return None
