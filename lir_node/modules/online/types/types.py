# 假设这些是你定义的枚举或常量（对应 Go 中的 types 包）
class GainCalculationMode:
    SUM_EDGE_GAINS = "SumEdgeGains"
    SUM_EDGE_AND_ROUTER_GAINS = "SumEdgeAndRouterGains"


class SimStrategy:
    PER_PACKET_ACK = "PerPacketAck"


class SimNetworkNodeType:
    NORMAL_ROUTER = "NormalRouter"
    PATH_VALIDATION_ROUTER = "PathValidationRouter"
    END_HOST = "EndHost"


class SimPacketType:
    DataPacket = "DataPacket"
    AckPacket = "AckPacket"


class SimDirectedLinkType:
    DirectedNormalLink = "DirectedNormalLink"
    DirectedPvLink = "DirectedPvLink"
    DirectedAccessLink = "DirectedAccessLink"


class RunningType:
    RealTest = "RealTest"
    VirtualTest = "VirtualTest"


class RectifiedLossCalculateType:
    TYPE_DELIVERY_RATIO = 0  # 使用传统模式
    TYPE_SCALING = 1  # 使用放缩方式
