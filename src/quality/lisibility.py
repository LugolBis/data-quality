import math
from typing import Optional

import pandas as pd
from neo4j import Record, Result

from driver.neo4j_driver import Neo4jSession
from quality.enums import Degree
from quality.types import MultiGraphEdges, NodeDegrees, Statistics
from quality.utils import _compute_statistics, _format_label
from utils.utils import logger, some


def distr_node_degree(session: Neo4jSession) -> Optional[list[NodeDegrees]]:
    degrees: list[NodeDegrees] = []

    query: str = (
        "MATCH (n) "
        "OPTIONAL MATCH $$ "
        "RETURN id(n) AS id, labels(n) AS label, COUNT(r) AS degree "
    )

    result_in: Result = session.run_query(query.replace("$$", "(n)<-[r]-()"))
    result_out: Result = session.run_query(query.replace("$$", "(n)-[r]->()"))

    degrees_in: Optional[list[NodeDegrees]] = _compute_node_degree(
        result_in, Degree.INCOMING
    )
    degrees_out: Optional[list[NodeDegrees]] = _compute_node_degree(
        result_out, Degree.OUTCOMING
    )

    if some(degrees_in):
        degrees.extend(degrees_in)
        del degrees_in

    if some(degrees_out):
        degrees.extend(degrees_out)
        del degrees_out

    if len(degrees) > 0:
        return degrees
    else:
        return None


def check_multigraph_edges(session: Neo4jSession) -> Optional[list[MultiGraphEdges]]:
    query: str = (
        "MATCH (n1)-[r]->(n2) "
        "WITH n1, n2, collect(type(r)) AS relationships "
        "WHERE size(relationships) > 1 "
        "RETURN labels(n1) AS labels_from, labels(n2) AS labels_to, relationships "
    )

    result: Result = session.run_query(query)
    df: pd.DataFrame = result.to_df()

    df["labels_from"] = df["labels_from"].apply(_format_label)
    df["labels_to"] = df["labels_to"].apply(_format_label)

    edges: list[MultiGraphEdges] = []
    for idx, row in df.iterrows():
        label_from: str = row["labels_from"]
        label_to: str = row["labels_to"]
        relationships: list[str] = row["relationships"]

        edges.append(MultiGraphEdges(label_from, label_to, relationships))

    if len(edges) > 0:
        return edges
    else:
        return None


def compute_graph_diameter(session: Neo4jSession, gds_graph_name: str) -> float:
    _create_gds_graph(session, gds_graph_name)

    query: str = (
        "MATCH (n) "
        "CALL gds.allShortestPaths.dijkstra.stream( "
        f"  '{gds_graph_name}', "
        "   { sourceNode: n } "
        ") YIELD totalCost "
        "WITH n, MAX(totalCost) AS distant "
        "WHERE distant > 0 "
        "RETURN max(distant) as diameter"
    )

    try:
        print(query)

        result: Result = session.run_query(query)  # type: ignore
        row: Optional[Record] = result.single()

        if some(row):
            return row["diameter"]
    except Exception as error:
        logger.error(error)

    return math.nan


def _create_gds_graph(session: Neo4jSession, gds_graph_name: str) -> None:
    try:
        session.run_query(f"CALL gds.graph.drop('{gds_graph_name}', false)")  # type: ignore
    except Exception as error:
        logger.error(error)

    try:
        session.run_query(f"CALL gds.graph.project('{gds_graph_name}', '*', '*')")  # type: ignore
    except Exception as error:
        logger.error(error)


def _compute_node_degree(result: Result, degree: Degree) -> Optional[list[NodeDegrees]]:
    df: pd.DataFrame = result.to_df()
    df["label"] = df["label"].apply(_format_label)

    df_aggregated: pd.DataFrame = pd.DataFrame(
        df.groupby("label", as_index=False)["degree"].agg(list)
    )

    del df

    degrees: list[NodeDegrees] = []
    for idx, row in df_aggregated.iterrows():
        label: str = row["label"]
        values: list[int | float] = row["degree"]

        statistics: Optional[Statistics] = _compute_statistics(values)

        if some(statistics):
            degrees.append(NodeDegrees(**vars(statistics), label=label, degree=degree))

    if len(degrees) > 0:
        return degrees
    else:
        return None
