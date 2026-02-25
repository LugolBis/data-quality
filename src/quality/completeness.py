from typing import Optional

from neo4j import Record, Result

from driver.neo4j_driver import Neo4jSession
from quality.types import ComponentDetail, ConnectedComponentsReport
from utils.utils import logger


def measure_wcc(session: Neo4jSession) -> Optional[ConnectedComponentsReport]:
    """
    Measure Weakly Connected Components (WCC) in the graph using GDS.\n
    Useful for finding isolated islands/fragments of data.

    :param session: A `Neo4jSession` to query the database.
    :type session: Neo4jSession
    :return: A report containing the total number of components and the sizes of the largest ones.
    :rtype: ConnectedComponentsReport | None
    """
    graph_name: str = "quality_analysis_wcc"

    try:
        session.run_query(f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName")
        session.run_query(f"CALL gds.graph.project('{graph_name}', '*', '*') YIELD graphName")

        query: str = (
            f"CALL gds.wcc.stream('{graph_name}') "
            "YIELD nodeId, componentId "
            "WITH componentId, count(nodeId) AS size "
            "ORDER BY size DESC "
            "WITH collect({id: componentId, size: size}) AS all_components "
            "RETURN size(all_components) AS total_components, "
            "       reduce(s = 0, c IN all_components | s + c.size) AS total_nodes, "
            "       all_components[0..10] AS top_components "
        )

        result: Result = session.run_query(query)
        record: Optional[Record] = result.single()

        if record:
            top_comps: list[ComponentDetail] = [
                ComponentDetail(component_id=c["id"], size=c["size"])
                for c in record["top_components"]
            ]
            
            return ConnectedComponentsReport(
                algorithm="WCC (Weakly Connected Components)",
                total_components=record["total_components"],
                total_nodes=record["total_nodes"],
                largest_components=top_comps,
            )

    except Exception as error:
        logger.error(f"GDS Execution Error (WCC): {error}")
        return None

    finally:
        try:
            session.run_query(f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName")
        except Exception as cleanup_error:
            logger.error(f"Failed to drop WCC graph memory: {cleanup_error}")

    return None


def measure_scc(session: Neo4jSession) -> Optional[ConnectedComponentsReport]:
    """
    Measure Strongly Connected Components (SCC) in the graph using GDS.\n
    Useful for finding cyclic dependencies (loops) in directional relationships.

    :param session: A `Neo4jSession` to query the database.
    :type session: Neo4jSession
    :return: A report containing the total number of strongly connected components.
    :rtype: ConnectedComponentsReport | None
    """
    graph_name: str = "quality_analysis_scc"

    try:
        session.run_query(f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName")
        session.run_query(f"CALL gds.graph.project('{graph_name}', '*', '*') YIELD graphName")

        query: str = (
            f"CALL gds.scc.stream('{graph_name}') "
            "YIELD nodeId, componentId "
            "WITH componentId, count(nodeId) AS size "
            "ORDER BY size DESC "
            "WITH collect({id: componentId, size: size}) AS all_components "
            "RETURN size(all_components) AS total_components, "
            "       reduce(s = 0, c IN all_components | s + c.size) AS total_nodes, "
            "       all_components[0..10] AS top_components "
        )

        result: Result = session.run_query(query)
        record: Optional[Record] = result.single()

        if record:
            top_comps: list[ComponentDetail] = [
                ComponentDetail(component_id=c["id"], size=c["size"])
                for c in record["top_components"]
            ]
            
            return ConnectedComponentsReport(
                algorithm="SCC (Strongly Connected Components)",
                total_components=record["total_components"],
                total_nodes=record["total_nodes"],
                largest_components=top_comps,
            )

    except Exception as error:
        logger.error(f"GDS Execution Error (SCC): {error}")
        return None

    finally:
        try:
            session.run_query(f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName")
        except Exception as cleanup_error:
            logger.error(f"Failed to drop SCC graph memory: {cleanup_error}")

    return None