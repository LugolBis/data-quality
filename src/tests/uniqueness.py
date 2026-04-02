from typing import TYPE_CHECKING

from quality.uniqueness import duplicate_nodes, duplicate_relationships
from utils.utils import some

if TYPE_CHECKING:
    from driver.neo4j_driver import Neo4jSession


def main(session: Neo4jSession) -> None:
    duplicates_rels = duplicate_relationships(session)
    duplicates_nodes = duplicate_nodes(session, "Person", 0.6)

    if some(duplicates_rels):
        print("\n")
        print(f"Found the following duplicates of relationships :\n{duplicates_rels}")

    if some(duplicates_nodes):
        print("\n")
        print(f"Found the following duplicates of nodes :\n{duplicates_nodes}")
