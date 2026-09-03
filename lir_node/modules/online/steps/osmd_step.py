from modules.online.entities import sim_path as sppm
from modules.online.types import types as tm
from modules.online.steps import simulator as sem
from typing import Dict, List
import math
from modules.online.tools import probs as pm

_EPSILON = 1e-9


def recalculate_score_and_find_best_path(sm: sem.Simulator) -> sppm.SimPath:
    for sim_path in sm.sim_graph.available_paths:
        sim_path.calculate_score()
    sorted_paths = sorted(sm.sim_graph.available_paths, key=lambda current_sim_path: current_sim_path.score)
    current_score = -1
    current_regret = -1
    for sorted_path in sorted_paths:
        if sorted_path.score > current_score:
            current_regret += 1
            sorted_path.regret_value = current_regret
            current_score = sorted_path.score
        else:
            sorted_path.regret_value = current_regret
    return sorted_paths[0]


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
    path_probabilities = [
        path_mapping.get(sim_path.description, 0.0)
        for sim_path in sm.sim_graph.available_paths
    ]
    selected_path_index = pm.sample_discrete(path_probabilities)
    return sm.sim_graph.available_paths[selected_path_index]


def set_current_edges_probability(sm: sem.Simulator):
    for sim_abs_link in sm.sim_graph.sim_directed_abs_links:
        sim_abs_link.current_edge_probability = sim_abs_link.explore_probabilities[-1]


def _extract_min_path_flow(links: List) -> float:
    """Return min positive edge flow along a path, or 0 if any edge is depleted."""
    min_prob = links[0].current_edge_probability
    if min_prob <= _EPSILON:
        return 0.0
    for link in links[1:]:
        prob = link.current_edge_probability
        if prob <= _EPSILON:
            return 0.0
        if prob < min_prob:
            min_prob = prob
    return min_prob


def _subtract_path_flow(links: List, flow: float) -> int:
    """Subtract flow from path edges; return how many edges became depleted."""
    depleted = 0
    for link in links:
        old_prob = link.current_edge_probability
        new_prob = old_prob - flow
        link.current_edge_probability = new_prob
        if old_prob > _EPSILON and new_prob <= _EPSILON:
            depleted += 1
    return depleted


def decompose_to_get_path_probabilities(sm: sem.Simulator) -> Dict[str, float]:
    """
    将边级探索概率分解为路径概率。

    直接遍历预计算的 available_paths，避免每轮随机游走和 NetworkX 出边查询；
    复杂度从 O(P * L * 图查询) 降为 O(P * L) 每轮分解。
    """
    path_mapping: Dict[str, float] = {}
    available_paths = sm.sim_graph.available_paths
    active_edge_count = sum(
        1 for link in sm.sim_graph.sim_directed_abs_links
        if link.current_edge_probability > _EPSILON
    )

    while active_edge_count > 0:
        extracted = False
        for sim_path in available_paths:
            links = sim_path.directed_abs_links
            if not links:
                continue

            min_prob = _extract_min_path_flow(links)
            if min_prob <= _EPSILON:
                continue

            path_mapping[sim_path.description] = path_mapping.get(sim_path.description, 0.0) + min_prob
            active_edge_count -= _subtract_path_flow(links, min_prob)
            extracted = True
            break

        if not extracted:
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


def init_all_paths_probabilities(sm: sem.Simulator):
    """将每条可用路径初始化为均匀探索概率（路径级 OSMD，每条路径一个 arm）。"""
    number_of_paths = len(sm.sim_graph.available_paths)
    uniform_prob = 1.0 / number_of_paths if number_of_paths > 0 else 0.0
    for sim_path in sm.sim_graph.available_paths:
        sim_path.weights.append(1.0)
        sim_path.explore_probabilities.append(uniform_prob)


def determine_current_epoch_selected_path_direct(sm: sem.Simulator) -> sppm.SimPath:
    """按路径探索概率直接采样，无需边级流分解。"""
    path_probabilities = [sim_path.explore_probabilities[-1] for sim_path in sm.sim_graph.available_paths]
    selected_path_index = pm.sample_discrete(path_probabilities)
    return sm.sim_graph.available_paths[selected_path_index]


def projection_paths_to_simplex(sm: sem.Simulator):
    """将路径权重投影回概率单纯形（K 条路径的 OSMD 投影）。"""
    total_weight = sum(sim_path.weights[-1] for sim_path in sm.sim_graph.available_paths)
    if total_weight <= 0:
        total_weight = 1.0
    for sim_path in sm.sim_graph.available_paths:
        prob = max(sim_path.weights[-1] / total_weight, 0.001)
        sim_path.explore_probabilities.append(prob)
