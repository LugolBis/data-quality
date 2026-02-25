from typing import Optional
from driver.neo4j_driver import Neo4jSession
from quality.completeness import measure_wcc, measure_scc
from quality.types import ConnectedComponentsReport
from utils.utils import some


def main(session: Neo4jSession) -> None:

    wcc_report: Optional[ConnectedComponentsReport] = measure_wcc(session)
    scc_report: Optional[ConnectedComponentsReport] = measure_scc(session)

    if some(wcc_report):
        print("\n")
        print(wcc_report)

    if some(scc_report):
        print("\n")
        print(scc_report)
