from modules.online.types import types as tm
from modules.online.entities import sim_params as spm


def resolve_sim_node_type(typeString: str) -> int:
    if typeString == "EndHost":
        return tm.SimNetworkNodeType.END_HOST
    elif typeString == "NormalRouter":
        return tm.SimNetworkNodeType.NORMAL_ROUTER
    elif typeString == "PathValidationRouter":
        return tm.SimNetworkNodeType.PATH_VALIDATION_ROUTER
    else:
        raise ValueError(f"unsupported node type: {typeString}")


def resolve_sim_node_name(nodeParam: spm.SimNodeParam) -> str:
    nodeType = resolve_sim_node_type(nodeParam.type)
    nodeName = f"{nodeType}-{nodeParam.index}"
    return nodeName
