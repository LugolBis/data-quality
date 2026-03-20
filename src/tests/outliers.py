from typing import TYPE_CHECKING

from profiling.outlier import (
    detecter_outliers_numeriques,
    measure_average_centrality_by_label,
    measure_eigenvector_centrality,
)
from utils.utils import some

if TYPE_CHECKING:
    from driver.neo4j_driver import Neo4jSession
    from quality.types import CentralityScore, LabelCentralityStats, NumericalOutlier


def main(session: Neo4jSession) -> None:
    """
    Exécute les analyses avancées : détection d'outliers numériques
    """
    outliers_numeriques: list[NumericalOutlier] | None = detecter_outliers_numeriques(
        session,
        z_score_threshold=1.96,
    )

    centralite_eigenvector: list[CentralityScore] | None = (
        measure_eigenvector_centrality(session, epsilon=0.5)
    )

    centralite_moyenne_par_label: list[LabelCentralityStats] | None = (
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
