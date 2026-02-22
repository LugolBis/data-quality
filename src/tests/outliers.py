from typing import Optional

from driver.neo4j_driver import Neo4jSession
from quality.outlier import (
    detecter_outliers_numeriques,
    measure_eigenvector_centrality,
    measure_average_centrality_by_label,
)
from quality.types import NumericalOutlier, CentralityScore, LabelCentralityStats
from utils.utils import some


def main(session: Neo4jSession) -> None:
    """
    Exécute les analyses avancées : détection d'outliers numériques
    """
    outliers_numeriques: Optional[list[NumericalOutlier]] = (
        detecter_outliers_numeriques(session, z_score_threshold=1.96)
    )

    centralite_eigenvector: Optional[list[CentralityScore]] = (
        measure_eigenvector_centrality(session)
    )

    centralite_moyenne_par_label: Optional[list[LabelCentralityStats]] = (
        measure_average_centrality_by_label(session)
    )

    if some(outliers_numeriques):
        print("\nNUMERICAL OUTLIERS")
        print("\n\n".join([outlier.__repr__() for outlier in outliers_numeriques]))
    else:
        print("No numerical outliers detected.")

    if some(centralite_eigenvector):
        print("\nCENTRALITY OUTLIERS")
        print("\n\n".join([score.__repr__() for score in centralite_eigenvector]))
    else:
        print("No centrality outliers detected.")

    if some(centralite_moyenne_par_label):
        print("\nAVERAGE CENTRALITY PER LABEL")
        print("\n\n".join([stats.__repr__() for stats in centralite_moyenne_par_label]))
    else:
        print("No average centrality per label detected.")
