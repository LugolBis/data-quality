from typing import Optional

from driver.neo4j_driver import Neo4jSession
from quality.integrity import check_properties_consistency, detecter_doublons
from quality.types import LabelStats, TextSimilarity
from utils.utils import some


def main(session: Neo4jSession) -> None:
    properties: Optional[list[LabelStats]] = check_properties_consistency(session)
    similarities: Optional[list[TextSimilarity]] = detecter_doublons(
        session, seuil_similarite=0.6
    )

    if some(properties):
        print(properties)

    if some(similarities):
        print("\n")
        print("\n".join([sim.__repr__() for sim in similarities]))
