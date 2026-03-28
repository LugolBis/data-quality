from typing import TYPE_CHECKING

from models.enums import Entity
from quality.consistency import fd
from utils.utils import some

if TYPE_CHECKING:
    from driver.neo4j_driver import Neo4jSession


def main(session: Neo4jSession) -> None:
    fd_err = fd(session, Entity.NODE, "Person", {"name"}, {"birth"})

    if some(fd_err):
        print("\n")
        print(f"The functional dependency isn't verified : {fd_err}")
