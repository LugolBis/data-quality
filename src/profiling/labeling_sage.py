from typing import TYPE_CHECKING

from models.utils import format_label
from profiling.types import AnomalyDetail, FeatureMismatchReport
from utils.utils import logger

if TYPE_CHECKING:
    from neo4j import Result

    from driver.neo4j_driver import Neo4jSession


def _setup_and_project_graph(
    session: Neo4jSession,
    graph_name: str,
    max_categories: int = 100,
) -> list[str]:
    schema_query = """
    CALL db.schema.nodeTypeProperties() YIELD propertyName, propertyTypes
    UNWIND propertyTypes AS t
    WITH propertyName, collect(DISTINCT t) AS uniqueTypes
    WHERE NOT propertyName IN ['__entity', '__original_type', '__rel_id', 'embedding', 'id', 'name']
    RETURN propertyName, uniqueTypes
    """
    schema_result = session.run_query(schema_query)

    numeric_props = []
    string_props = []

    if schema_result:
        for record in schema_result:
            prop = record["propertyName"]
            types = record["uniqueTypes"]
            if any(t in ["Long", "Double", "Integer", "Float"] for t in types):
                numeric_props.append(prop)
            elif "String" in types:
                string_props.append(prop)

    logger.info(f"Detected Numeric properties: {numeric_props}")
    logger.info(f"Detected String properties: {string_props}")

    session.run_query(
        "MATCH (n) WHERE NOT '__RelationshipNode__' IN labels(n) SET n.__entity = 'NODE'",
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
        "CREATE (rn)-[:__TEMP_IN__]->(b)",
    )

    return_clauses = ["id(n) AS id", "[n.__entity] AS labels"]
    final_feature_names = []

    for prop in numeric_props:
        return_clauses.append(f"coalesce(toFloat(n.`{prop}`), 0.0) AS `{prop}`")
        final_feature_names.append(prop)

    for prop in string_props:
        distinct_query = (
            "MATCH (n) "
            f"WHERE n.`{prop}` IS NOT NULL "
            f"RETURN DISTINCT n.`{prop}` AS val "
            f"LIMIT {max_categories + 1}"
        )
        distinct_vals = [
            r["val"]
            for r in session.run_query(distinct_query)  # ty:ignore[invalid-argument-type]
            if r["val"] is not None
        ]

        if len(distinct_vals) == 0 or len(distinct_vals) > max_categories:
            logger.warning(
                f"Skipping string property '{prop}' (categories: {len(distinct_vals)}). Exceeds limit {max_categories} or is empty.",
            )
            continue

        encoded_prop_name = f"{prop}_encoded"
        case_stmts = [f"CASE n.`{prop}`"]

        for i, val in enumerate(distinct_vals):
            one_hot = [0.0] * len(distinct_vals)
            one_hot[i] = 1.0
            safe_val = str(val).replace("'", "\\'")
            case_stmts.append(f"  WHEN '{safe_val}' THEN {one_hot}")

        default_array = [0.0] * len(distinct_vals)
        case_stmts.append(f"  ELSE {default_array}")
        case_stmts.append(f"END AS `{encoded_prop_name}`")

        return_clauses.append("\n".join(case_stmts))
        final_feature_names.append(encoded_prop_name)
        logger.info(
            f"Encoded String property '{prop}' into {len(distinct_vals)}-dim array: {encoded_prop_name}",
        )

    session.run_query(f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName")  # ty:ignore[invalid-argument-type]

    node_query = f"""
    MATCH (n) WHERE n.__entity IS NOT NULL
    RETURN {", ".join(return_clauses)}
    """

    rel_query = """
    MATCH (n)-[r]->(m)
    WHERE type(r) IN ['__TEMP_OUT__', '__TEMP_IN__']
    RETURN id(n) AS source, id(m) AS target, type(r) AS type
    """

    project_query = f"""
    CALL gds.graph.project.cypher(
        '{graph_name}',
        "{node_query}",
        "{rel_query}"
    ) YIELD graphName, nodeCount, relationshipCount
    """

    session.run_query(project_query)  # ty:ignore[invalid-argument-type]
    logger.info(
        f"Graph projected successfully with combined features: {final_feature_names}",
    )

    return final_feature_names


def _cleanup_graph_and_temp_data(session: Neo4jSession, graph_name: str):
    try:
        session.run_query(f"CALL gds.graph.drop('{graph_name}', false) YIELD graphName")  # ty:ignore[invalid-argument-type]
        session.run_query("MATCH (rn:__RelationshipNode__) DETACH DELETE rn")
        session.run_query("MATCH (n) WHERE n.__entity IS NOT NULL REMOVE n.__entity")
    except Exception as cleanup_error:
        logger.error(f"Failed during cleanup: {cleanup_error}")


def train_and_store_graphsage_model(
    session: Neo4jSession,
    model_name: str = "anomaly_graphsage_model",
    epochs: int = 10,
    sample_sizes: list[int] = [25, 10],
) -> bool:
    graph_name = "train_feature_graph"

    try:
        logger.info(
            f"Preparing data and projecting graph '{graph_name}' for training...",
        )
        numeric_properties = _setup_and_project_graph(session, graph_name)

        session.run_query(f"CALL gds.model.drop('{model_name}', false) YIELD modelInfo")  # ty:ignore[invalid-argument-type]

        sample_sizes_str = "[" + ", ".join(map(str, sample_sizes)) + "]"
        train_config_lines = [
            f"modelName: '{model_name}'",
            "embeddingDimension: 64",
            "randomSeed: 42",
            f"epochs: {epochs}",
            f"sampleSizes: {sample_sizes_str}",
            "aggregator: 'MEAN'",
        ]

        if numeric_properties:
            props_list_str = (
                "[" + ", ".join([f"'{p}'" for p in numeric_properties]) + "]"
            )
            train_config_lines.append(f"featureProperties: {props_list_str}")
            train_config_lines.append("projectedFeatureDimension: 32")

        train_config_cypher = "{" + ", ".join(train_config_lines) + "}"

        logger.info(f"Training GraphSAGE model '{model_name}'...")
        session.run_query(f"""
            CALL gds.beta.graphSage.train('{graph_name}', {train_config_cypher}) 
            YIELD modelInfo
        """)  # ty:ignore[invalid-argument-type]

        logger.info(f"Storing model '{model_name}' to disk...")
        session.run_query(
            f"CALL gds.model.store('{model_name}') YIELD modelName, storeMillis",  # ty:ignore[invalid-argument-type]
        )
        logger.info(f"Model '{model_name}' successfully trained and stored.")
        return True

    except Exception as error:
        logger.error(f"Model Training Error: {error}")
        return False

    finally:
        _cleanup_graph_and_temp_data(session, graph_name)


def detect_anomalies_with_pretrained_model(
    session: Neo4jSession,
    model_name: str = "anomaly_graphsage_model",
    similarity_threshold: float = 0.85,
) -> list[FeatureMismatchReport] | None:
    graph_name = "inference_feature_graph"
    anomalies_list: list[AnomalyDetail] = []

    try:
        logger.info("Preparing data and projecting graph for inference...")
        _setup_and_project_graph(session, graph_name)

        check_model_query = (
            f"CALL gds.model.exists('{model_name}') YIELD exists RETURN exists"
        )
        exists_result = session.run_query(check_model_query)  # ty:ignore[invalid-argument-type]

        is_in_memory = False
        if exists_result:
            for record in exists_result:
                is_in_memory = record["exists"]
                break

        if not is_in_memory:
            logger.info(f"Loading model '{model_name}' from disk to memory...")
            session.run_query(
                f"CALL gds.model.load('{model_name}') YIELD modelName, loadMillis",  # ty:ignore[invalid-argument-type]
            )

        logger.info("Mutating graph with GraphSAGE embeddings...")
        session.run_query(f"""
            CALL gds.beta.graphSage.mutate('{graph_name}', {{
                modelName: '{model_name}',
                mutateProperty: 'embedding'
            }}) YIELD nodePropertiesWritten
        """)  # ty:ignore[invalid-argument-type]

        logger.info("Running KNN similarity stream...")
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
        
        RETURN n1.__entity AS entity_type, l1 AS labels1, l2 AS labels2,
               CASE WHEN n1.__entity = 'NODE' THEN elementId(n1) ELSE n1.__rel_id END AS id1,
               CASE WHEN n2.__entity = 'NODE' THEN elementId(n2) ELSE n2.__rel_id END AS id2,
               similarity
        ORDER BY similarity DESC
        """
        result: Result = session.run_query(knn_query)  # ty:ignore[invalid-argument-type]

        for record in result:
            entity_type = record["entity_type"]
            similarity = float(record["similarity"])
            labels1_str = (
                format_label(record["labels1"]) if record["labels1"] else "UNLABELED"
            )
            labels2_str = (
                format_label(record["labels2"]) if record["labels2"] else "UNLABELED"
            )

            if labels1_str == labels2_str:
                continue

            anomalies_list.append(
                AnomalyDetail(
                    entity_type=entity_type,
                    similarity=similarity,
                    id1=str(record["id1"]),
                    labels1=labels1_str,
                    id2=str(record["id2"]),
                    labels2=labels2_str,
                ),
            )

    except Exception as error:
        logger.error(f"Anomaly Detection Error: {error}")
        return None

    finally:
        _cleanup_graph_and_temp_data(session, graph_name)
    if len(anomalies_list) > 0:
        return [
            FeatureMismatchReport(
                threshold=similarity_threshold,
                total_anomalies=len(anomalies_list),
                anomalies=anomalies_list,
            ),
        ]
    return None
