from typing import Optional

from driver.neo4j_driver import Neo4jSession
from quality.label import detect_label_anomalies_by_features
from quality.types import FeatureMismatchReport
from utils.utils import some


def main(session: Neo4jSession) -> None:
    mismatch_reports: Optional[list[FeatureMismatchReport]] = (
        detect_label_anomalies_by_features(
            session, similarity_threshold=0.90, property_ratio=0.5
        )
    )

    if some(mismatch_reports):
        print("\nREPORT: Entities with Similar Features but Different Labels")
        for report in mismatch_reports:
            print(report)
    else:
        print(
            "\nNO ANOMALIES DETECTED: All entities have consistent labels with their features."
        )
