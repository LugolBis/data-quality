_STATE_LINK: int = 0
_STATE_ENTITY: int = 1


def _graph_pattern_parser(
    graph_pattern: str,
    entity_alias: str,
    index: int,
    label: str | None = None,
) -> str:
    label = label if label != "_" else None
    alias_nb = str(index)
    state: int = _STATE_LINK
    result = ""

    for char in graph_pattern:
        if state == _STATE_LINK:
            if char in ["(", "["]:
                state = _STATE_ENTITY
            result += char
        else:
            if char == ":":
                if result[-1] not in ["(", "["]:
                    result += alias_nb
            elif char in [")", "]"]:
                state = _STATE_LINK
                if result.endswith(entity_alias):
                    result += f"{alias_nb}:"

                if result.endswith(f"{entity_alias}{alias_nb}:"):
                    if label:
                        result += label
                    else:
                        result = result.removesuffix(":")
            result += char

    return result
