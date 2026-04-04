from typing import TYPE_CHECKING

from models.enums import Entity
from quality.consistency import cfd, fd, gfd, query_validation
from quality.enums import BoolOperator, ConditionOp, ConditionType
from quality.types import Condition, ConditionValue
from utils.utils import some

if TYPE_CHECKING:
    from driver.neo4j_driver import Neo4jSession


def main(session: Neo4jSession) -> None:
    fd_err = fd(session, Entity.NODE, "Person", {"name"}, {"birth"})

    sub_condition = Condition(
        "ski_level",
        ConditionValue(
            ConditionType.CONSTANT,
            ["confirmed", "beginner", "professionnal"],
        ),
        ConditionOp.CONTAINS,
        None,
    )
    condition = Condition(
        "education",
        ConditionValue(ConditionType.CONSTANT, 45),
        ConditionOp.LOWER,
        (
            BoolOperator.OR,
            sub_condition,
        ),
    )
    cfd_err = cfd(session, Entity.NODE, "Person", condition, {"name"}, {"birth"})

    gfd_err = gfd(
        session,
        Entity.NODE,
        "city",
        "City",
        "(pa:Actif)-[:Habite]->(city)<-[:Est_maire]-(:Person)",
        {"country", "name", "dept"},
        {"arr"},
    )

    dvq_err = query_validation(
        session,
        "MATCH (c1:City)-[:Love]->(c2:Company) RETURN c1, c2",
        False,  # noqa: FBT003
    )

    if some(fd_err):
        print("\n")
        print(f"The functional dependency isn't verified : {fd_err}")

    if some(cfd_err):
        print("\n")
        print(f"The conditional functional dependency isn't verified : {cfd_err}")

    if some(gfd_err):
        print("\n")
        print(f"The graph functional dependency isn't verified : {gfd_err}")

    if some(dvq_err):
        print("\n")
        print(f"The data query validation isn't verified : {dvq_err}")
