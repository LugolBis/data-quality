import re
from typing import TYPE_CHECKING

from scipy.optimize import linear_sum_assignment

from quality.enums import LabelAction
from quality.types import LabelErr
from utils.utils import logger

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
        ELSE 1-(toFloat(size(Y)) / (size(X) + size(Y)))
        END AS labels_sim

    WHERE labels_sim $TSL_OP$ $TRESHOLD_SIM_LABELS$

    MATCH (nt1:___Token)-[r:___SIMILAR_TO]-(nt2:___Token)
    WHERE nt1.value IN n1.___Tokens AND nt2.value IN n2.___Tokens

    WITH n1, n2, labels_sim,
        n1.___Tokens AS tokens1,
        n2.___Tokens AS tokens2,
        collect({t1: nt1.value, t2: nt2.value, score: r.score}) AS simPairs

    RETURN elementId(n1) AS ID1, elementId(n2) AS ID2,
        labels_sim, tokens1, tokens2, simPairs;
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

    result: Result = session.run_query(query)  # ty:ignore[invalid-argument-type]
    records = result.to_eager_result().records

    treshold_sim_tokens = float(mapping[_TSK])
    suggestions: list[LabelErr] = []

    for record in records:
        node_id_x = record.get("ID1")
        node_id_y = record.get("ID2")
        labels_similarity = record.get("labels_sim")
        tokens1 = record.get("tokens1")
        tokens2 = record.get("tokens2")
        sim_pairs = record.get("simPairs")

        if None in (node_id_x, node_id_y, labels_similarity, tokens1, tokens2):
            logger.error(f"Invalid record : {record}")
            continue

        # Build the score dictionnary
        score_dict = {}
        for sp in sim_pairs or []:
            t1 = sp["t1"]
            t2 = sp["t2"]
            score = sp["score"]
            score_dict[(t1, t2)] = score

        # Build the cost matrix
        cost_matrix = [
            [score_dict.get((t1, t2), 1.0) for t2 in tokens2] for t1 in tokens1
        ]

        # Apply the Hungarian algorithm score (maximize)
        row_idx, col_idx = linear_sum_assignment(cost_matrix, maximize=True)
        total_sim = sum(
            cost_matrix[i][j] for i, j in zip(row_idx, col_idx, strict=True)
        )

        max_len = max(len(tokens1), len(tokens2))
        tokens_similarity = total_sim / max_len if max_len > 0 else 0.0

        condition_tsk = False
        if tsk_op == ">=":
            condition_tsk = tokens_similarity >= treshold_sim_tokens
        elif tsk_op == "<=":
            condition_tsk = tokens_similarity <= treshold_sim_tokens
        else:
            logger.error(f"Unsupported tsk_op: {tsk_op}")
            continue

        if condition_tsk:
            suggestions.append(
                LabelErr(
                    action,
                    labels_similarity,
                    tokens_similarity,
                    node_id_x,
                    node_id_y,
                ),
            )

    return suggestions


def _merge(
    session: Neo4jSession,
    tsl_merge: float,
    tsk_merge: float,
) -> list[LabelErr]:
    mapping = {_TSL: str(tsl_merge), _TSK: str(tsk_merge)}
    return _analyze_labels(
        session,
        mapping,
        LabelAction.MERGE,
        tsl_op="<=",
        tsk_op=">=",
    )


def _split(
    session: Neo4jSession,
    tsl_split: float,
    tsk_split: float,
) -> list[LabelErr]:
    mapping = {_TSL: str(tsl_split), _TSK: str(tsk_split)}
    return _analyze_labels(
        session,
        mapping,
        LabelAction.SPLIT,
        tsl_op=">=",
        tsk_op="<=",
    )


def labeling_clustering(
    session: Neo4jSession,
    tsl_merge: float,
    tsk_merge: float,
    tsl_split: float,
    tsk_split: float,
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

        # Merge analysis :
        analysis.extend(_merge(session, tsl_merge, tsk_merge))

        # Split analysis :
        analysis.extend(_split(session, tsl_split, tsk_split))
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
