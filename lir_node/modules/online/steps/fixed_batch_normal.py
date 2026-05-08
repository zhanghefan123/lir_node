import datetime
from modules.online.entities.retrieved_feedback import RetrievedFeedback
from modules.online.steps import simulator as sem
from modules.online.entities import sim_path as sppm
from typing import List
from tools import count as cm
from apps.network.lir import udp_other_client as uocm
from modules.online.steps import osmd_step as osm
import math
import time
from modules.kernel import kernel_configurator as kcm


def forward_real_packets_or_retrieve_acks_for_fixed_batch_normal(sm: sem.Simulator,
                                                          current_epoch_selected_path: sppm.SimPath) -> List[RetrievedFeedback]:
    """
    进行真实的数据包的转发
    :return:
    """
    # 首先判断是否需要进行 retrieve
    # --------------------------------------------------------------------------------------------------------------------------------------------
    if len(sm.old_epoch_path_list) > 0:
        retrieved_feedbacks = kcm.kernel_config_loader.retrieve_kernel_information_for_fixed_batch()
        if len(retrieved_feedbacks) > 0:  # 如果大于 0 说明进行了 feedback 的获取
            for retrieved_feedback in retrieved_feedbacks:
                old_epoch_selected_path = sm.old_epoch_path_list.pop(0)
                retrieved_feedback.retrieved_epoch_selected_path = old_epoch_selected_path
                # 进行状态的更新
                sm.latest_acks_epoch = retrieved_feedback.epoch_id
                sm.sim_graph.sending_elapsed_list.append(retrieved_feedback.sending_time_elapsed)
                sm.sim_graph.packet_sending_rate.append(float(sm.client_detailed_info.batch_size) / (retrieved_feedback.sending_time_elapsed / 1000 / 1000))
                sm.sim_graph.retrieved_timestamp_list.append(time.time())
            return retrieved_feedbacks

    # 如果当前选择进行发送数据包
    sm.sim_graph.sending_timestamp_list.append(time.time())

    # 添加落后的路径的选择
    sm.old_epoch_path_list.append(current_epoch_selected_path)

    # 如果 retrieve 不回来就进行 sending
    # --------------------------------------------------------------------------------------------------------------------------------------------
    delivery_ratio_list = []
    for simDirectedPvLink in current_epoch_selected_path.directed_abs_links:
        if len(simDirectedPvLink.illegal_ratios) == 0:
            delivery_ratio_list.append(1.0)
        else:
            delivery_ratio_list.append((1 - simDirectedPvLink.illegal_ratios[-1]))

    # 进行返回
    if (sm.latest_selected_path is None) or (sm.latest_selected_path.description != current_epoch_selected_path.description):
        # 获取批次大小
        batch_size = sm.simulator_params.number_of_pkts_per_link * (
                len(current_epoch_selected_path.pv_routers) + 1)
        # 计算每个节点的采样大小
        counts = cm.calc_cascade_sample_counts(batch_size, delivery_ratio_list)
        # 如果当前内核路径为空, 或者当前内核路径和当前选择的路径不同
        sm.latest_selected_path = current_epoch_selected_path
        # 进行路径的下发
        kcm.kernel_config_loader.set_sec_path_mab_route_for_fixed_batch(current_epoch_selected_path,
                                                                        batch_size,
                                                                        counts)
    else:
        # 如果路径相同, 只需要进行路径的重置即可
        # 获取批次大小
        batch_size = sm.simulator_params.number_of_pkts_per_link * (
                len(current_epoch_selected_path.pv_routers) + 1)
        # 计算每个节点的采样大小
        counts = cm.calc_cascade_sample_counts(batch_size, delivery_ratio_list)
        # 进行路径的下发
        kcm.kernel_config_loader.reset_sec_path_mab_route_for_fixed_batch(batch_size, counts)

    # 进行实际的数据包的发送
    sm.client_detailed_info.batch_size = sm.simulator_params.number_of_pkts_per_link * (
            len(current_epoch_selected_path.pv_routers) + 1)
    udp_other_client = uocm.UdpOtherClient(sm.client_detailed_info)
    udp_other_client.start()
    # --------------------------------------------------------------------------------------------------------------------------------------------
    # 进行发送 epoch, relied_epoch, 选择的路径的更新
    # --------------------------------------------------------------------------------------------------------------------------------------------
    sm.sim_graph.sending_epochs.append(sm.latest_sending_epoch)
    sm.latest_sending_epoch += 1
    sm.sim_graph.relied_acks_epochs.append(sm.latest_acks_epoch)
    sm.sim_graph.selected_paths.append(current_epoch_selected_path)
    # --------------------------------------------------------------------------------------------------------------------------------------------
    # 按照 scheduled_list 进行更新
    # --------------------------------------------------------------------------------------------------------------------------------------------
    updated = osm.update_according_to_scheduled_list(sm, sm.latest_sending_epoch)
    # --------------------------------------------------------------------------------------------------------------------------------------------
    # 进行路径的损失值的更新
    # --------------------------------------------------------------------------------------------------------------------------------------------
    if updated or (sm.best_path is None):
        sm.best_path = osm.recalculate_score_and_find_best_path(sm)
    sm.sim_graph.best_paths.append(sm.best_path)
    # --------------------------------------------------------------------------------------------------------------------------------------------
    # 如果当前选择的路径和 best path 不一致的话, 那么 regret 进行 + 1 的操作
    # --------------------------------------------------------------------------------------------------------------------------------------------
    current_regret = current_epoch_selected_path.calculate_regret(sm.simulator_params.minimum_delivery_ratio)
    sm.sim_graph.accumulate_current_regret += current_regret
    sm.sim_graph.regret_list.append(sm.sim_graph.accumulate_current_regret / float(sm.latest_sending_epoch))
    # --------------------------------------------------------------------------------------------------------------------------------------------
    # 完成之后再检查一次
    return []


