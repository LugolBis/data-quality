from typing import Optional

from driver.neo4j_driver import Neo4jSession
from quality.integrity import (
    distr_nodes_properties,
    distr_relationships_properties,
    detecter_doublons_node,
    detecter_doublons_relationships,
)
from quality.types import EntityStats, TextSimilarity
from utils.utils import some


def main(session: Neo4jSession) -> None:
    properties: Optional[list[EntityStats]] = distr_nodes_properties(session)

    similarities_node: Optional[list[TextSimilarity]] = detecter_doublons_node(
        session, seuil_similarite=0.9
    )
    
    relationships: Optional[list[EntityStats]] = distr_relationships_properties(session)

    similarities_relationships: Optional[list[TextSimilarity]] = detecter_doublons_relationships(
        session, seuil_similarite=0.9
    )

    if some(properties):
        print(properties)

    if some(similarities_node):
        print("\n")
        print("\n".join([sim.__repr__() for sim in similarities_node]))

    if some(relationships):
        print("\n")
        print(relationships)

    if some(similarities_relationships):
        print("\n")
        print("\n".join([sim.__repr__() for sim in similarities_relationships]))
