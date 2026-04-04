from enum import Enum


class Constraint(str, Enum):
    UNIQUENESS = "UNIQUENESS"
    EXISTENCE = "EXISTENCE"
    KEY = "KEY"
    TYPE = "TYPE"


class DateFmt(str, Enum):
    DATE = "DATE"
    LOCAL_TIME = "LOCAL TIME"
    ZONED_TIME = "ZONED TIME"
    LOCAL_DATETIME = "LOCAL DATETIME"
    ZONED_DATETIME = "ZONED DATETIME"

    def __str__(self) -> str:
        return self.value


class ConditionType(str, Enum):
    CONSTANT = "CONSTANT"
    PROPERTY = "PROPERTY"


class ConditionOp(str, Enum):
    EQUAL = "="
    DIFFERENT = "<>"
    GREATER = ">"
    GREATER_EQ = ">="
    LOWER = "<"
    LOWER_EQ = "<="
    CONTAINS = "IN"
    STARTS_WITH = "STARTS WITH"
    ENDS_WITH = "ENDS WITH"
    MATCH_REGEX = "=~"

    def __str__(self) -> str:
        return self.value


class BoolOperator(str, Enum):
    AND = "AND"
    NOT = "NOT"
    OR = "OR"
    XOR = "XOR"

    def __str__(self) -> str:
        return self.value
