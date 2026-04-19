import re
from typing import TYPE_CHECKING

from driver.neo4j_driver import Neo4jSession
from quality.enums import LabelAction
from quality.types import LabelErr
from utils.utils import logger

if TYPE_CHECKING:
    from neo4j import Result


# Step - 1
_TOKENIZATION: str = """
    MATCH (n)-[r]-(m)
    WITH n,
    CASE WHEN startNode(r) = n THEN 'OU:' ELSE 'IN:' END
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

# Step - 3.a - Compute Monge-Elkan similarity
_ANALYSIS: str = """
    CALL apoc.periodic.iterate(
        'MATCH (n1)
         WHERE n1.___Tokens IS NOT NULL
         RETURN n1',

        'MATCH (n2)
         WHERE id(n2) > id(n1)
           AND n2.___Tokens IS NOT NULL

         WITH n1, n2,
           [l IN labels(n1) WHERE l IN labels(n2)] AS X,
           apoc.coll.toSet(
             [l IN labels(n1) WHERE NOT l IN labels(n2)]
             + [l IN labels(n2) WHERE NOT l IN labels(n1)]
           ) AS Y

         WITH n1, n2,
           CASE (size(X) + size(Y)) WHEN 0 THEN 0.0
             ELSE 1-(toFloat(size(Y)) / (size(X) + size(Y)))
           END AS labels_sim

         WHERE labels_sim $TSL_OP$ $TRESHOLD_SIM_LABELS$

         WITH n1, n2, labels_sim
         UNWIND n1.___Tokens AS t1val
         MATCH (nt1:___Token { value: t1val })
         OPTIONAL MATCH (nt1)-[r1:___SIMILAR_TO]-(nt2:___Token)
         WHERE nt2.value IN n2.___Tokens

         WITH n1, n2, labels_sim, t1val,
           CASE WHEN t1val IN n2.___Tokens THEN 1.0
                ELSE coalesce(max(r1.score), 0.0)
           END AS best_forward

         WITH n1, n2, labels_sim,
           avg(best_forward) AS me_forward

         UNWIND n2.___Tokens AS t2val
         MATCH (nt2:___Token { value: t2val })
         OPTIONAL MATCH (nt2)-[r2:___SIMILAR_TO]-(nt1b:___Token)
         WHERE nt1b.value IN n1.___Tokens

         WITH n1, n2, labels_sim, me_forward, t2val,
           CASE WHEN t2val IN n1.___Tokens THEN 1.0
                ELSE coalesce(max(r2.score), 0.0)
           END AS best_backward

         WITH n1, n2, labels_sim, me_forward,
           avg(best_backward) AS me_backward

         WITH n1, n2, labels_sim,
           (me_forward + me_backward) / 2.0 AS sim_t

         WHERE sim_t $TSK_OP$ $TRESHOLD_SIM_TOKENS$

         MERGE (n1)-[c:___$ACTION$]->(n2)
           SET c.labels_sim = labels_sim,
               c.sim_t      = sim_t',

        { batchSize: $batch_size, parallel: true }
    )
    YIELD batches, total, errorMessages
    RETURN batches, total, errorMessages;
"""

# Step - 3.b - READ suggested candidates
_READ_SUGGESTIONS: str = """
    MATCH (n1)-[c:___$ACTION$]->(n2)
    RETURN elementId(n1) AS ID1, elementId(n2) AS ID2,
           c.labels_sim AS labels_sim, c.sim_t AS sim_t;
