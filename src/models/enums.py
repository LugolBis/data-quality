from enum import Enum

WILDCARD = "_"


class Degree(str, Enum):
    INCOMING = "INCOMING"
    OUTCOMING = "OUTCOMING"


class Entity(Enum):
    NODE = "NODE"
    RELATIONSHIP = "RELATIONSHIP"
