from enum import Enum


class Degree(str, Enum):
    INCOMING = "INCOMING"
    OUTCOMING = "OUTCOMING"


class Entity(Enum):
    NODE = "NODE"
    RELATIONSHIP = "RELATIONSHIP"


class Constraint(str, Enum):
    UNIQUENESS = "UNIQUENESS"
    EXISTENCE = "EXISTENCE"
    KEY = "KEY"
    TYPE = "TYPE"


class ComponentAlgo(Enum):
    WCC = "WCC"
    SCC = "SCC"
