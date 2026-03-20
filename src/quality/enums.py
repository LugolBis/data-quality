from enum import Enum


class Constraint(str, Enum):
    UNIQUENESS = "UNIQUENESS"
    EXISTENCE = "EXISTENCE"
    KEY = "KEY"
    TYPE = "TYPE"
