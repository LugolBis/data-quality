from collections import defaultdict
from typing import TYPE_CHECKING, Any

import pandas as pd

from models.utils import get_label
from profiling.types import (
    CentralityScore,
    LabelCentralityStats,
    NumericalOutlier,
    OutlierDetail,
)
from utils.utils import logger

if TYPE_CHECKING:
    from neo4j import Result

    from driver.neo4j_driver import Neo4jSession


def detecter_outliers_numeriques(
    session: Neo4jSession,
    z_score_threshold: float = 1.96,
) -> list[NumericalOutlier] | None:
    """
    [Numerical Outliers]
    Calculate mean, standard deviation and confidence interval to detect numerical outliers.

    :param session: A `Neo4jSession` to query the database.
    :type session: Neo4jSession
    :param z_score_threshold: The Z-Score threshold to define outliers.
    :type z_score_threshold: float
    :return: The detailed list of numerical outliers.
    :rtype: list[NumericalOutlier] | None
    """
    query: str = "MATCH (n) RETURN elementId(n) as ID, labels(n) as Labels, properties(n) as Props"

    try:
        result: Result = session.run_query(query)
        nodes: list[dict[str, Any]] = [record.data() for record in result]
    except Exception as e:
        logger.error(f"Error fetching nodes for outliers: {e}")
        return None

    groups: dict[str, list] = defaultdict(list)
    for node in nodes:
        label_key = get_label(node["Labels"])
        groups[label_key].append(node)

    detected_outliers: list[NumericalOutlier] = []

    for label_str, group_nodes in groups.items():
        numeric_data = defaultdict(dict)

        for node in group_nodes:
            node_id = node["ID"]
            for key, val in node["Props"].items():
                if isinstance(val, (int, float)) and not isinstance(val, bool):
                    numeric_data[key][node_id] = val

        for prop, values_dict in numeric_data.items():
            if len(values_dict) < 3:
                continue

            s = pd.Series(values_dict)
            moyenne = float(s.mean())
            ecart_type = float(s.std())

            if pd.isna(ecart_type) or ecart_type == 0:
                continue

            lower_bound = moyenne - (z_score_threshold * ecart_type)
            upper_bound = moyenne + (z_score_threshold * ecart_type)

            outliers = s[(s < lower_bound) | (s > upper_bound)]

            if not outliers.empty:
                details = [
                    OutlierDetail(node_id=str(out_id), value=float(out_val))
                    for out_id, out_val in outliers.items()
                ]

                detected_outliers.append(
                    NumericalOutlier(
                        label=label_str,
                        property_=prop,
                        mean=moyenne,
                        std_dev=ecart_type,
                        lower_bound=lower_bound,
                        upper_bound=upper_bound,
                        outliers=details,
                    ),
                )

    return detected_outliers if detected_outliers else None


def measure_eigenvector_centrality(
    session: Neo4jSession,
    epsilon: float = 0.5,
) -> list[CentralityScore] | None:
    """
    Check the graph topology and measure 'Eigenvector Centrality' with the Neo4j GDS plugin.

    :param session: A `Neo4jSession` to query the database.
    :type session: Neo4jSession
    :return: The detailed list of centrality scores for the top 5 nodes.
    :rtype: list[CentralityScore] | None
    """
    graph_name: str = "quality_analysis_graph"
    scores: list[CentralityScore] = []

    try:
        drop_query: str = f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName"
        session.run_query(drop_query)

        project_query: str = (
            f"CALL gds.graph.project('{graph_name}', '*', '*') YIELD graphName"
        )
        session.run_query(project_query)

        eigen_query: str = (
            f"CALL gds.eigenvector.stream('{graph_name}') "
            "YIELD nodeId, score "
            f"WHERE score > {epsilon} "
            "RETURN gds.util.asNode(nodeId) AS node, score "
            "ORDER BY score DESC "
        )
        result: Result = session.run_query(eigen_query)  # type: ignore

        for record in result:
            node = record["node"]
            score: float = float(record["score"])

            labels: str = get_label(list(node.labels))

            display_name: str = str(
                node.get("name") or node.get("title") or "<Unnamed>",
            )

            scores.append(CentralityScore(labels, display_name, score))

    except Exception as error:
        logger.error(f"GDS Execution Error (Eigenvector Centrality): {error}")
        return None

    finally:
        try:
            cleanup_query: str = (
                f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName"
            )
            session.run_query(cleanup_query)
        except Exception as cleanup_error:
            logger.error(f"Failed to drop GDS graph memory: {cleanup_error}")

    if len(scores) > 0:
        return scores
    return None


def measure_average_centrality_by_label(
    session: Neo4jSession,
) -> list[LabelCentralityStats] | None:
    """
    Check the graph topology and calculate the average 'Eigenvector Centrality' grouped by node labels.\n

    :param session: A `Neo4jSession` to query the database.
    :type session: Neo4jSession
    :return: A list containing the average and max centrality scores per label combination.
    :rtype: list[LabelCentralityStats] | None
    """
    graph_name: str = "quality_analysis_graph_avg"
    stats_list: list[LabelCentralityStats] = []

    try:
        drop_query: str = f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName"
        session.run_query(drop_query)

        project_query: str = (
            f"CALL gds.graph.project('{graph_name}', '*', '*') YIELD graphName"
        )
        session.run_query(project_query)

        agg_query: str = (
            f"CALL gds.eigenvector.stream('{graph_name}') "
            "YIELD nodeId, score "
            "WITH gds.util.asNode(nodeId) AS n, score "
            "RETURN labels(n) AS raw_labels, "
            "       count(n) AS nodeCount, "
            "       avg(score) AS avgScore, "
            "       max(score) AS maxScore "
            "ORDER BY avgScore DESC"
        )
        result: Result = session.run_query(agg_query)

        for record in result:
            raw_labels: list[str] = record["raw_labels"]
            count: int = record["nodeCount"]
            avg_score: float = float(record["avgScore"])
            max_score: float = float(record["maxScore"])

            label_str: str = get_label(raw_labels) if raw_labels else "UNLABELED"

            stats_list.append(
                LabelCentralityStats(
                    label=label_str,
                    count=count,
                    avg_score=avg_score,
                    max_score=max_score,
                ),
            )

    except Exception as error:
        logger.error(f"GDS Execution Error (Average Centrality): {error}")
        return None

    finally:
        try:
            cleanup_query: str = (
                f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName"
            )
            session.run_query(cleanup_query)
        except Exception as cleanup_error:
            logger.error(f"Failed to drop GDS graph memory: {cleanup_error}")

    if len(stats_list) > 0:
        return stats_list
    return None
