from typing import Optional
from neo4j import Record, Result
from driver.neo4j_driver import Neo4jSession
from quality.types import AnomalyDetail, FeatureMismatchReport
from utils.utils import logger


def detect_label_anomalies_by_features(
    session: Neo4jSession, similarity_threshold: float = 0.85
) -> Optional[list[FeatureMismatchReport]]:
    """
    Transform relationships into nodes, extract topological features (FastRP),
    and use KNN to find nodes with highly similar features but DIFFERENT labels.
    Uses '__entity' to strictly separate original Nodes from Relationships.

    :param session: Neo4jSession instance.
    :param similarity_threshold: Minimum KNN similarity to be considered a match.
    :return: A report of mismatched entities.
    """
    graph_name = "feature_comparison_graph"
    anomalies_list: list[AnomalyDetail] = []

    try:
        session.run_query(
            "MATCH (n) WHERE NOT '__RelationshipNode__' IN labels(n) "
            "SET n.__entity = 'NODE'"
        )

        session.run_query(
            "MATCH (a)-[r]->(b) "
            "WHERE type(r) <> '__TEMP_OUT__' AND type(r) <> '__TEMP_IN__' "
            "CREATE (rn:__RelationshipNode__ { "
            "    __entity: 'RELATIONSHIP', "
            "    __original_type: type(r), "
            "    __rel_id: elementId(r) "
            "}) "
            "CREATE (a)-[:__TEMP_OUT__]->(rn) "
            "CREATE (rn)-[:__TEMP_IN__]->(b)"
        )

        session.run_query(f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName")

        session.run_query(
            f"CALL gds.graph.project('{graph_name}', '*', ['__TEMP_OUT__', '__TEMP_IN__']) YIELD graphName"
        )

        session.run_query(f"""
            CALL gds.fastRP.mutate('{graph_name}', {{
                embeddingDimension: 64,
                randomSeed: 42,
                mutateProperty: 'embedding'
            }}) YIELD nodePropertiesWritten
        """)

        knn_query = f"""
        CALL gds.knn.stream('{graph_name}', {{
            nodeProperties: ['embedding'],
            topK: 5,
            sampleRate: 1.0,
            deltaThreshold: 0.0
        }})
        YIELD node1, node2, similarity
        WITH gds.util.asNode(node1) AS n1, gds.util.asNode(node2) AS n2, similarity
        WHERE similarity >= {similarity_threshold}
          AND n1.__entity = n2.__entity 
          AND elementId(n1) < elementId(n2)
        
        WITH n1, n2, similarity,
             CASE WHEN n1.__entity = 'NODE' THEN labels(n1) ELSE [n1.__original_type] END AS l1,
             CASE WHEN n2.__entity = 'NODE' THEN labels(n2) ELSE [n2.__original_type] END AS l2
        
        RETURN n1.__entity AS entity_type,
               l1 AS labels1, l2 AS labels2,
               CASE WHEN n1.__entity = 'NODE' THEN elementId(n1) ELSE n1.__rel_id END AS id1,
               CASE WHEN n2.__entity = 'NODE' THEN elementId(n2) ELSE n2.__rel_id END AS id2,
               similarity
        ORDER BY similarity DESC
        """
        result: Result = session.run_query(knn_query)

        for record in result:
            entity_type = record["entity_type"]
            similarity = float(record["similarity"])
            id1 = str(record["id1"])
            id2 = str(record["id2"])

            labels1_str = (
                "&".join(sorted(record["labels1"]))
                if record["labels1"]
                else "UNLABELED"
            )
            labels2_str = (
                "&".join(sorted(record["labels2"]))
                if record["labels2"]
                else "UNLABELED"
            )

            if labels1_str == labels2_str:
                continue

            anomalies_list.append(
                AnomalyDetail(
                    entity_type=entity_type,
                    similarity=similarity,
                    id1=id1,
                    labels1=labels1_str,
                    id2=id2,
                    labels2=labels2_str,
                )
            )

    except Exception as error:
        logger.error(f"Feature Comparison Error: {error}")
        return None

    finally:
        try:
            session.run_query(
                f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName"
            )

            session.run_query("MATCH (rn:__RelationshipNode__) DETACH DELETE rn")

            session.run_query(
                "MATCH (n) WHERE n.__entity IS NOT NULL REMOVE n.__entity"
            )
        except Exception as cleanup_error:
            logger.error(f"Failed during cleanup: {cleanup_error}")

    if len(anomalies_list) > 0:
        return [
            FeatureMismatchReport(
                threshold=similarity_threshold,
                total_anomalies=len(anomalies_list),
                anomalies=anomalies_list,
            )
        ]
    else:
        return None
