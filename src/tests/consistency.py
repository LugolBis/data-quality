import re
from typing import Optional

from driver.neo4j_driver import Neo4jSession
from quality.consistency import check_string_format
from quality.enums import Entity
from quality.types import TextFormat
from utils.utils import some


def main(session: Neo4jSession) -> None:
    formats: Optional[list[TextFormat]] = check_string_format(
        session, Entity.NODE, "Person", ["name"], re.compile("Jo.*"), True
    )

    if some(formats):
        print("\n".join([ft.__repr__() for ft in formats]))
