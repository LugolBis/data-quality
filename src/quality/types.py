from dataclasses import dataclass
from typing import TYPE_CHECKING

from models.types import Violation

if TYPE_CHECKING:
    from models.enums import Entity
    from quality.enums import Constraint


@dataclass(slots=True, frozen=True, eq=False)
class TextSimilarity:
    entity: Entity
    label: str
    similarity: float
    property: str
    first_value: str
    second_value: str

    def __repr__(self) -> str:
        return (
            f"[{self.similarity:.2f}] | {self.label} -> {self.property}\n\t"
            f"'{self.first_value}' <--> '{self.second_value}'"
        )


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
class QualityScore:
    valid: int
    total: int

    def __add__(self, other: QualityScore) -> QualityScore:
        return QualityScore(self.valid + other.valid, self.total + other.total)

    def __repr__(self) -> str:
        return f"{self.valid}\n_  is valid\n{self.total}"

    def percent(self) -> str:
        return f"{(self.valid / self.total) * 100:.2f}%"
