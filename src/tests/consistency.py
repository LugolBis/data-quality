import re
from typing import TYPE_CHECKING

from models.enums import Entity
from profiling.consistency import check_properties_type
from quality.consistency import check_string_format
from utils.utils import some

if TYPE_CHECKING:
    from driver.neo4j_driver import Neo4jSession
    from models.types import PairPropertiesType
    from quality.types import TextFormat


def main(session: Neo4jSession) -> None:
    formats: list[TextFormat] | None = check_string_format(
        session,
        Entity.NODE,
        "Person",
        ["name"],
        re.compile("Jo.*"),
        True,
    )

    types: list[PairPropertiesType] | None = check_properties_type(session)

    if some(formats):
        print("\n".join([ft.__repr__() for ft in formats]))

    if some(types):
        print("\n".join([t.__repr__() for t in types]))
