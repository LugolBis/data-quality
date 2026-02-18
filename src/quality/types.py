from abc import ABC
from dataclasses import dataclass
from typing import Set, Tuple

from quality.enums import Constraint, Degree, Entity


@dataclass
class MultiGraphEdges:
    label_from: str
    label_to: str
    relationships: list[str]


@dataclass
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


@dataclass
class NodeDegrees(Statistics):
    label: str
    degree: Degree
    count: int


@dataclass
class EntityProperties:
    names: list[str]
    count: int
    percent: float

    def __repr__(self) -> str:
        return f"[{', '.join(self.names)}] |-> count={self.count} | percent={self.percent:.1f}%"


@dataclass
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


@dataclass
class TextSimilarity:
    entity: Entity
    label: str
    similarity: float
    property: str
    first_value: str
    second_value: str

    def __repr__(self) -> str:
        return f"[{self.similarity:.2f}] | {self.label} -> {self.property}\n\t'{self.first_value}' <--> '{self.second_value}'"


@dataclass
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


@dataclass
class PairPropertiesType(Violation):
    property: str
    types: Set[Tuple[str, str]]

    def __repr__(self) -> str:
        return super().__repr__() + f" | {self.property}\n\t{self.types}"


@dataclass
class TextFormat(Violation):
    property: str

    def __repr__(self) -> str:
        return super().__repr__() + f" of Text Format violation for {self.property}"


@dataclass
class IndexViolation(Violation):
    def __repr__(self) -> str:
        return super().__repr__() + " of Index violation"


@dataclass
class ConstraintViolation(Violation):
    constraint: Constraint
    properties: list[str]

    def __repr__(self) -> str:
        return (
            f"{self.constraint} on {self.properties} | "
            + super().__repr__()
            + " of Constraint violation"
        )
