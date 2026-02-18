from typing import Optional

from driver.neo4j_driver import Neo4jSession
from quality.lisibility import check_multigraph_edges, distr_node_degree
from quality.types import MultiGraphEdges, NodeDegrees
from utils.utils import some


def main(session: Neo4jSession) -> None:
    degrees: Optional[list[NodeDegrees]] = distr_node_degree(session)
    edges: Optional[list[MultiGraphEdges]] = check_multigraph_edges(session)

    if some(degrees):
        print("\n".join([d.__repr__() for d in degrees]))

    if some(edges):
        print("\n".join([e.__repr__() for e in edges]))
