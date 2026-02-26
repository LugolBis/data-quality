from abc import ABC
from dataclasses import dataclass
from typing import Set, Tuple

from quality.enums import ComponentAlgo, Constraint, Degree, Entity


@dataclass(slots=True, frozen=True, eq=False)
class MultiGraphEdges:
    label_from: str
    label_to: str
    relationships: list[str]


@dataclass(slots=True, frozen=True, eq=False)
class Statistics:
    count: int
    limits: Tuple[float, float]
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
class EntityProperties:
    names: list[str]
    count: int
    percent: float

    def __repr__(self) -> str:
        return f"[{', '.join(self.names)}] |-> count={self.count} | percent={self.percent:.1f}%"


@dataclass(slots=True, frozen=True, eq=False)
class EntityStats:
    entity: Entity
    label: str
    count: int
    properties: list[EntityProperties]

    def __repr__(self) -> str:
        match self.entity:
            case Entity.NODE:
                return f"\n({self.label}) | count={self.count} :\n\t{'\n\t'.join([node.__repr__() for node in self.properties])}"
            case Entity.RELATIONSHIP:
                return f"\n[{self.label}] | count={self.count} :\n\t{'\n\t'.join([node.__repr__() for node in self.properties])}"


@dataclass(slots=True, frozen=True, eq=False)
class TextSimilarity:
    entity: Entity
    label: str
    similarity: float
    property: str
    first_value: str
    second_value: str

    def __repr__(self) -> str:
        return f"[{self.similarity:.2f}] | {self.label} -> {self.property}\n\t'{self.first_value}' <--> '{self.second_value}'"


@dataclass(slots=True, frozen=True, eq=False)
class Violation(ABC):
    entity: Entity
    label: str
    count: int
    invalid: int

    def get_percent(self, precision: int = 2) -> float:
        return round(float((self.invalid / self.count) * 100), precision)

    def __repr__(self) -> str:
        match self.entity:
            case Entity.NODE:
                return f"({self.label}) | count={self.count} -> {self.get_percent()}%"
            case Entity.RELATIONSHIP:
                return f"[{self.label}] | count={self.count} -> {self.get_percent()}%"
            case default:
                return f"Unknown entity : {default} - {self.label}) | count={self.count} -> {self.get_percent()}%"


@dataclass(slots=True, frozen=True, eq=False)
class PairPropertiesType(Violation):
    property: str
    types: Set[Tuple[str, str]]

    def __repr__(self) -> str:
        return super().__repr__() + f" | {self.property}\n\t{self.types}"


@dataclass(slots=True, frozen=True, eq=False)
class TextFormat(Violation):
    property: str

    def __repr__(self) -> str:
        return super().__repr__() + f" of Text Format violation for {self.property}"


@dataclass(slots=True, frozen=True, eq=False)
class IndexViolation(Violation):
    properties: list[str]

    def __repr__(self) -> str:
        return super().__repr__() + " of Index violation"


@dataclass(slots=True, frozen=True, eq=False)
class ConstraintViolation(Violation):
    constraint: Constraint
    properties: list[str]

    def __repr__(self) -> str:
        return (
            f"{self.constraint} on {self.properties} | "
            + super().__repr__()
            + " of Constraint violation"
        )


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
        return f"(:{self.label}) | count={self.count} -> Avg Score: {self.avg_score:.4f} (Max: {self.max_score:.4f})"


@dataclass(slots=True, frozen=True, eq=False)
class QualityScore:
    valid: int
    total: int

    def __add__(self, other: QualityScore) -> QualityScore:
        return QualityScore(self.valid + other.valid, self.total + other.total)

    def __repr__(self) -> str:
        return f"{self.valid}\n_  is valid\n{self.total}"

    def percent(self) -> str:
        return f"{(self.valid / self.total) * 100:.2f}%"


@dataclass(slots=True, frozen=True, eq=False)
class ComponentDetail:
    component_id: int
    size: int

    def __repr__(self) -> str:
        return f"Component ID: {self.component_id} -> {self.size} nodes"


@dataclass(slots=True, frozen=True, eq=False)
class IsolatedComponentsReport:
    algorithm: ComponentAlgo
    total_components: int
    total_nodes: int
    largest_components: list[ComponentDetail]

    def __repr__(self) -> str:
        details: str = "\n\t\t".join([str(c) for c in self.largest_components])
        return (
            f"[{self.algorithm}] | Total Components: {self.total_components} | Total Nodes: {self.total_nodes}\n"
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
            f"[{self.algorithm}] | Total Components: {self.total_components} | Total Nodes: {self.total_nodes}\n"
            f"\tcircular components:\n\t\t{details}"
        )
