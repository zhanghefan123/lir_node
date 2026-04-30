from typing import Tuple, List, Any, final

from modules.online.entities.sim_abstract_node import SimAbstractNode
from modules.online.types import types as tm


class SimDirectedLinkBase:
    def __init__(self, link_type: str, source: Any, target: Any):
        """
        :param link_type: 链路的类型 (对应 types.SimDirectedLinkType)
        :param source: 源节点 (对应 *SimAbstractNode)
        :param target: 目的节点 (对应 *SimAbstractNode)
        """
        self.type = link_type
        self.source = source
        self.target = target

    def get_source_and_target_names(self) -> Tuple[str, str]:
        """
        获取源和目的节点的名称
        """
        try:
            source_name = self.source.get_sim_node_name()
        except Exception as e:
            raise ValueError(f"Failed to get source name: {e}")

        try:
            target_name = self.target.get_sim_node_name()
        except Exception as e:
            raise ValueError(f"Failed to get target name: {e}")

        return source_name, target_name


class SimDirectedRealLink(SimDirectedLinkBase):
    def __init__(self, source: Any, target: Any):
        # 初始化父类，硬编码了 Go 代码里的 SimDirectedNormalLink 类型
        super().__init__(
            link_type=tm.SimDirectedLinkType.DirectedNormalLink,  # SimDirectedLinkType.SIM_DIRECTED_NORMAL_LINK
            source=source,
            target=target
        )


class SimDirectedAbsLink(SimDirectedLinkBase):
    def __init__(self, link_type: str, pv_link_description: str,
                 source: SimAbstractNode, intermediate: SimAbstractNode, target: SimAbstractNode):
        # 初始化父类，这里 Go 代码基类传的是 SimDirectedPvLink
        super().__init__(
            link_type=tm.SimDirectedLinkType.DirectedPvLink,  # SimDirectedLinkType.SIM_DIRECTED_PV_LINK
            source=source,
            target=target
        )

        self.link_type = link_type  # 链路的具体类型
        self.intermediate: SimAbstractNode = intermediate  # pvlink 的中间节点
        self.description = pv_link_description  # 对这个 directed pv link 的唯一描述

        # 到目前为止的跳变的次数
        # self.changed_times = 0

        # 各种随时间/迭代变化的列表属性
        self.weights: List[float] = []  # 随时间 t 变化
        self.illegal_ratios: List[float] = []  # 非法率
        self.explore_probabilities: List[float] = []  # 探索概率
        self.rectified_losses: List[float] = []  # 损失
        self.current_edge_probability: float = 0.0  # 为了 decomposition 而设置的一个临时变量

        # -------------------------------- deda 算法实现思路 ----------------------------
        self.accumulated_loss_z: float = 0
        self.weighted_accumulated_loss_m: float = 0
        self.sending_epoch_probabilities: List[float] = []
        self.accumulated_loss_z_list: List[float] = []
        self.weighted_accumulated_loss_m_list: List[float] = []
        # -------------------------------- deda 算法实现思路 ----------------------------
