from typing import TYPE_CHECKING

from profiling.integrity import (
    distr_nodes_properties,
    distr_properties_per_label,
    distr_relationships_properties,
)
from quality.integrity import (
    check_constraint_violation,
    check_index_violation,
)
from utils.utils import some

if TYPE_CHECKING:
    from driver.neo4j_driver import Neo4jSession
    from profiling.types import EntityStats
    from quality.types import ConstraintViolation, IndexViolation


def main(session: Neo4jSession) -> None:
    properties: list[EntityStats] | None = distr_nodes_properties(session)

    properties_per_label: list[EntityStats] | None = distr_properties_per_label(session)

    relationships: list[EntityStats] | None = distr_relationships_properties(session)

    constraints: list[ConstraintViolation] | None = check_constraint_violation(
        session,
    )
    indexes: list[IndexViolation] | None = check_index_violation(session)

    if some(properties):
        print(properties)

    if some(properties_per_label):
        print("\n")
        print(properties_per_label)

    if some(relationships):
        print("\n")
        print(relationships)

    if some(constraints):
        print("\n".join([v.__repr__() for v in constraints]))

    if some(indexes):
        print("\n")
        print("\n".join([v.__repr__() for v in indexes]))
