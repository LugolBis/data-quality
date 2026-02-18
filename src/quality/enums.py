from enum import Enum


class Degree(Enum):
    INCOMING = "INCOMING"
    OUTCOMING = "OUTCOMING"


class Entity(Enum):
    NODE = "NODE"
    RELATIONSHIP = "RELATIONSHIP"


class Constraint(Enum):
    UNIQUENESS = "UNIQUENESS"
    EXISTENCE = "EXISTENCE"
    KEY = "KEY"
    TYPE = "TYPE"
