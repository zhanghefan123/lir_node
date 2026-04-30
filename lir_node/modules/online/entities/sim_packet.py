import uuid
from typing import Any


# 假设 SimPacketType 在你的项目中是一个字符串或枚举类
# from modules.entities.real_entities.online.types import SimPacketType
# from .sim_abstract_node import SimAbstractNode  # 假设这是 SimAbstractNode 的导入路径

class SimPacket:
    def __init__(self, packet_type: Any, sample_node: Any, packet_uuid: str = None):
        """
        :param packet_type: 数据包的类型 (对应 types.SimPacketType)
        :param sample_node: 需要采样的 pv router (对应 *SimAbstractNode)
        :param packet_uuid: 数据包的唯一标识，默认自动生成
        """
        self.type = packet_type
        # 如果没有传入 uuid，则使用 Python 内置库自动生成一个 32 位的 UUID 字符串
        self.uuid = packet_uuid if packet_uuid else uuid.uuid4().hex

        # 默认初始状态
        self.is_corrupted = False  # 是否已经被篡改了
        self.is_dropped = False  # 是否已经被丢弃

        self.sample_node = sample_node


def create_sim_packet(packet_type: Any, sample_node: Any) -> SimPacket:
    """
    进行模拟数据包的创建 (对应 Go 中的 CreateSimPacket)
    """
    return SimPacket(
        packet_type=packet_type,
        sample_node=sample_node
    )