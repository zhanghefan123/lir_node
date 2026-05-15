from modules.online.entities import sim_path as sppm
from modules.online.types import types as tm
from modules.online.steps import simulator as sem
from typing import Dict
import random
import math
from modules.online.tools import probs as pm


def recalculate_score_and_find_best_path(sm: sem.Simulator) -> sppm.SimPath:
    for sim_path in sm.sim_graph.available_paths:
        sim_path.calculate_score()
    current_epoch_best_path = \
        sorted(sm.sim_graph.available_paths, key=lambda current_sim_path: current_sim_path.score)[0]
    return current_epoch_best_path


def calculate_rectified_loss(sm: sem.Simulator, illegal_ratio: float, link_explore_prob: float) -> float:
    if sm.rectified_loss_calculating_type == tm.RectifiedLossCalculateType.TYPE_DELIVERY_RATIO:
        estimated_loss = 1 - get_estimated_gain(sm, 1 - illegal_ratio)
        rectified_loss = estimated_loss / link_explore_prob
        return rectified_loss
    else:
        if illegal_ratio > (1 - sm.simulator_params.minimum_delivery_ratio):
            estimated_loss = 1.0
        else:
            estimated_loss = 0.0
        rectified_loss = estimated_loss / link_explore_prob
        return rectified_loss


def get_estimated_gain(sm: sem.Simulator, delivery_ratio: float) -> float:
    min_dr = sm.simulator_params.minimum_delivery_ratio

    # 1. 处理边界：防止 deliveryRatio 为 0 或负数导致 NaN/Inf
    effective_dr = max(delivery_ratio, min_dr)

    # 2. 处理 deliveryRatio 超过 1.0 的情况
    effective_dr = min(effective_dr, 1.0)

    # 3. 计算增益
    return 1 - math.log(effective_dr) / math.log(min_dr)


def init_all_edges_probabilities(sm: sem.Simulator):
    edge_total_probability = 0.0
    number_of_paths = len(sm.sim_graph.available_paths)
    single_path_probability = 1.0 / number_of_paths if number_of_paths > 0 else 0.0
    for sim_path in sm.sim_graph.available_paths:
        for sim_abs_link in sim_path.directed_abs_links:
            if not sim_abs_link.explore_probabilities:
                sim_abs_link.explore_probabilities.append(single_path_probability)
            else:
                sim_abs_link.explore_probabilities[0] += single_path_probability
            edge_total_probability += single_path_probability


def determine_current_epoch_selected_path(sm: sem.Simulator, path_mapping: Dict[str, float]) -> sppm.SimPath:
    path_probabilities = []
    for sim_path in sm.sim_graph.available_paths:
        probability = path_mapping.get(sim_path.description, 0.0)
        path_probabilities.append(probability)

    # 假设 probs.sample_discrete 已经被移植
    selected_path_index = pm.sample_discrete(path_probabilities)
    current_epoch_selected_path = sm.sim_graph.available_paths[selected_path_index]
    return current_epoch_selected_path


def set_current_edges_probability(sm: sem.Simulator):
    for sim_abs_link in sm.sim_graph.sim_directed_abs_links:
        sim_abs_link.current_edge_probability = sim_abs_link.explore_probabilities[-1]


def decompose_to_get_path_probabilities(sm: sem.Simulator) -> Dict[str, float]:
    epsilon = 1e-9
    path_mapping = {}

    while True:
        start_point = sm.sim_graph.sim_abstract_nodes_mapping[
            sm.sim_graph.graph_params.source_dest_params.source]
        current_path_desc = ""
        current_path = []
        minimum_edge_probability = float('inf')

        while True:
            all_output_edges = sm.sim_graph.find_all_output_edges(start_point)
            moved = False

            available_edges = []
            for output_edge in all_output_edges:
                if output_edge.current_edge_probability > epsilon:
                    available_edges.append(output_edge)
                    moved = True

            if not moved:
                break
            else:
                output_edge = random.choice(available_edges)
                source_name = output_edge.source.get_sim_node_name()
                normal_router_name = output_edge.intermediate.get_sim_node_name()

                current_path_desc += f"{source_name}->{normal_router_name}->"
                current_path.append(output_edge)
                start_point = output_edge.target

                if output_edge.current_edge_probability < minimum_edge_probability:
                    minimum_edge_probability = output_edge.current_edge_probability

            start_node_name = start_point.get_sim_node_name()
            if start_node_name == sm.sim_graph.graph_params.source_dest_params.destination:
                current_path_desc += start_node_name
                path_mapping[current_path_desc] = path_mapping.get(current_path_desc,
                                                                   0.0) + minimum_edge_probability

                # 减去概率
                for in_path_link in current_path:
                    in_path_link.current_edge_probability -= minimum_edge_probability
                break

        # 判断当前是否还有链路概率 > 0
        all_zero = True
        for sim_abs_link in sm.sim_graph.sim_directed_abs_links:
            if sim_abs_link.current_edge_probability > epsilon:
                all_zero = False
                break

        if all_zero or not moved:  # 防死循环退出条件
            break

    return path_mapping


def projection_back_to_legal_plane(sm: sem.Simulator, source, destination):
    destination_node_name = destination.get_sim_node_name()

    # 1. 利用逆拓扑排序 (计算 Potential)
    for index in range(len(sm.sim_graph.topology_order) - 1, -1, -1):
        current_node = sm.sim_graph.topology_order[index]

        if current_node.type == tm.SimNetworkNodeType.END_HOST:
            current_node_name = current_node.get_sim_node_name()
            if destination_node_name == current_node_name:
                current_node.potential = 1.0
            else:
                all_output_edges = sm.sim_graph.find_all_output_edges(current_node)
                node_potential = sum(edge.weights[-1] * edge.target.potential for edge in all_output_edges)
                current_node.potential = node_potential

        elif current_node.type == tm.SimNetworkNodeType.PATH_VALIDATION_ROUTER:
            all_output_edges = sm.sim_graph.find_all_output_edges(current_node)
            node_potential = sum(edge.weights[-1] * edge.target.potential for edge in all_output_edges)
            current_node.potential = node_potential
        else:
            raise ValueError(f"Unknown node type for potential calculation: {current_node.type}")

    # 4. 根据潜力计算流量分配 (计算 Flow 和新的 Explore Probabilities)
    source.flow = 1.0

    for index in range(len(sm.sim_graph.topology_order)):
        current_node = sm.sim_graph.topology_order[index]
        all_output_edges = sm.sim_graph.find_all_output_edges(current_node)

        for output_edge in all_output_edges:
            if output_edge.source.potential > 0:
                current_edge_probability = (
                        output_edge.source.flow * output_edge.weights[-1] * output_edge.target.potential /
                        output_edge.source.potential)
                current_edge_probability = max(current_edge_probability, 0.001)
                output_edge.explore_probabilities.append(current_edge_probability)
                output_edge.target.flow += current_edge_probability
            else:
                output_edge.explore_probabilities.append(0.001)

    # 5. 清空所有的 potential 和 flow
    for abstract_node in sm.sim_graph.sim_abstract_nodes:
        abstract_node.potential = 0.0
        abstract_node.flow = 0.0
