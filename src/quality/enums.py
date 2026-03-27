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
