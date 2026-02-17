from abc import ABC
from dataclasses import dataclass

from quality.enums import Constraint, Entity


@dataclass
class NodeProperties:
    names: list[str]
    count: int
    percent: float

    def __repr__(self) -> str:
        return f"[{', '.join(self.names)}] |-> count={self.count} | percent={self.percent:.1f}%"


@dataclass
class LabelStats:
    label: str
    count: int
    properties: list[NodeProperties]

    def __repr__(self) -> str:
        return f"\n{self.label} | count={self.count} :\n\t{'\n\t'.join([node.__repr__() for node in self.properties])}"


@dataclass
class TextSimilarity:
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
