from typing import TYPE_CHECKING

from profiling.integrity import distr_nodes_properties, distr_relationships_properties
from quality.integrity import (
    detecter_doublons_node,
    detecter_doublons_relationships,
)
from utils.utils import some

if TYPE_CHECKING:
    from driver.neo4j_driver import Neo4jSession
    from profiling.types import EntityStats
    from quality.types import TextSimilarity


def main(session: Neo4jSession) -> None:
    properties: list[EntityStats] | None = distr_nodes_properties(session)

    similarities_node: list[TextSimilarity] | None = detecter_doublons_node(
        session,
        seuil_similarite=0.9,
    )

    relationships: list[EntityStats] | None = distr_relationships_properties(session)

    similarities_relationships: list[TextSimilarity] | None = (
        detecter_doublons_relationships(
            session,
            seuil_similarite=0.9,
        )
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
