from enum import Enum


class Entity(Enum):
    NODE = "NODE"
    RELATIONSHIP = "RELATIONSHIP"


class Constraint(Enum):
    UNIQUENESS = "UNIQUENESS"
    EXISTENCE = "EXISTENCE"
    KEY = "KEY"
    TYPE = "TYPE"
