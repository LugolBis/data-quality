from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from models.enums import Degree, Entity
from models.types import Violation

if TYPE_CHECKING:
    from profiling.enums import ComponentAlgo


@dataclass(slots=True, frozen=True, eq=False)
class EntityProperties:
    names: list[str]
    count: int
    percent: float

    def __repr__(self) -> str:
        return (
            f"[{', '.join(self.names)}] |-> count={self.count} | "
            f"percent={self.percent:.1f}%"
        )


@dataclass(slots=True, frozen=True, eq=False)
class EntityStats:
    entity: Entity
    label: str
    count: int
    properties: list[EntityProperties]

    def __repr__(self) -> str:
        match self.entity:
            case Entity.NODE:
                return (
                    f"\n({self.label}) | count={self.count} :\n\t"
                    f"{'\n\t'.join([node.__repr__() for node in self.properties])}"
                )
            case Entity.RELATIONSHIP:
                return (
                    f"\n[{self.label}] | count={self.count} :\n\t"
                    f"{'\n\t'.join([node.__repr__() for node in self.properties])}"
                )


@dataclass
class ComponentDetail:
    component_id: int
    size: int
    sample_nodes: list[str] = field(default_factory=list)

    def __repr__(self) -> str:
        samples_str = " | ".join(self.sample_nodes)
        return f"Component {self.component_id} ({self.size} nodes) -> {samples_str}"


@dataclass(slots=True, frozen=True, eq=False)
class IsolatedComponentsReport:
    algorithm: ComponentAlgo
    total_components: int
    total_nodes: int
    largest_components: list[ComponentDetail]

    def __repr__(self) -> str:
        details: str = "\n\t\t".join([str(c) for c in self.largest_components])
        return (
            f"[{self.algorithm}] | Total Components: {self.total_components} | "
            f"Total Nodes: {self.total_nodes}\n"
            f"\tisolated components:\n\t\t{details}"
        )


@dataclass(slots=True, frozen=True, eq=False)
class CircularComponentsReport:
    algorithm: ComponentAlgo
    total_components: int
    total_nodes: int
    largest_components: list[ComponentDetail]

    def __repr__(self) -> str:
        details: str = "\n\t\t".join([str(c) for c in self.largest_components])
        return (
            f"[{self.algorithm}] | Total Components: {self.total_components} | "
            f"Total Nodes: {self.total_nodes}\n"
            f"\tcircular components:\n\t\t{details}"
        )


@dataclass(slots=True, frozen=True, eq=False)
class AnomalyDetail:
    entity_type: str
    similarity: float
    id1: str
    labels1: str
    id2: str
    labels2: str

    def __repr__(self) -> str:
        return (
            f"[{self.entity_type}] Sim: {self.similarity:.4f} | "
            f"('{self.labels1}' id:{self.id1}) <---> ('{self.labels2}' id:{self.id2})"
        )


@dataclass(slots=True, frozen=True, eq=False)
class FeatureMismatchReport:
    threshold: float
    total_anomalies: int
    anomalies: list[AnomalyDetail]

    def __repr__(self) -> str:
        details = "\n".join([str(a) for a in self.anomalies])
        return (
            f"FEATURE & LABEL MISMATCH REPORT (Similarity >= {self.threshold})\n"
            f"Total Anomalies Found: {self.total_anomalies}\n"
            f"Details:\n{details}"
        )


@dataclass(slots=True, frozen=True, eq=False)
class Eccentricity:
    diameter: float
    radius: float


@dataclass(slots=True, frozen=True, eq=False)
class MultiGraphEdges:
    label_from: str
    label_to: str
    relationships: list[str]


@dataclass(slots=True, frozen=True, eq=False)
class Statistics:
    count: int
    limits: tuple[float, float]
    sum_: float
    average: float
    median: float
    variance: float
    standard_deviation: float
    q1: float
    q2: float
    q3: float


@dataclass(slots=True, frozen=True, eq=False)
class NodeDegrees(Statistics):
    label: str
    degree: Degree


@dataclass(slots=True, frozen=True, eq=False)
class OutlierDetail:
    node_id: str
    value: float

    def __repr__(self) -> str:
        return f"NodeID: {self.node_id} | Value: {self.value}"


@dataclass(slots=True, frozen=True, eq=False)
class NumericalOutlier:
    label: str
    property: str
    mean: float
    std_dev: float
    lower_bound: float
    upper_bound: float
    outliers: list[OutlierDetail]

    def __repr__(self) -> str:
        details = "\n\t\t".join([str(o) for o in self.outliers])
        return (
            f"(:{self.label}) on property '{self.property}'\n"
            f"Mean: {self.mean:.2f} | Std: {self.std_dev:.2f}\n"
            f"Confidence Interval: [{self.lower_bound:.2f}, {self.upper_bound:.2f}]\n"
            f"Outliers ({len(self.outliers)} found):\n{details}"
        )


@dataclass(slots=True, frozen=True, eq=False)
class CentralityScore:
    element_id: str
    label: str
    score: float


@dataclass(slots=True, frozen=True, eq=False)
class LabelCentralityStats:
    label: str
    count: int
    avg_score: float
    max_score: float

    def __repr__(self) -> str:
        return (
            f"(:{self.label}) | count={self.count} -> Avg Score: {self.avg_score:.4f} "
            f"(Max: {self.max_score:.4f})"
        )


@dataclass(slots=True, frozen=True, eq=False)
class PairPropertiesType(Violation):
    property: str
    types: set[tuple[str, str]]

    def __repr__(self) -> str:
        return super().__repr__() + f" | {self.property}\n\t{self.types}"
