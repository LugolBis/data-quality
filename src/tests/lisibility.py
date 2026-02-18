from typing import Optional

from driver.neo4j_driver import Neo4jSession
from quality.lisibility import distr_node_degree
from quality.types import NodeDegrees
from utils.utils import some


def main(session: Neo4jSession) -> None:
    degrees: Optional[list[NodeDegrees]] = distr_node_degree(session)

    if some(degrees):
        print("\n".join([d.__repr__() for d in degrees]))
