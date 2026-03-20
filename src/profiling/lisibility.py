import math
from dataclasses import asdict
from typing import TYPE_CHECKING

import pandas as pd

from models.enums import Degree
from models.utils import format_label
from profiling.types import Eccentricity, MultiGraphEdges, NodeDegrees, Statistics
from profiling.utils import _compute_statistics
from utils.utils import logger, some

if TYPE_CHECKING:
    from neo4j import Record, Result

    from driver.neo4j_driver import Neo4jSession


def distr_node_degree(session: Neo4jSession) -> list[NodeDegrees] | None:
    """
    Compute statistics of the nodes degree.

    :param session: A `Neo4jSession` to query the database.
    :type session: Neo4jSession
    :return: The computed statistics of node degree.
    :rtype: list[NodeDegrees] | None
    """
    degrees: list[NodeDegrees] = []

    query: str = (
        "MATCH (n) "
        "OPTIONAL MATCH $$ "
        "RETURN id(n) AS id, labels(n) AS label, COUNT(r) AS degree "
    )

    result_in: Result = session.run_query(query.replace("$$", "(n)<-[r]-()"))
    result_out: Result = session.run_query(query.replace("$$", "(n)-[r]->()"))

    degrees_in: list[NodeDegrees] | None = _compute_node_degree(
        result_in,
        Degree.INCOMING,
    )
    degrees_out: list[NodeDegrees] | None = _compute_node_degree(
        result_out,
        Degree.OUTCOMING,
    )

    if some(degrees_in):
        degrees.extend(degrees_in)
        del degrees_in

    if some(degrees_out):
        degrees.extend(degrees_out)
        del degrees_out

    if len(degrees) > 0:
        return degrees
    return None


def check_multigraph_edges(session: Neo4jSession) -> list[MultiGraphEdges] | None:
    """
    Retrieves the information of **Nodes** and **Relationships** who form a *Multi Graph*.

    :param session: A `Neo4jSession` to query the database.
    :type session: Neo4jSession
    :return: A list of the edges and vertex who form a multigraph.
    :rtype: list[MultiGraphEdges] | None
    """

    query: str = (
        "MATCH (n1)-[r]->(n2) "
        "WITH n1, n2, collect(type(r)) AS relationships "
        "WHERE size(relationships) > 1 "
        "RETURN labels(n1) AS labels_from, labels(n2) AS labels_to, relationships "
    )

    result: Result = session.run_query(query)
    df: pd.DataFrame = result.to_df()

    df["labels_from"] = df["labels_from"].apply(format_label)
    df["labels_to"] = df["labels_to"].apply(format_label)

    edges: list[MultiGraphEdges] = []
    for _idx, row in df.iterrows():
        label_from: str = row["labels_from"]
        label_to: str = row["labels_to"]
        relationships: list[str] = row["relationships"]

        edges.append(MultiGraphEdges(label_from, label_to, relationships))

    if len(edges) > 0:
        return edges
    return None


def compute_graph_eccentricity(session: Neo4jSession) -> Eccentricity:
    """
    Compute Graph eccentricity.

    :param session: A `Neo4jSession` to query the database.
    :type session: Neo4jSession
    :param gds_graph_name: Name for the GDS graph.
    :type gds_graph_name: str
    :return: The graph diameter and radius or `NaN` value if the computations failed.
    :rtype: tuple[float, float]
    """
    gds_graph_name: str = "analysis_graph_diameter"
    _create_gds_graph(session, gds_graph_name)

    query: str = (
        "MATCH (n) "
        "CALL gds.allShortestPaths.dijkstra.stream( "
        f"  '{gds_graph_name}', "
        "   { sourceNode: n } "
        ") YIELD totalCost "
        "WITH n, MAX(totalCost) AS distant "
        "WHERE distant > 0 "
        "RETURN max(distant) as diameter, min(distant) as radius"
    )

    try:
        result: Result = session.run_query(query)
        row: Record | None = result.single()

        if some(row):
            return Eccentricity(diameter=row["diameter"], radius=row["radius"])
    except Exception as error:
        logger.error(error)

    return Eccentricity(math.nan, math.nan)


def _create_gds_graph(session: Neo4jSession, gds_graph_name: str) -> None:
    """
    Drop and Project a GDS graph.

    :param session: A `Neo4jSession` to query the database.
    :type session: Neo4jSession
    :param gds_graph_name: Name for the GDS graph.
    :type gds_graph_name: str
    """
    try:
        session.run_query(f"CALL gds.graph.drop('{gds_graph_name}', false)")  # type: ignore
    except Exception as error:
        logger.error(error)

    try:
        session.run_query(f"CALL gds.graph.project('{gds_graph_name}', '*', '*')")  # type: ignore
    except Exception as error:
        logger.error(error)


def _compute_node_degree(result: Result, degree: Degree) -> list[NodeDegrees] | None:
    """
    Compute node degree.

    :param result: Cypher query result.
    :type result: Result
    :param degree: Specify if the degree is `incoming` or `outcoming`.
    :type degree: Degree
    :return: A list of nodes degree.
    :rtype: list[NodeDegrees] | None
    """
    df: pd.DataFrame = result.to_df()
    df["label"] = df["label"].apply(format_label)

    df_aggregated: pd.DataFrame = pd.DataFrame(
        df.groupby("label", as_index=False)["degree"].agg(list),
    )

    del df

    degrees: list[NodeDegrees] = []
    for _idx, row in df_aggregated.iterrows():
        label: str = row["label"]
        values: list[int | float] = row["degree"]

        statistics: Statistics | None = _compute_statistics(values)

        if some(statistics):
            degrees.append(
                NodeDegrees(**asdict(statistics), label=label, degree=degree),
            )

    if len(degrees) > 0:
        return degrees
    return None
