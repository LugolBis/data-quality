from enum import Enum


class AnalysisState(str, Enum):
    IDLE = "idle"
    ERROR = "error"
    EMPTY = "empty"
    SUCCESS = "success"
