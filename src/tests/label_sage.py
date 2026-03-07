from typing import Optional
from datetime import datetime

from driver.neo4j_driver import Neo4jSession
from quality.types import FeatureMismatchReport
from utils.utils import some, logger

from quality.label_sage import (
    train_and_store_graphsage_model,
    detect_anomalies_with_pretrained_model,
)


def main(session: Neo4jSession) -> None:
    current_time = datetime.now().strftime("%Y%m%d_%H%M")
    current_model_name = f"anomaly_graphsage_{current_time}"

    logger.info(f"=== Starting GraphSAGE Anomaly Detection Pipeline ===")
    logger.info(f"Target Model Name: {current_model_name}")

    is_trained = train_and_store_graphsage_model(
        session=session, model_name=current_model_name, epochs=10, sample_sizes=[25, 10]
    )

    if not is_trained:
        logger.error("Model training failed. Aborting anomaly detection.")
        return

    mismatch_reports: Optional[list[FeatureMismatchReport]] = (
        detect_anomalies_with_pretrained_model(
            session=session, model_name=current_model_name, similarity_threshold=0.90
        )
    )

    if some(mismatch_reports):
        print(
            f"\nREPORT: Entities with Similar GraphSAGE Features but Different Labels"
        )
        print(f"[Model Used: {current_model_name}]\n")
        for report in mismatch_reports:
            print(report)
    else:
        print(
            f"\nNO ANOMALIES DETECTED: All entities have consistent labels with their features. "
            f"(Model: {current_model_name})"
        )
