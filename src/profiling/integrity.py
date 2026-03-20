from typing import TYPE_CHECKING

from models.enums import Entity
from models.utils import format_label
from profiling.types import EntityProperties, EntityStats
from utils.utils import logger

if TYPE_CHECKING:
    import pandas as pd
    from neo4j import Result

    from driver.neo4j_driver import Neo4jSession


def distr_nodes_properties(session: Neo4jSession) -> list[EntityStats] | None:
    """
    [Schema Integrity] Analyze if nodes with the same label combination
    share the exact same set of property keys.

    :param self: The object itself.
    """

    query: str = (
        "MATCH (n) "
        "WITH labels(n) AS Labels, keys(n) AS PropertyKeys "
        "RETURN Labels, PropertyKeys, count(*) AS Nombre "
    )

    result: Result = session.run_query(query)
    df: pd.DataFrame = result.to_df()

    try:
        df["Label_Combo"] = df["Labels"].apply(lambda x: tuple(sorted(x)))
        df["Property_Keys_Set"] = df["PropertyKeys"].apply(lambda x: tuple(sorted(x)))
        labels_uniques = df["Label_Combo"].unique()
    except Exception as error:
        logger.error(error)
        return None

    analysis: list[EntityStats] = []

    for label_tuple in labels_uniques:
        groupe: pd.DataFrame = df[df["Label_Combo"] == label_tuple]
        total_nodes: int = groupe["Nombre"].sum()
        label_str: str = format_label(label_tuple)

        properties: list[EntityProperties] = []

        groupe_sorted: pd.DataFrame = groupe.sort_values(by="Nombre", ascending=False)

        for _index, row in groupe_sorted.iterrows():
            props: list[str] = list(row["Property_Keys_Set"])
            count: int = int(row["Nombre"])
            percent: float = float((count / total_nodes) * 100)

            properties.append(EntityProperties(props, count, percent))

        analysis.append(
            EntityStats(
                entity=Entity.NODE,
                label=label_str,
                count=total_nodes,
                properties=properties,
            ),
        )

    return analysis


def distr_relationships_properties(
    session: Neo4jSession,
) -> list[EntityStats] | None:
    """
    [Relationship Schema Integrity]
    Analyze if relationships of the same TYPE share the exact same set of property keys.

    :param self: The object itself.
    """
    query: str = (
        "MATCH ()-[r]->() "
        "WITH type(r) AS RelType, keys(r) AS PropertyKeys "
        "RETURN RelType, PropertyKeys, count(*) AS Nombre "
    )

    result: Result = session.run_query(query)
    df: pd.DataFrame = result.to_df()

    try:
        df["Property_Keys_Set"] = df["PropertyKeys"].apply(lambda x: tuple(sorted(x)))
        types_unique = df["RelType"].unique()
    except Exception as error:
        logger.error(error)
        return None

    analysis: list[EntityStats] = []

    for r_type in types_unique:
        groupe: pd.DataFrame = df[df["RelType"] == r_type]
        total: int = groupe["Nombre"].sum()

        properties: list[EntityProperties] = []
        groupe_sorted = groupe.sort_values(by="Nombre", ascending=False)

        for _index, row in groupe_sorted.iterrows():
            props: list[str] = list(row["Property_Keys_Set"])
            count: int = int(row["Nombre"])
            percent: float = float((count / total) * 100)

            properties.append(EntityProperties(props, count, percent))

        analysis.append(
            EntityStats(
                entity=Entity.RELATIONSHIP,
                label=r_type,
                count=total,
                properties=properties,
            ),
        )

    return analysis
