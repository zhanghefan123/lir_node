from typing import Any
from modules.online.types import types as tm


class SimAbstractNode:
    def __init__(self, node_type: int, actual_node: Any, id_generator: int = None):
        """
        :param node_type: 节点类型 (SimNetworkNodeType)
        :param actual_node: 实际的节点对象 (SimEndHost, SimNormalRouter 等)
        :param id_generator: 用于 networkx 图节点的唯一标识 (对应 Go 中的 graph.Node 的 ID)
        """
        self.id = id_generator
        self.type = node_type
        self.actual_node = actual_node
        self.potential: float = 0.0
        self.flow: float = 0.0

    # ---------------------------------------------------------
    # 以下两个魔术方法是为了让这个对象可以无缝作为 networkx 图的节点
    # 等价于 Go 语言中实现 graph.Node 接口的 ID() 方法
    # ---------------------------------------------------------
    def __hash__(self):
        return hash(self.id) if self.id is not None else id(self)

    def __eq__(self, other):
        if isinstance(other, SimAbstractNode):
            return self.id == other.id
        return False

    def get_sim_node_base_from_abstract(self) -> Any:
        """
        在 Python 中，由于 EndHost, NormalRouter 等都继承自 SimNodeBase，
        它们本身就包含了 node_name 和 index 属性。
        因此我们不需要像 Go 那样做繁琐的 switch 类型断言，直接返回 actual_node 即可。
        """
        valid_types = [
            tm.SimNetworkNodeType.END_HOST,
            tm.SimNetworkNodeType.NORMAL_ROUTER,
            tm.SimNetworkNodeType.PATH_VALIDATION_ROUTER
        ]

        if self.type in valid_types:
            # 在 Python 的面向对象模型中，子类实例可以直接当做父类使用
            return self.actual_node
        else:
            raise ValueError("cannot get sim node base from abstract: unknown type")

    def get_sim_node_name(self) -> str:
        """
        获取节点名称。
        """
        try:
            base_node = self.get_sim_node_base_from_abstract()
            # 直接访问父类 SimNodeBase 中定义的 node_name 属性
            return base_node.node_name
        except AttributeError:
            raise ValueError(f"get sim node failed: actual_node is missing 'node_name' attribute")
        except Exception as e:
            raise ValueError(f"get sim node failed: {e}")