def start_fixed_batch_normal(sm: sem.Simulator):
    # 1. 让所有的路径的概率相同 (并计算出每条边的概率)
    osm.init_all_edges_probabilities(sm)  # 这里面会将所有的链路的概率初始化为 0.5, 只进行一次

    # 2. 进入循环
    while True:
        if sm.latest_acks_epoch == sm.simulator_params.number_of_epochs:
            break

        # 2.2 判断是否取回了 ack (case 1: 如果取回了 ack, 模型的概率变化了, 需要进行重新的选路) (case 2: 如果没有取回 ack, 模型的概率没有变化依然选之前的路径)
        if sm.retrieved_acks:
            start_time = datetime.datetime.now()  # 记录选路开始时间
            osm.set_current_edges_probability(sm)  # 设置每条边的概率
            path_mapping = osm.decompose_to_get_path_probabilities(sm)  # 进行流分解
            current_epoch_selected_path = osm.determine_current_epoch_selected_path(sm, path_mapping)  # 输出当前应该选择的路径
            determine_path_time_elapsed = (datetime.datetime.now() - start_time).total_seconds()  # 记录选路花费时间
            sm.sim_graph.determine_path_time_elapsed_list.append(determine_path_time_elapsed)  # 填充花费时间到列表之中
        else:
            current_epoch_selected_path = sm.latest_selected_path

        # 2.3 case1: 进行数据包的发送 / case2: 进行一系列 ack 的取回
        retrieved_feedbacks = forward_real_packets_or_retrieve_acks_for_fixed_batch_normal(sm, current_epoch_selected_path)
        if len(retrieved_feedbacks) == 0:
            sm.retrieved_acks = False  # 如果只是进行数据包的发送, 那么 continue, 模型以及路径不变
            continue
        else:
            sm.retrieved_acks = True  # 如果 retrieve 到了不止一个 epoch 的 response, 那么模型需要改变, 路径也需要改变

        # 2.4 记录模型更新开始时间
        stat_update_model_time = datetime.datetime.now()

        for retrieved_feedback in retrieved_feedbacks:
            gap = sm.latest_sending_epoch - retrieved_feedback.epoch_id  # 进行 gap 的计算
            sm.gap_list.append(gap)  # 进行 gap_list 的更新
            current_calculated_path = retrieved_feedback.retrieved_epoch_selected_path  # 当前计算的路径
            directed_abs_links, directed_abs_links_mapping = current_calculated_path.get_directed_abs_links()  # 获取域间路径以及 mapping
            # 进行所有的反馈的遍历, 从而计算出所选路径的, 每条链路的数据包破坏率
            for index in range(retrieved_feedback.number_of_sample_nodes):
                if index == 0:
                    estimated_legal_ratio = min(float(retrieved_feedback.retrieved_ack_counts[index] / retrieved_feedback.expected_ack_counts[index]), 1.0)
                else:
                    delivery_ratio_before = float(retrieved_feedback.retrieved_ack_counts[index - 1]) / float(
                        retrieved_feedback.expected_ack_counts[index - 1])  # 84 / 100
                    delivery_ratio_current = float(retrieved_feedback.retrieved_ack_counts[index]) / float(
                        retrieved_feedback.expected_ack_counts[index])  # 89 / 100
                    numerator = delivery_ratio_current
                    denominator = delivery_ratio_before
                    if denominator == 0:
                        estimated_legal_ratio = 0
                    else:
                        estimated_legal_ratio = min(numerator / denominator, 1.0)
                directed_abs_links[index].illegal_ratios.append(1 - estimated_legal_ratio)

            # 计算出所有未选择链路的数据包破坏率
            for directed_abs_link in sm.sim_graph.sim_directed_abs_links:
                if directed_abs_link.description not in directed_abs_links_mapping:
                    directed_abs_link.illegal_ratios.append(0.0)

            # 计算无偏估计
            for directed_pv_link in sm.sim_graph.sim_directed_abs_links:
                if directed_pv_link.description in directed_abs_links_mapping:
                    illegal_ratio = directed_pv_link.illegal_ratios[-1]
                    rectified_loss = osm.calculate_rectified_loss(sm, illegal_ratio, directed_pv_link.explore_probabilities[-1])
                    directed_pv_link.rectified_losses.append(rectified_loss)
                else:
                    rectified_loss = 0.0
                    directed_pv_link.rectified_losses.append(rectified_loss)

            # 在对偶空间上进行各个链路的权重的更新
            for directed_pv_link in sm.sim_graph.sim_directed_abs_links:
                if sm.simulator_params.enable_dade_algorithm:
                    learning_rate_modified = sm.simulator_params.learning_rate / math.pow(gap, 0.5)
                    current_epoch_weight = directed_pv_link.explore_probabilities[-1] * math.exp(
                        -learning_rate_modified * directed_pv_link.rectified_losses[-1])
                else:
                    current_epoch_weight = directed_pv_link.explore_probabilities[-1] * math.exp(
                        -sm.simulator_params.learning_rate * directed_pv_link.rectified_losses[-1])
                directed_pv_link.weights.append(current_epoch_weight)

            # 将权重重新进行投影
            source_node = sm.sim_graph.sim_abstract_nodes_mapping[
                sm.sim_graph.graph_params.source_dest_params.source]
            dest_node = sm.sim_graph.sim_abstract_nodes_mapping[
                sm.sim_graph.graph_params.source_dest_params.destination]
            osm.projection_back_to_legal_plane(sm, source_node, dest_node)

            # 获取更新模型的时间
            update_model_time_elapsed = (datetime.datetime.now() - stat_update_model_time).total_seconds()
            sm.sim_graph.update_model_time_elapsed_list.append(update_model_time_elapsed)
