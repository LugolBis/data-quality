from datetime import datetime
from typing import TYPE_CHECKING

from profiling.labeling_sage import (
    detect_anomalies_with_pretrained_model,
    train_and_store_graphsage_model,
)
from utils.utils import logger, some

if TYPE_CHECKING:
    from driver.neo4j_driver import Neo4jSession
    from profiling.types import FeatureMismatchReport


def main(session: Neo4jSession) -> None:
    current_time = datetime.now().strftime("%Y%m%d_%H%M")
    current_model_name = f"anomaly_graphsage_{current_time}"

    logger.info("=== Starting GraphSAGE Anomaly Detection Pipeline ===")
    logger.info(f"Target Model Name: {current_model_name}")

    is_trained = train_and_store_graphsage_model(
        session=session,
        model_name=current_model_name,
        epochs=10,
        sample_sizes=[25, 10],
    )

    if not is_trained:
        logger.error("Model training failed. Aborting anomaly detection.")
        return

    mismatch_reports: list[FeatureMismatchReport] | None = (
        detect_anomalies_with_pretrained_model(
            session=session,
            model_name=current_model_name,
            similarity_threshold=0.90,
        )
    )

    if some(mismatch_reports):
        print(
            "\nREPORT: Entities with Similar GraphSAGE Features but Different Labels",
        )
        print(f"[Model Used: {current_model_name}]\n")
        for report in mismatch_reports:
            print(report)
    else:
        print(
            f"\nNO ANOMALIES DETECTED: All entities have consistent labels with their features. "
            f"(Model: {current_model_name})",
        )
