from enum import Enum


class WidgetState(str, Enum):
    IDLE = "idle"
    ERROR = "error"
    EMPTY = "empty"
    SUCCESS = "success"


class LoadMethod(Enum):
    CSV = "CSV file"
    DUMP = ".dump file"
    SCRIPT = "Cypher script"
