from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from models.enums import Entity
from models.types import Violation
from quality.enums import BoolOperator, ConditionOp, ConditionType, SetRelation

if TYPE_CHECKING:
    from models.enums import Degree, Entity
    from quality.enums import Constraint

_ENTITY_CONDITION_ALIAS: str = "__ENTITY_CONDITION_ALIAS__"


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
class Component:
    entity: Entity
    entity_alias: str
    label: str
    graph_pattern: str
    invalid: int


@dataclass(slots=True, frozen=True, eq=False)
class RelationshipDuplicate:
    label: str
    invalid_pair: int


@dataclass(slots=True, frozen=True, eq=False)
class NodeDuplicate:
    label: str
    node_id_x: str
    node_id_y: str


@dataclass(slots=True, frozen=True, eq=False)
class MultivaluedDuplicate:
    entity: Entity
    label: str
    property_: str
    invalid: int


@dataclass(slots=True, frozen=True, eq=False)
class DateErr:
    entity: Entity
    label: str
    property: str
    fmt_found: set[str]


@dataclass(slots=True, frozen=True, eq=False)
class LblgSetErr:
    label: str
    cmp_set: set[str]
    relation: SetRelation
    invalid: int


@dataclass(slots=True, frozen=True, eq=False)
class FDErr:
    entity: Entity
    label: str
    x: set[str]
    y: set[str]
    invalid: int


@dataclass(slots=True, frozen=True, eq=False)
class CFDErr:
    entity: Entity
    label: str
    condition: str
    x: set[str]
    y: set[str]
    invalid: int


@dataclass(slots=True, frozen=True, eq=False)
class GFDErr:
    entity: Entity
    entity_alias: str
    label: str
    graph_pattern: str
    x: set[str]
    y: set[str]
    invalid: int


@dataclass(slots=True, frozen=True, eq=False)
class DVQErr:
    query: str
    should_be_empty: bool
    found: int


@dataclass(slots=True, frozen=True, eq=False)
class DegreeErr:
    degree: Degree
    label: str
    found: set[int]


@dataclass(slots=True, frozen=True, eq=False)
class ConditionValue:
    type: ConditionType
    value: Any

    def __str__(self) -> str:
        if self.type == ConditionType.PROPERTY:
            return str(f"{_ENTITY_CONDITION_ALIAS}['{self.value}']")
        return str(self.value)


@dataclass(slots=True, frozen=True, eq=False)
class Condition:
    property_: str
    value: ConditionValue
    operator: ConditionOp
    next: tuple[BoolOperator, Condition] | None

    def __str__(self) -> str:
        if self.next:
            return (
                f"({_ENTITY_CONDITION_ALIAS}['{self.property_}'] {self.operator!s}"
                f" {self.value!s}) {self.next[0]!s} {self.next[1]!s}"
            )
        return (
            f"{_ENTITY_CONDITION_ALIAS}['{self.property_}'] {self.operator!s}"
            f" {self.value!s}"
        )
