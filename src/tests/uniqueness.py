from typing import TYPE_CHECKING

from quality.uniqueness import duplicate_relationships
from utils.utils import some

if TYPE_CHECKING:
    from driver.neo4j_driver import Neo4jSession


def main(session: Neo4jSession) -> None:
    duplicates_rels = duplicate_relationships(session)

    if some(duplicates_rels):
        print("\n")
        print(f"Found the following duplicates of relationships :\n{duplicates_rels}")
