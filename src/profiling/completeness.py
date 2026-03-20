from typing import TYPE_CHECKING

from profiling.enums import ComponentAlgo
from profiling.types import (
    CircularComponentsReport,
    ComponentDetail,
    IsolatedComponentsReport,
)
from utils.utils import logger

if TYPE_CHECKING:
    from neo4j import Record, Result

    from driver.neo4j_driver import Neo4jSession


def measure_wcc(
    session: Neo4jSession,
    min_size: int = 1,
) -> list[IsolatedComponentsReport] | None:
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
            f"CALL gds.graph.project('{graph_name}', '*', '*') YIELD graphName",
        )

        query: str = (
            f"CALL gds.wcc.stream('{graph_name}') "
            "YIELD nodeId, componentId "
            "WITH componentId, count(nodeId) AS size, collect(gds.util.asNode(nodeId))[0..3] AS sample_nodes "
            "ORDER BY size DESC "
            "WITH collect({id: componentId, size: size, samples: sample_nodes}) AS all_components "
            "RETURN size(all_components) AS total_components, "
            "       reduce(s = 0, c IN all_components | s + c.size) AS total_nodes, "
            f"       [c IN all_components WHERE c.size = {min_size}] AS filtered_components "
        )

        result: Result = session.run_query(query)  # ty:ignore[invalid-argument-type]
        record: Record | None = result.single()

        if record:
            filtered_comps: list[ComponentDetail] = []

            for c in record["filtered_components"]:
                samples: list[str] = []
                for node in c["samples"]:
                    labels_str = (
                        "&".join(list(node.labels)) if node.labels else "UNLABELED"
                    )
                    name_str = str(
                        node.get("name")
                        or node.get("title")
                        or node.get("id")
                        or "<NoName>",
                    )
                    samples.append(f"(:{labels_str} {{name: '{name_str}'}})")

                filtered_comps.append(
                    ComponentDetail(
                        component_id=c["id"],
                        size=c["size"],
                        sample_nodes=samples,
                    ),
                )

            return [
                IsolatedComponentsReport(
                    algorithm=ComponentAlgo("WCC"),
                    total_components=record["total_components"],
                    total_nodes=record["total_nodes"],
                    largest_components=filtered_comps,
                ),
            ]

    except Exception as error:
        logger.error(f"GDS Execution Error (WCC): {error}")
        return None

    finally:
        try:
            session.run_query(
                f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName",
            )
        except Exception as cleanup_error:
            logger.error(f"Failed to drop WCC graph memory: {cleanup_error}")

    return None


def measure_scc(
    session: Neo4jSession,
    min_size: int = 2,
) -> list[CircularComponentsReport] | None:
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
            f"CALL gds.graph.project('{graph_name}', '*', '*') YIELD graphName",
        )

        query: str = (
            f"CALL gds.scc.stream('{graph_name}') "
            "YIELD nodeId, componentId "
            "WITH componentId, count(nodeId) AS size, collect(gds.util.asNode(nodeId))[0..3] AS sample_nodes "
            "ORDER BY size DESC "
            "WITH collect({id: componentId, size: size, samples: sample_nodes}) AS all_components "
            "RETURN size(all_components) AS total_components, "
            "       reduce(s = 0, c IN all_components | s + c.size) AS total_nodes, "
            f"       [c IN all_components WHERE c.size >= {min_size}] AS filtered_components "
        )

        result: Result = session.run_query(query)  # ty:ignore[invalid-argument-type]
        record: Record | None = result.single()

        if record:
            filtered_comps: list[ComponentDetail] = []

            for c in record["filtered_components"]:
                samples: list[str] = []
                for node in c["samples"]:
                    labels_str = (
                        "&".join(list(node.labels)) if node.labels else "UNLABELED"
                    )
                    name_str = str(
                        node.get("name")
                        or node.get("title")
                        or node.get("id")
                        or "<NoName>",
                    )
                    samples.append(f"(:{labels_str} {{name: '{name_str}'}})")

                filtered_comps.append(
                    ComponentDetail(
                        component_id=c["id"],
                        size=c["size"],
                        sample_nodes=samples,
                    ),
                )

            return [
                CircularComponentsReport(
                    algorithm=ComponentAlgo("SCC"),
                    total_components=record["total_components"],
                    total_nodes=record["total_nodes"],
                    largest_components=filtered_comps,
                ),
            ]

    except Exception as error:
        logger.error(f"GDS Execution Error (SCC): {error}")
        return None

    finally:
        try:
            session.run_query(
                f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName",
            )
        except Exception as cleanup_error:
            logger.error(f"Failed to drop SCC graph memory: {cleanup_error}")

    return None
