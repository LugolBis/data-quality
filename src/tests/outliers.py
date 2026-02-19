from typing import Optional

from driver.neo4j_driver import Neo4jSession
from quality.outlier import detecter_outliers_numeriques
from quality.types import NumericalOutlier
from utils.utils import some


def main(session: Neo4jSession) -> None:
    """
    Exécute les analyses avancées : détection d'outliers numériques
    """
    outliers_numeriques: Optional[list[NumericalOutlier]] = detecter_outliers_numeriques(
        session, z_score_threshold=1.96
    )

    if some(outliers_numeriques):
        print("\nOUTLIERS NUMÉRIQUES")
        print("\n\n".join([outlier.__repr__() for outlier in outliers_numeriques]))
    else:
        print("Aucun outlier numérique détecté.")


