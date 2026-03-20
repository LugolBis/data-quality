from typing import TYPE_CHECKING

from quality.schema import check_constraint_violation, check_index_violation
from utils.utils import some

if TYPE_CHECKING:
    from driver.neo4j_driver import Neo4jSession
    from quality.types import ConstraintViolation, IndexViolation


def main(session: Neo4jSession) -> None:
    constraints: list[ConstraintViolation] | None = check_constraint_violation(
        session,
    )
    indexes: list[IndexViolation] | None = check_index_violation(session)

    if some(constraints):
        print("\n".join([v.__repr__() for v in constraints]))

    if some(indexes):
        print("\n")
        print("\n".join([v.__repr__() for v in indexes]))
