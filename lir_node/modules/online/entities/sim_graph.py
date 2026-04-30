import networkx as nx
from typing import List, Dict, Optional, Any
from modules.online.entities import sim_params as spm
from modules.online.entities.sim_abstract_node import SimAbstractNode
from modules.online.tools import resolver as rm
from modules.online.types import types as tm
from modules.online.entities import sim_normal_router as snrm
from modules.online.entities import sim_abstract_node as sanm
from modules.online.entities import sim_path_validation_router as spvrm
from modules.online.entities import sim_directed_link as sdlm
from modules.online.entities import sim_end_host as sehm
from modules.online.entities import sim_path as sspm
from modules.online.entities import sim_params as sppm
from modules.config import interface_loader as ilm


class SimGraph:
    def __init__(self, running_type: str):
        # 记录运行模式
        self.running_type = running_type

        # 使用 networkx 的有向图代替 gonum 的 simple.DirectedGraph
        self.real_graph: nx.DiGraph = nx.DiGraph()

        # ------------------------ 图相关参数 ------------------------
        self.topology_order = []
        self.graph_params: Optional[sppm.GraphParams] = None
        self.source_node: Optional[Any] = None
        self.destination_node: Optional[Any] = None
        self.sim_abstract_nodes: List[sanm.SimAbstractNode] = []
        self.sim_directed_real_links: List[sdlm.SimDirectedRealLink] = []
        self.sim_directed_abs_links: List[sdlm.SimDirectedAbsLink] = []
        self.sim_abstract_nodes_mapping: Dict[str, sanm.SimAbstractNode] = {}
        self.sim_directed_real_links_mapping: Dict[str, sdlm.SimDirectedRealLink] = {}
        self.sim_directed_abs_links_mapping: Dict[str, sdlm.SimDirectedAbsLink] = {}
        self.available_paths: List[sspm.SimPath] = []
        self.available_path_mapping: Dict[str, sspm.SimPath] = {}
        self.all_lir_interfaces = []
        self.all_lir_interfaces_mapping = {}
        # ------------------------ 图相关参数 ------------------------

        # ------------------------ fixed/dynamic batch 共享参数 ------------------------
        self.selected_paths: List[sspm.SimPath] = []
        self.best_paths: List[sspm.SimPath] = []
        self.accumulate_current_regret: float = 0.0
        self.regret_list: List[float] = []
        self.reach_timeout_time_elapsed_list: List[int] = []  # 发送的时间的消耗
        self.retrieved_timestamp_list: List[float] = []  # 时间戳序列
        self.packet_sending_rate: List[float] = []
        # ------------------------ fixed/dynamic batch 共享参数 ------------------------

        # ------------------------ fixed batch 独享运行相关参数 ------------------------
        self.sending_elapsed_list: List[float] = []
        self.sending_epochs: List[int] = []  # 发送包的 epoch
        self.sending_timestamp_list: List[float] = []  # 发送包的 epoch 对应的时间戳
        self.relied_acks_epochs: List[int] = []  # 即当前的 epoch 依赖的是第几个更新
        self.determine_path_time_elapsed_list: List[float] = []  # 决策路径的时间开销
        self.update_model_time_elapsed_list: List[float] = []  # 更新模型的时间开销
        # self.sending_epoch_timestamp_list: List[float] = []  # 发送 batch 的时间开销 (已经有 sending_timestamp_list 了)
        # ------------------------ fixed batch 独享运行相关参数 ------------------------

        # ------------------------ dynamic batch 独享运行相关参数 ------------------------
        self.collect_enough_ack_time_elapsed_list: List[int] = []
        self.epoch_sampling_packets_list: List[int] = []  # 每个 epoch 发送的数据包的数量
        self.epoch_unsampling_packets_list: List[int] = []
        # ------------------------ dynamic batch 独享运行相关参数 ------------------------

    def load_graph_params_from_configuration_file(self, simulation_graph_path: str):
        """从配置文件中加载图的参数信息"""
        try:
            with open(simulation_graph_path, 'r', encoding='utf-8') as f:
                data = f.read()
            self.graph_params = spm.GraphParams.from_json(data)
        except Exception as e:
            raise RuntimeError(f"read or unmarshal topology file failed: {e}")

    def load_nodes_from_node_params(self):
        """从 GraphParams 中的节点参数信息中加载图中的节点"""
        for node_param in self.graph_params.nodes:
            # 假设这些 resolve 方法已被移植
            node_type = rm.resolve_sim_node_type(node_param.type)
            node_name = rm.resolve_sim_node_name(node_param)

            if node_type == tm.SimNetworkNodeType.NORMAL_ROUTER:  # SimNetworkNodeType.NORMAL_ROUTER
                actual_node = snrm.SimNormalRouter(
                    node_name, node_param.index,
                    node_param.corrupt_ratio.start, node_param.corrupt_ratio.end,
                    node_param.corrupt_special_packet_ratio.start, node_param.corrupt_special_packet_ratio.end
                )
                sim_abstract_node = sanm.SimAbstractNode(node_type, actual_node, id_generator=node_param.index)
            elif node_type == tm.SimNetworkNodeType.PATH_VALIDATION_ROUTER:  # SimNetworkNodeType.PATH_VALIDATION_ROUTER
                actual_node = spvrm.SimPathValidationRouter(node_name, node_param.index)
                sim_abstract_node = sanm.SimAbstractNode(node_type, actual_node, id_generator=node_param.index)
            elif node_type == tm.SimNetworkNodeType.END_HOST:  # SimNetworkNodeType.END_HOST
                actual_node = sehm.SimEndHost(node_name, node_param.index)
                sim_abstract_node = sanm.SimAbstractNode(node_type, actual_node, id_generator=node_param.index)
            else:
                print(f"unsupported node type: {node_type}", flush=True)
                raise ValueError(f"unsupported node type: {node_type}")

            # 统一添加到列表、映射和网络图中
            self.sim_abstract_nodes.append(sim_abstract_node)
            self.sim_abstract_nodes_mapping[actual_node.node_name] = sim_abstract_node
            # networkx 可以直接将对象作为节点存入图中
            self.real_graph.add_node(sim_abstract_node)

    def load_source_and_dest(self):
        """从配置文件中加载源和目的节点的信息"""
        source_name = self.graph_params.source_dest_params.source
        dest_name = self.graph_params.source_dest_params.destination

        self.source_node = self.sim_abstract_nodes_mapping.get(source_name)
        if not self.source_node:
            raise ValueError(f"load source failed: {source_name} not found")

        self.destination_node = self.sim_abstract_nodes_mapping.get(dest_name)
        if not self.destination_node:
            raise ValueError(f"load destination failed: {dest_name} not found")

    def load_link_params(self, link_type: str, link_params: List[Any]):
        """处理任意类型的 abstract links"""
        for link_param in link_params:
            source_node_name = rm.resolve_sim_node_name(link_param.source_node)
            intermediate_node_name = rm.resolve_sim_node_name(link_param.intermediate_node)
            target_node_name = rm.resolve_sim_node_name(link_param.target_node)

            source_abs_node = self.sim_abstract_nodes_mapping.get(source_node_name)
            if not source_abs_node:
                raise ValueError(f"cannot find source sim abstract node, name: {source_node_name}")

            intermediate_abs_node = self.sim_abstract_nodes_mapping.get(intermediate_node_name)
            if not intermediate_abs_node:
                raise ValueError(f"cannot find intermediate sim abstract node, name: {intermediate_node_name}")

            target_abs_node = self.sim_abstract_nodes_mapping.get(target_node_name)
            if not target_abs_node:
                raise ValueError(f"cannot find target sim abstract node, name: {target_node_name}")

            link_desc = f"{source_node_name}->{intermediate_node_name}->{target_node_name}"

            link = sdlm.SimDirectedAbsLink(link_type, link_desc, source_abs_node,
                                           intermediate_abs_node,
                                           target_abs_node)

            self.sim_directed_abs_links.append(link)
            if link_desc not in self.sim_directed_abs_links_mapping:
                self.sim_directed_abs_links_mapping[link_desc] = link
            else:
                raise ValueError(f"duplicate link desc: {link_desc}")

    def load_access_links_and_pv_links_params(self):
        """加载图中的 accessLink 和 pvLink"""
        self.load_link_params("SimDirectedAccessLink", self.graph_params.access_links)
        self.load_link_params("SimDirectedPvLink", self.graph_params.pv_links)

    def load_real_links_from_link_params(self):
        """从 GraphParams 中的链路参数信息中加载图中的链路"""
        for link_param in self.graph_params.links:
            source_node_name = rm.resolve_sim_node_name(link_param.source_node)
            target_node_name = rm.resolve_sim_node_name(link_param.target_node)

            source_abs_node = self.sim_abstract_nodes_mapping.get(source_node_name)
            if not source_abs_node:
                raise ValueError(f"cannot find source sim abstract node, name: {source_node_name}")

            target_abs_node = self.sim_abstract_nodes_mapping.get(target_node_name)
            if not target_abs_node:
                raise ValueError(f"cannot find target sim abstract node, name: {target_node_name}")

            real_link_desc = f"{source_node_name}->{target_node_name}"
            real_link = sdlm.SimDirectedRealLink(source_abs_node, target_abs_node)

            # 向 networkx 图中添加有向边，可以附加对象作为属性
            self.real_graph.add_edge(source_abs_node, target_abs_node, real_link=real_link)

            self.sim_directed_real_links.append(real_link)
            if real_link_desc not in self.sim_directed_real_links_mapping:
                self.sim_directed_real_links_mapping[real_link_desc] = real_link
            else:
                raise ValueError(f"duplicate real link description: {real_link_desc}")

    def load_link_identifiers(self):
        """
        加载 link identifiers
        :return:
        """
        self.all_lir_interfaces, self.all_lir_interfaces_mapping = ilm.load_all_interfaces()  # 进行所有的接口的加载

    def find_all_output_edges(self, pv_router_or_end_host: Any) -> List[Any]:
        """
        给定一个 endhost 或 pv router，找到所有的出边 (SimDirectedAbsLink)。
        这个方法依赖于 networkx.DiGraph 来进行拓扑关系的查询。
        """
        all_output_links = []

        try:
            start_node_name = pv_router_or_end_host.get_sim_node_name()
        except Exception as e:
            raise ValueError(f"could not get start sim node name due to {e}")

        # 使用 networkx 的 successors 方法获取所有的下一跳节点 (即 Normal Routers)
        # 这完全等价于 Go 代码中的 simGraph.RealGraph.From(pvRouterOrEndHost.ID())
        for current_normal in self.real_graph.successors(pv_router_or_end_host):

            try:
                normal_node_name = current_normal.get_sim_node_name()
            except Exception as e:
                raise ValueError(f"could not get intermediate sim node name due to {e}")

            # 获取当前 Normal Router 的下一跳 (即目标 PV Router 或 EndHost)
            # 对应 Go 代码中的 outputNormal.Next()
            normal_successors = list(self.real_graph.successors(current_normal))

            # 增加一个安全校验，防止因为拓扑死胡同导致索引越界
            if not normal_successors:
                continue

            next_pv_router_or_end_host = normal_successors[0]

            try:
                dest_node_name = next_pv_router_or_end_host.get_sim_node_name()
            except Exception as e:
                raise ValueError(f"could not get dest sim node name due to {e}")

            # 拼接键值并在 mapping 中查找对应的抽象链路
            link_key = f"{start_node_name}->{normal_node_name}->{dest_node_name}"
            output_link = self.sim_directed_abs_links_mapping.get(link_key)

            if output_link is not None:
                all_output_links.append(output_link)

        return all_output_links

    def find_neighbor_and_next_node(self, start_index: int, node_str_list: List[str]) -> (SimAbstractNode, SimAbstractNode):
        neighbor = self.sim_abstract_nodes_mapping[node_str_list[start_index + 1]]
        for index in range(start_index + 1, len(node_str_list)):
            current_node = self.sim_abstract_nodes_mapping[node_str_list[index]]
            if current_node.type == tm.SimNetworkNodeType.NORMAL_ROUTER:
                continue
            else:
                return neighbor, current_node

    def calculate_available_paths(self):
        available_paths = list(nx.shortest_simple_paths(self.real_graph, self.source_node,
                                                        self.destination_node, weight=None))
        # calculate available paths
        for index, available_path in enumerate(available_paths):
            # create simpath
            sim_path = sspm.SimPath()
            # traverse nodes in path
            for inner_index, current_node in enumerate(available_path):
                sim_path.node_list.append(current_node)
                # if the final -> break
                if inner_index == (len(available_path) - 1):
                    break
                # get link identifier when running type == Real
                if (current_node.type == tm.SimNetworkNodeType.END_HOST) or (current_node.type == tm.SimNetworkNodeType.PATH_VALIDATION_ROUTER):
                    neighbor = available_path[inner_index + 1]
                    interface = self.all_lir_interfaces_mapping[f"{current_node.id}->{neighbor.id}"]
                    sim_path.interfaces.append(interface)
            # update info to fill directedPvLinks and directedPvLinksMapping
            sim_path.update_info(self.sim_directed_abs_links_mapping)
            # get path desc
            sim_path_desc = sim_path.get_path_description()
            sim_path.description = sim_path_desc
            # update available path list
            self.available_paths.append(sim_path)
            self.available_path_mapping[sim_path.description] = sim_path

        # calculate the path score
        for simpath in self.available_paths:
            simpath.calculate_score()

        # sort the paths
        self.available_paths = sorted(self.available_paths, key=lambda path: path.score)

        # set id
        for path_id, available_path in enumerate(self.available_paths):
            available_path.path_id = path_id + 1

        # 进行 available_paths 的打印
        for sim_path in self.available_paths:
            print(f"path_id: {sim_path.path_id}, {sim_path.description}, {sim_path.score}", flush=True)

    def load_available_paths(self):
        for index, available_path_str in enumerate(self.graph_params.available_paths):
            # create path
            sim_path = sspm.SimPath()
            # set id
            sim_path.path_id = index + 1
            # fill node list
            node_str_list = available_path_str.split(",")
            for inner_index, node_str in enumerate(node_str_list):
                # get current node
                current_node = self.sim_abstract_nodes_mapping[node_str]
                sim_path.node_list.append(current_node)
                # if the final break
                if inner_index == (len(node_str_list) - 1):
                    break
                # get link identifier
                if (current_node.type == tm.SimNetworkNodeType.END_HOST) or (
                        current_node.type == tm.SimNetworkNodeType.PATH_VALIDATION_ROUTER):
                    neighbor = self.sim_abstract_nodes_mapping[node_str_list[inner_index + 1]]
                    interface = self.all_lir_interfaces_mapping[f"{current_node.id}->{neighbor.id}"]
                    sim_path.interfaces.append(interface)

            # fill directedPvLinks and directedPvLinksMapping in simPath
            sim_path.update_info(self.sim_directed_abs_links_mapping)
            # get path desc
            sim_path_desc = sim_path.get_path_description()
            sim_path.description = sim_path_desc
            # update available path list
            self.available_paths.append(sim_path)
            self.available_path_mapping[sim_path.description] = sim_path

    def topology_sort(self):
        topo_generator = nx.topological_sort(self.real_graph)
        topo_order = list(topo_generator)
        final_order = []
        for node in topo_order:
            if isinstance(node, sanm.SimAbstractNode):
                if (node.type == tm.SimNetworkNodeType.PATH_VALIDATION_ROUTER) or (
                        node.type == tm.SimNetworkNodeType.END_HOST):
                    final_order.append(node)
            else:
                raise ValueError("unsupported node type")
        self.topology_order = final_order
