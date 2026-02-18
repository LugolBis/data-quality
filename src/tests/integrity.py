from typing import Optional

from driver.neo4j_driver import Neo4jSession
from quality.integrity import (
    distr_nodes_properties,
    distr_relationships_properties,
    detecter_doublons_node,
)
from quality.types import EntityStats, TextSimilarity
from utils.utils import some


def main(session: Neo4jSession) -> None:
    properties: Optional[list[EntityStats]] = distr_nodes_properties(session)
    similarities: Optional[list[TextSimilarity]] = detecter_doublons_node(
        session, seuil_similarite=0.6
    )
    relationships: Optional[list[EntityStats]] = distr_relationships_properties(session)

    if some(properties):
        print(properties)

    if some(similarities):
        print("\n")
        print("\n".join([sim.__repr__() for sim in similarities]))

    if some(relationships):
        print("\n")
        print(relationships)
