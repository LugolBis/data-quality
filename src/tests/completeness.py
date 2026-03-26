from typing import TYPE_CHECKING

from models.enums import Entity
from profiling.completeness import measure_scc, measure_wcc
from quality.completeness import existence_path
from utils.utils import some

if TYPE_CHECKING:
    from driver.neo4j_driver import Neo4jSession
    from profiling.types import CircularComponentsReport, IsolatedComponentsReport
    from quality.types import ElementaryPath


def main(session: Neo4jSession) -> None:
    path_report: ElementaryPath | None = existence_path(
        session,
        Entity("NODE"),
        "n1",
        "Person",
        "(n1)-[*]->(n2:Company)",
    )
    wcc_report: list[IsolatedComponentsReport] | None = measure_wcc(session)
    scc_report: list[CircularComponentsReport] | None = measure_scc(session)

    if some(path_report):
        print("\n")
        print(f"FAILED to verifiy the following path existence : {path_report}")

    if some(wcc_report):
        print("\n")
        print(wcc_report)

    if some(scc_report):
        print("\n")
        print(scc_report)
