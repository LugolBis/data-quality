from abc import ABC
from dataclasses import dataclass

from models.enums import Entity


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
                return (
                    f"Unknown entity : {default} - {self.label}) | count={self.count}"
                    f" -> {self.get_percent()}%"
                )
