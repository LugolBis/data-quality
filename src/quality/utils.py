from quality.enums import Entity
from utils.utils import logger


def _build_match(entity_type: Entity, label_str: str, alias: str = "e") -> str:
    match entity_type:
        case Entity.NODE:
            return f"MATCH ({alias}:{label_str}) "
        case Entity.RELATIONSHIP:
            return f"MATCH ()-[{alias}:{label_str}]->() "
        case default:
            logger.error(f"Unknown entity : {default}")
            return f"// Unknown entity {default}\nMATCH ({alias}:{label_str}) "
