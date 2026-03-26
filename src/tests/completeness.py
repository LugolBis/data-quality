from typing import TYPE_CHECKING

from profiling.completeness import measure_scc, measure_wcc
from utils.utils import some

if TYPE_CHECKING:
    from driver.neo4j_driver import Neo4jSession
    from profiling.types import CircularComponentsReport, IsolatedComponentsReport


def main(session: Neo4jSession) -> None:
    wcc_report: list[IsolatedComponentsReport] | None = measure_wcc(session)
    scc_report: list[CircularComponentsReport] | None = measure_scc(session)

    if some(wcc_report):
        print("\n")
        print(wcc_report)

    if some(scc_report):
        print("\n")
        print(scc_report)
