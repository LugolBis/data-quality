from typing import TYPE_CHECKING

from profiling.lisibility import (
    check_multigraph_edges,
    compute_graph_eccentricity,
    distr_node_degree,
)
from utils.utils import some

if TYPE_CHECKING:
    from driver.neo4j_driver import Neo4jSession
    from profiling.types import Eccentricity, MultiGraphEdges, NodeDegrees


def main(session: Neo4jSession) -> None:
    degrees: list[NodeDegrees] | None = distr_node_degree(session)
    edges: list[MultiGraphEdges] | None = check_multigraph_edges(session)
    eccentricity: Eccentricity = compute_graph_eccentricity(session)

    if some(degrees):
        print("\n".join([d.__repr__() for d in degrees]))

    if some(edges):
        print("\n".join([e.__repr__() for e in edges]))

    print(f"Graph eccentricity : {eccentricity}")
