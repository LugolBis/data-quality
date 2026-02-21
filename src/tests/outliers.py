from typing import Optional

from driver.neo4j_driver import Neo4jSession
from quality.outlier import detecter_outliers_numeriques, mesurer_centralite_eigenvector
from quality.types import NumericalOutlier, CentralityScore
from utils.utils import some


def main(session: Neo4jSession) -> None:
    """
    Exécute les analyses avancées : détection d'outliers numériques
    """
    outliers_numeriques: Optional[list[NumericalOutlier]] = detecter_outliers_numeriques(
        session, z_score_threshold=1.96
    )

    centralite_eigenvector: Optional[list[CentralityScore]] = mesurer_centralite_eigenvector(session)

    if some(outliers_numeriques):
        print("\nOUTLIERS NUMÉRIQUES")
        print("\n\n".join([outlier.__repr__() for outlier in outliers_numeriques]))
    else:
        print("Aucun outlier numérique détecté.")

    if some(centralite_eigenvector):
        print("\nOUTLIERS DE CENTRALITÉ")
        print("\n\n".join([score.__repr__() for score in centralite_eigenvector]))
    else:
        print("Aucun outlier de centralité détecté.")

