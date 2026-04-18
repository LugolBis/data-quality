import re
from typing import TYPE_CHECKING

from quality.enums import LabelAction
from quality.types import LabelErr
from utils.utils import logger, some

if TYPE_CHECKING:
    from neo4j import Result

    from driver.neo4j_driver import Neo4jSession

# Step - 1
_TOKENIZATION: str = """
    MATCH (n)-[r]-(m)
    WITH n,
    CASE WHEN startNode(r) = n THEN 'OUT:' ELSE 'IN:' END
    + type(r) + ':' +
    CASE size(labels(m)) WHEN 0 THEN 'UNLABELLED'
        ELSE apoc.text.join(apoc.coll.sort(labels(m)), '')
    END AS triplet
    WITH n, apoc.coll.sort(
        apoc.coll.toSet(collect(triplet))
    ) AS tokens
    SET n.___Tokens = tokens
    RETURN count(n) AS nodesIndexed;
"""

# Step - 2.a
_TOKENS_CREATION: str = """
    MATCH (n)
    WHERE n.___Tokens IS NOT null
    WITH apoc.coll.toSet(
        apoc.coll.flatten(collect(n.___Tokens))
    ) AS vocab
    UNWIND range(0, size(vocab)-1) AS i
    MERGE (v:___Token { value: vocab[i], id: i })
    RETURN count(v) AS tokensCreated;
"""

# Step - 2.b
_TOKENS_SIM: str = """
    MATCH (t1:___Token), (t2:___Token)
    WHERE id(t1) < id(t2)
    WITH t1, t2,
        round(apoc.text.levenshteinSimilarity(t1.value, t2.value), 4) AS sim
    WHERE sim > 0
    MERGE (t1)-[r:___SIMILAR_TO]->(t2)
    SET r.score = sim
    RETURN count(r) AS similarityRelationshipsCreated;
"""

# Step - 3
_ANALYSIS: str = """
    MATCH (n1), (n2)
    WHERE id(n1) < id(n2)
        AND n1.___Tokens IS NOT null
        AND n2.___Tokens IS NOT null

    WITH n1, n2,
    [l IN labels(n1) WHERE l IN labels(n2)] AS X,
    apoc.coll.toSet([l IN labels(n1) WHERE NOT l IN labels(n2)]
    + [l IN labels(n2) WHERE NOT l IN labels(n1)]) AS Y

    WITH n1, n2,
    CASE (size(X) + size(Y)) WHEN 0 THEN 0.0
        ELSE (toFloat(size(Y)) / (size(X) + size(Y)))
        END AS labels_sim

    WHERE labels_sim $TSL_OP$ $TRESHOLD_SIM_LABELS$

    UNWIND n1.___Tokens AS token1Value
    MATCH (nt1:___Token { value: token1Value })
    UNWIND n2.___Tokens AS token2Value
    MATCH (nt2:___Token { value: token2Value })
    MATCH (nt1)-[r:___SIMILAR_TO]-(nt2)

    WITH n1, n2, labels_sim,
    sum(r.score) / (toFloat(size(n1.___Tokens) + size(n2.___Tokens))) AS sim_t

    WHERE sim_t $TSK_OP$ $TRESHOLD_SIM_TOKENS$

    RETURN elementId(n1) AS ID1, elementId(n2) AS ID2, labels_sim, sim_t;
"""

_CLEANUP: tuple[str, str] = (
    "MATCH (t:___Token) DETACH DELETE t;",
    "MATCH (n) WHERE n.___Tokens IS NOT null REMOVE n.___Tokens;",
)

_TSL: str = "$TRESHOLD_SIM_LABELS$"
_TSK: str = "$TRESHOLD_SIM_TOKENS$"
_TSL_OP: str = "$TSL_OP$"
_TSK_OP: str = "$TSK_OP$"


def _analyze_labels(
    session: Neo4jSession,
    mapping: dict[str, str],
    action: LabelAction,
    tsl_op: str,
    tsk_op: str,
) -> list[LabelErr]:
    local_mapping = mapping.copy()
    local_mapping[_TSL_OP] = tsl_op
    local_mapping[_TSK_OP] = tsk_op

    pattern = re.compile("|".join(map(re.escape, local_mapping)))
    query = pattern.sub(lambda m: local_mapping[m.group(0)], _ANALYSIS)

    logger.info(query)
    result: Result = session.run_query(query)  # ty:ignore[invalid-argument-type]
    records = result.to_eager_result().records

    suggestions: list[LabelErr] = []
    for record in records:
        node_id_x = record.get("ID1")
        node_id_y = record.get("ID2")
        labels_similarity = record.get("labels_sim")
        tokens_similarity = record.get("sim_t")

        if all(
            some(value)
            for value in (node_id_x, node_id_y, labels_similarity, tokens_similarity)
        ):
            suggestions.append(
                LabelErr(
                    action,
                    labels_similarity,
                    tokens_similarity,
                    node_id_x,
                    node_id_y,
                ),
            )
        else:
            logger.error(f"Invalid record : {record}")

    return suggestions


def _merge(session: Neo4jSession, mapping: dict[str, str]) -> list[LabelErr]:
    return _analyze_labels(
        session,
        mapping,
        LabelAction.MERGE,
        tsl_op="<=",
        tsk_op=">=",
    )


def _split(session: Neo4jSession, mapping: dict[str, str]) -> list[LabelErr]:
    return _analyze_labels(
        session,
        mapping,
        LabelAction.SPLIT,
        tsl_op=">=",
        tsk_op="<=",
    )


def labeling_clustering(
    session: Neo4jSession,
    treshold_sim_labels: float,
    treshold_sim_tokens: float,
) -> list[LabelErr] | None:
    """
    :param session: A valid connection to a `Neo4jSession`.
    :type session: Neo4jSession
    :param treshold_sim_labels: Treshold of similarity between labels set.
        The value should be in [0;1].
    :type treshold_sim_labels: float
    :param treshold_sim_tokens: Treshold of similarity between tokens set.
        The value should be in [0;1].
    :type treshold_sim_tokens: float
    :raises RuntimeError: If one of the `_CLEANUP` query failed.
    """

    cleanup_error = None
    analysis: list[LabelErr] = []

    try:
        session.run_query(_TOKENIZATION)  # ty:ignore[invalid-argument-type]
        session.run_query(_TOKENS_CREATION)  # ty:ignore[invalid-argument-type]
        session.run_query(_TOKENS_SIM)  # ty:ignore[invalid-argument-type]

        mapping = {
            _TSL: str(treshold_sim_labels),
            _TSK: str(treshold_sim_tokens),
        }

        # Merge analysis :
        analysis.extend(_merge(session, mapping))

        # Split analysis :
        analysis.extend(_split(session, mapping))
    except Exception as error:
        logger.error(error)
    finally:
        try:
            for query in _CLEANUP:
                session.run_query(query)  # ty:ignore[invalid-argument-type]
        except Exception as error:
            logger.error("Cleanup failed")
            cleanup_error = error

    if cleanup_error:
        msg = "Failed to run the clean up script during labels analysis"
        raise RuntimeError(msg) from cleanup_error

    if len(analysis) > 0:
        return analysis
    return None
