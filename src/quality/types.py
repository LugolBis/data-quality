from dataclasses import dataclass

from quality.enums import EntityType


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
class SchemaViolation:
    entity: EntityType
    label: str
    count: int
    percent: float

    def __repr__(self) -> str:
        match self.entity:
            case EntityType.NODE:
                return f"({self.label}) | count={self.count} -> {self.percent}% of properties schema violation"
            case EntityType.RELATIONSHIP:
                return f"[{self.label}] | count={self.count} -> {self.percent}% of properties schema violation"
            case default:
                return f"Unknown type : {default} - {self.label}) | count={self.count} -> {self.percent}% of properties schema violation"
