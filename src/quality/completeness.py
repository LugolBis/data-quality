from typing import Optional

from neo4j import Record, Result

from driver.neo4j_driver import Neo4jSession
from quality.enums import ComponentAlgo
from quality.types import (
    CircularComponentsReport,
    ComponentDetail,
    IsolatedComponentsReport,
)
from utils.utils import logger


def measure_wcc(
    session: Neo4jSession,
    min_size: int = 1,
) -> Optional[list[IsolatedComponentsReport]]:
    """
    Measure Weakly Connected Components (WCC) in the graph using GDS.\n
    Useful for finding isolated islands/fragments of data.

    :param session: A `Neo4jSession` to query the database.
    :type session: Neo4jSession
    :param min_size: The minimum number of nodes a component must have to be included in the details (default is 2).
    :type min_size: int
    :return: A report containing global stats and details of components exceeding the min_size.
    :rtype: list[IsolatedComponentsReport] | None
    """
    graph_name: str = "quality_analysis_wcc"

    try:
        session.run_query(f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName")
        session.run_query(
            f"CALL gds.graph.project('{graph_name}', '*', '*') YIELD graphName"
        )

        query: str = (
            f"CALL gds.wcc.stream('{graph_name}') "
            "YIELD nodeId, componentId "
            "WITH componentId, count(nodeId) AS size "
            "ORDER BY size DESC "
            "WITH collect({id: componentId, size: size}) AS all_components "
            "RETURN size(all_components) AS total_components, "
            "       reduce(s = 0, c IN all_components | s + c.size) AS total_nodes, "
            f"       [c IN all_components WHERE c.size = {min_size}] AS filtered_components "
        )

        result: Result = session.run_query(query)  # type: ignore
        record: Optional[Record] = result.single()

        if record:
            filtered_comps: list[ComponentDetail] = [
                ComponentDetail(component_id=c["id"], size=c["size"])
                for c in record["filtered_components"]
            ]

            return [
                IsolatedComponentsReport(
                    algorithm=ComponentAlgo("WCC"),
                    total_components=record["total_components"],
                    total_nodes=record["total_nodes"],
                    largest_components=filtered_comps,
                )
            ]

    except Exception as error:
        logger.error(f"GDS Execution Error (WCC): {error}")
        return None

    finally:
        try:
            session.run_query(
                f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName"
            )
        except Exception as cleanup_error:
            logger.error(f"Failed to drop WCC graph memory: {cleanup_error}")

    return None


def measure_scc(
    session: Neo4jSession,
    min_size: int = 2,
) -> Optional[list[CircularComponentsReport]]:
    """
    Measure Strongly Connected Components (SCC) in the graph using GDS.\n
    Useful for finding cyclic dependencies (loops) in directional relationships.

    :param session: A `Neo4jSession` to query the database.
    :type session: Neo4jSession
    :param min_size: The minimum number of nodes a component must have to be included in the details (default is 2).
    :type min_size: int
    :return: A report containing global stats and details of components exceeding the min_size.
    :rtype: list[CircularComponentsReport] | None
    """
    graph_name: str = "quality_analysis_scc"

    try:
        session.run_query(f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName")
        session.run_query(
            f"CALL gds.graph.project('{graph_name}', '*', '*') YIELD graphName"
        )

        query: str = (
            f"CALL gds.scc.stream('{graph_name}') "
            "YIELD nodeId, componentId "
            "WITH componentId, count(nodeId) AS size "
            "ORDER BY size DESC "
            "WITH collect({id: componentId, size: size}) AS all_components "
            "RETURN size(all_components) AS total_components, "
            "       reduce(s = 0, c IN all_components | s + c.size) AS total_nodes, "
            f"       [c IN all_components WHERE c.size >= {min_size}] AS filtered_components "
        )

        result: Result = session.run_query(query)  # type: ignore
        record: Optional[Record] = result.single()

        if record:
            filtered_comps: list[ComponentDetail] = [
                ComponentDetail(component_id=c["id"], size=c["size"])
                for c in record["filtered_components"]
            ]

            return [
                CircularComponentsReport(
                    algorithm=ComponentAlgo("SCC"),
                    total_components=record["total_components"],
                    total_nodes=record["total_nodes"],
                    largest_components=filtered_comps,
                )
            ]

    except Exception as error:
        logger.error(f"GDS Execution Error (SCC): {error}")
        return None

    finally:
        try:
            session.run_query(
                f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName"
            )
        except Exception as cleanup_error:
            logger.error(f"Failed to drop SCC graph memory: {cleanup_error}")

    return None
