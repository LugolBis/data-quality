from typing import Optional

from driver.neo4j_driver import Neo4jSession
from quality.schema import check_constraint_violation, check_index_violation
from quality.types import ConstraintViolation, IndexViolation
from utils.utils import some


def main(session: Neo4jSession) -> None:
    constraints: Optional[list[ConstraintViolation]] = check_constraint_violation(
        session
    )
    indexes: Optional[list[IndexViolation]] = check_index_violation(session)

    if some(constraints):
        print("\n".join([v.__repr__() for v in constraints]))

    if some(indexes):
        print("\n")
        print("\n".join([v.__repr__() for v in indexes]))
