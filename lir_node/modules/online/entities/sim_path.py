from typing import List, Dict, Tuple, Any
from modules.online.entities.sim_abstract_node import SimAbstractNode
from modules.online.entities.sim_directed_link import SimDirectedAbsLink
from modules.online.entities.sim_normal_router import SimNormalRouter
from modules.online.entities.sim_path_validation_router import SimPathValidationRouter
from modules.online.types import types as tm
from modules.config import interface_loader as ilm


def find_next_pv_router_or_end_host(sim_path: 'SimPath', start_index: int) -> Tuple[Any, int, Any]:
    """
    从 start_index 开始找到第一个 (pv router 或者 end host) 以及它的 index,
    并且在这个 pv router 之前只能有一个 normal router，如果有超过一个 normal router 就抛出异常。
    返回: (target_node, target_index, normal_router)
    """
    normal_router = None
    number_of_normal_routers = 0

    for index in range(start_index + 1, len(sim_path.node_list)):
        node = sim_path.node_list[index]

        if node.type == tm.SimNetworkNodeType.NORMAL_ROUTER:
            normal_router = node
            number_of_normal_routers += 1
            if number_of_normal_routers > 1:
                raise ValueError("too many normal routers within pvlink")

        if node.type in (tm.SimNetworkNodeType.PATH_VALIDATION_ROUTER, tm.SimNetworkNodeType.END_HOST):
            return node, index, normal_router

    return None, -1, None


class SimPath:
    def __init__(self):
        self.path_id: int = 0  # 路径的唯一 id
        self.node_list: List[SimAbstractNode] = []  # 可以是两种不同的 router (SimAbstractNode)
        self.pv_routers: List[SimPathValidationRouter] = []  # 这条路径上所有的 pv router
        self.pv_routers_mapping: Dict[str, SimPathValidationRouter] = {}  # 这条路径上所有的 pv router 的 mapping
        self.directed_abs_links: List[SimDirectedAbsLink] = []  # 这条路径上所有的 directed pv link
        self.directed_abs_links_mapping: Dict[str, SimDirectedAbsLink] = {}  # 从 description 到 directed pv link 的 mapping
        self.node_name_to_index_mapping: Dict[str, int] = {}  # 从节点的名称到对应索引
        self.weights: List[float] = []  # 这条路径的历史权重
        self.explore_probabilities: List[float] = []  # 根据 weight 算出来的当前应该选的路径的概率
        self.gains: List[float] = []  # 这条路径的增益
        self.score: float = 0.0  # 用来进行排序的
        self.description: str = ""  # 对这条路径的唯一描述
        self.average_corrupt_ratio: float = 0.0
        self.average_drop_ratio: float = 0.0
        self.interfaces: List[ilm.Interface] = []
        self.modified_batch_size: int = 0

    def __str__(self):
        return self.description

    def get_path_description(self) -> str:
        if not self.node_list:
            raise ValueError("get path description failed due to empty node list")

        # 在 Python 中，直接将节点名称收集到列表中，最后用 join 拼接即可
        node_names = [node.get_sim_node_name() for node in self.node_list]
        return "->".join(node_names)

    def get_directed_abs_links(self) -> Tuple[List[SimDirectedAbsLink], Dict[str, SimDirectedAbsLink]]:
        return self.directed_abs_links, self.directed_abs_links_mapping

    def update_info(self, name_to_pv_link_mapping: Dict[str, Any]):
        """
        Fill directed_pv_links_mapping and directed_abs_links
        """
        directed_pv_links = []
        directed_pv_links_mapping = {}

        start_index = 0
        current_node_index = 0

        while True:
            source_node = self.node_list[start_index]
            target_node, start_index, intermediate_node = find_next_pv_router_or_end_host(self, start_index)

            if target_node is None:
                break

            source_node_name = source_node.get_sim_node_name()
            intermediate_node_name = intermediate_node.get_sim_node_name()
            target_node_name = target_node.get_sim_node_name()

            # get description of the directed pv link
            pv_link_description = f"{source_node_name}->{intermediate_node_name}->{target_node_name}"

            # record mapping
            self.node_name_to_index_mapping[target_node_name] = current_node_index
            current_node_index += 1

            # get pv link from mapping
            directed_pv_link = name_to_pv_link_mapping[pv_link_description]

            # update pv router list
            if target_node.type == tm.SimNetworkNodeType.PATH_VALIDATION_ROUTER:
                pv_router = target_node.actual_node
                if not pv_router:
                    raise ValueError("target node actual_node is not a path validation router")

                self.pv_routers.append(pv_router)
                self.pv_routers_mapping[pv_router.node_name] = pv_router

            # update pv link list
            directed_pv_links.append(directed_pv_link)
            if pv_link_description not in directed_pv_links_mapping:
                directed_pv_links_mapping[pv_link_description] = directed_pv_link
            else:
                raise ValueError(
                    f"get directed pv links failed due to duplicate directed pv link description: {pv_link_description}")

        self.directed_abs_links = directed_pv_links
        self.directed_abs_links_mapping = directed_pv_links_mapping

    def calculate_regret(self, minimum_delivery_ratio: float) -> float:
        """
        进行后悔值的计算
        :param minimum_delivery_ratio: 允许的最小的传输成功率
        :return:
        """
        regret_value = 0.0
        for pv_link in self.directed_abs_links:
            normal_router = pv_link.intermediate.actual_node
            if isinstance(normal_router, SimNormalRouter):
                avg_corrupt_ratio = float(normal_router.corrupt_ratio_start + normal_router.corrupt_ratio_end) / 2.0 / 1000000.0
                if avg_corrupt_ratio > (1 - minimum_delivery_ratio):
                    regret_value += 1
        # print(f"regret_value = {regret_value}", flush=True)
        return regret_value

    def calculate_score(self):
        """
        计算链路的得分 (换掉一条后面的链路更不重要，得分越高的链路, 越靠前)
        self.available_paths = sorted(self.available_paths, key=lambda path: path.score)
        """
        score = 0.0
        for index, directed_pv_link in enumerate(self.directed_abs_links):
            # 假设 actual_node 是 SimNormalRouter 并具有这些属性
            intermediate_node = directed_pv_link.intermediate.actual_node
            # Python 中可以直接使用 getattr 避免类型转换失败，此处假设该节点就是 NormalRouter
            if isinstance(intermediate_node, SimNormalRouter):
                avg_corrupt_ratio = (intermediate_node.corrupt_ratio_start + intermediate_node.corrupt_ratio_end) / 2
                score += avg_corrupt_ratio
            else:
                raise RuntimeError("unsupported node type")
        self.score = score



