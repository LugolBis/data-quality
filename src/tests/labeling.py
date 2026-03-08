from typing import TYPE_CHECKING

from quality.labeling import detect_label_anomalies_by_features
from utils.utils import some

if TYPE_CHECKING:
    from driver.neo4j_driver import Neo4jSession
    from quality.types import FeatureMismatchReport


def main(session: Neo4jSession) -> None:
    mismatch_reports: list[FeatureMismatchReport] | None = (
        detect_label_anomalies_by_features(
            session,
            similarity_threshold=0.90,
            property_ratio=0.5,
        )
    )

    if some(mismatch_reports):
        print("\nREPORT: Entities with Similar Features but Different Labels")
        for report in mismatch_reports:
            print(report)
    else:
        print(
            "\nNO ANOMALIES DETECTED: All entities have consistent labels with their features.",
        )