"""

_CLEANUP: tuple[str, str, str, str] = (
    "MATCH ()-[m:___MERGE]->() DELETE m;",
    "MATCH ()-[s:___SPLIT]->() DELETE s;",
    "MATCH (t:___Token) DETACH DELETE t;",
    "MATCH (n) WHERE n.___Tokens IS NOT NULL REMOVE n.___Tokens;",
)

_TSL: str = "$TRESHOLD_SIM_LABELS$"
_TSK: str = "$TRESHOLD_SIM_TOKENS$"
_TSL_OP: str = "$TSL_OP$"
_TSK_OP: str = "$TSK_OP$"
_ACTION: str = "$ACTION$"


def _analyze_labels(
    session: Neo4jSession,
    mapping: dict[str, str],
    action: LabelAction,
    tsl_op: str,
    tsk_op: str,
    batch_size: int,
) -> list[LabelErr]:
    local_mapping = mapping.copy()
    local_mapping[_TSL_OP] = tsl_op
    local_mapping[_TSK_OP] = tsk_op
    local_mapping[_ACTION] = str(action)

    pattern = re.compile("|".join(map(re.escape, local_mapping)))
    query_write = pattern.sub(lambda m: local_mapping[m.group(0)], _ANALYSIS)
    query_read = pattern.sub(lambda m: local_mapping[m.group(0)], _READ_SUGGESTIONS)

    # 3.a -  Write operations
    result: Result = session.run_query(query_write, {"batch_size": batch_size})  # ty:ignore[invalid-argument-type]
    record = result.to_eager_result().records[0]
    if record["errorMessages"]:
        logger.error(
            f"apoc.periodic.iterate reported errors: {record['errorMessages']}",
        )

    # 3.b - Read operation
    candidates: Result = session.run_query(query_read)  # ty:ignore[invalid-argument-type]

    suggestions: list[LabelErr] = []
    for record in candidates.to_eager_result().records:
        node_id_x = record.get("ID1")
        node_id_y = record.get("ID2")
        labels_sim = record.get("labels_sim")
        sim_t = record.get("sim_t")

        if None in (node_id_x, node_id_y, labels_sim, sim_t):
            logger.error(f"Invalid record : {record}")
            continue

        suggestions.append(
            LabelErr(action, labels_sim, sim_t, node_id_x, node_id_y),
        )

    return suggestions


def _merge(
    session: Neo4jSession,
    tsl_merge: float,
    tsk_merge: float,
    batch_size: int,
) -> list[LabelErr]:
    mapping = {_TSL: str(tsl_merge), _TSK: str(tsk_merge)}
    return _analyze_labels(
        session,
        mapping,
        LabelAction.MERGE,
        "<=",
        ">=",
        batch_size,
    )


def _split(
    session: Neo4jSession,
    tsl_split: float,
    tsk_split: float,
    batch_size: int,
) -> list[LabelErr]:
    mapping = {_TSL: str(tsl_split), _TSK: str(tsk_split)}
    return _analyze_labels(
        session,
        mapping,
        LabelAction.SPLIT,
        ">=",
        "<=",
        batch_size,
    )


def labeling_clustering(
    session: Neo4jSession,
    tsl_merge: float,
    tsk_merge: float,
    tsl_split: float,
    tsk_split: float,
    batch_size: int = 150,
) -> list[LabelErr] | None:
    """
    :param session: A valid connection to a `Neo4jSession`.
    :type session: Neo4jSession
    :param tsl_merge: Treshold of similarity between labels set used for Merge.
        The value should be in [0;1].
    :type tsl_merge: float
    :param tsk_merge: Treshold of similarity between tokens set
        (using Hungarian algorithm score) used for Merge. The value should be in [0;1].
    :type tsk_merge: float
    :param tsl_split: Treshold of similarity between labels set used for Split.
        The value should be in [0;1].
    :type tsl_split: float
    :param tsk_split: Treshold of similarity between tokens set
        (using Hungarian algorithm score) used for Split. The value should be in [0;1].
    :type tsk_split: float
    :raises RuntimeError: If one of the `_CLEANUP` query failed.
    """

    cleanup_error = None
    analysis: list[LabelErr] = []

    try:
        session.run_query(_TOKENIZATION)  # ty:ignore[invalid-argument-type]
        session.run_query(_TOKENS_CREATION)  # ty:ignore[invalid-argument-type]
        session.run_query(_TOKENS_SIM)  # ty:ignore[invalid-argument-type]

        with Neo4jSession.clone(session) as session_tmp:
            # Merge analysis :
            analysis.extend(_merge(session_tmp, tsl_merge, tsk_merge, batch_size))

        with Neo4jSession.clone(session) as session_tmp:
            # Split analysis :
            analysis.extend(_split(session_tmp, tsl_split, tsk_split, batch_size))
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
