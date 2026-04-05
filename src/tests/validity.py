import re
from typing import TYPE_CHECKING

from models.enums import Entity
from profiling.validity import check_properties_type
from quality.enums import DateFmt, SetRelation
from quality.validity import check_date_format, check_string_format, labeling_set
from utils.utils import some

if TYPE_CHECKING:
    from driver.neo4j_driver import Neo4jSession
    from profiling.types import PairPropertiesType
    from quality.types import DateErr, TextFormat


def main(session: Neo4jSession) -> None:
    formats: list[TextFormat] | None = check_string_format(
        session,
        Entity.NODE,
        "Person",
        ["name"],
        re.compile("Jo.*"),
        True,
    )

    date_fmt: list[DateErr] | None = check_date_format(
        session,
        Entity.NODE,
        "Person",
        ["birth"],
        DateFmt.DATE,
    )

    lblg_set = labeling_set(
        session,
        "Actif",
        SetRelation.EXCLUDE,
        {"Person"},
    )

    types: list[PairPropertiesType] | None = check_properties_type(session)

    if some(formats):
        print("\n")
        print("\n".join([ft.__repr__() for ft in formats]))

    if some(date_fmt):
        print("\n")
        print(date_fmt)

    if some(lblg_set):
        print("\n")
        print(lblg_set)

    if some(types):
        print("\n".join([t.__repr__() for t in types]))
