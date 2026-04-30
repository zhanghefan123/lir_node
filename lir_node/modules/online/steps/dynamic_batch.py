from typing import List
from apps.network.lir import udp_other_client as uocm
from modules.online.steps import simulator as sem
from modules.online.types import types as tm
from modules.online.steps import osmd_step as osm
import datetime
import math
import time

if __name__ != "__main__":
    from modules.kernel import kernel_configurator as kcm


def forward_real_packets_or_retrieve_acks_for_dynamic_batch(sm: sem.Simulator) -> (List[int], List[int]):
    """
    进行真实的数据包的转发
    :return:
    """
    # 1. 首先判断是否需要进行 retrieve
    (epoch_id, collect_enough_ack_time_elapsed, reach_timeout_time_elapsed, number_of_sampling_packets,
     number_of_unsamping_packets, received_ack_counts,
     expected_ack_counts, retrieved) = kcm.kernel_config_loader.retrieve_kernel_information_for_dynamic_batch()
    # 2. 如果成功进行了返回, 那么进行 [received_acks, expected_acks] 的返回
    if retrieved:
        # 进行 ack 的更新
        sm.latest_acks_epoch = epoch_id
        sm.sim_graph.collect_enough_ack_time_elapsed_list.append(collect_enough_ack_time_elapsed)
        sm.sim_graph.reach_timeout_time_elapsed_list.append(reach_timeout_time_elapsed)
        sm.sim_graph.epoch_sampling_packets_list.append(number_of_sampling_packets)
        sm.sim_graph.epoch_unsampling_packets_list.append(number_of_unsamping_packets)
        # 进行当前 epoch 的打印
        # print(f"latest ack epoch: {sm.latest_acks_epoch}, currnet_epoch_sent_packets: {current_epoch_sent_packets}, received ack counts: {received_ack_counts}, expected ack counts: {expected_ack_counts}", flush=True)
        # 进行结果的返回
        return received_ack_counts, expected_ack_counts
    # 3. 如果没有成功返回, 那么进行数据包的发送 (不用进行路径的下发, 沿之前的路径进行发送即可)
    sm.client_detailed_info.batch_size = sm.simulator_params.mini_batch_size
    udp_other_client = uocm.UdpOtherClient(sm.client_detailed_info)
    udp_other_client.start()
    return [], []


def init_dynamic_batch(sm: sem.Simulator):
    kcm.kernel_config_loader.set_min_ack_for_rtt_estimation(sm.simulator_params.min_ack_for_rtt_estimation)


def start_dynamic_batch(sm: sem.Simulator):
    # 1. 让所有的路径的概率相同 (并计算出每条边的概率)
    osm.init_all_edges_probabilities(sm)

    # 2. 进入循环
    while True:
        if sm.latest_acks_epoch == sm.simulator_params.number_of_epochs:
            break

        if sm.retrieved_acks:
            # ----------------------- 根据更新后的模型进行路径的选择  -----------------------
            start_time = datetime.datetime.now()  # 记录决策开始时间
            osm.set_current_edges_probability(sm)  # 设置每条边的概率
            path_mapping = osm.decompose_to_get_path_probabilities(sm)  # 根据边概率进行流分解
            current_epoch_selected_path = osm.determine_current_epoch_selected_path(sm,
                                                                                    path_mapping)  # 决策当前路径 (原代码此处注释为 2.2，应为确定本轮路径)
            determine_path_time_elapsed = (datetime.datetime.now() - start_time).total_seconds()  # 记录经过了多少时间
            sm.sim_graph.determine_path_time_elapsed_list.append(determine_path_time_elapsed)  # 进行list的更新
            # ----------------------- 根据更新后的模型进行路径的选择  -----------------------

            # ----------------------- 进行所选择的路径以及最优路径更新 -----------------------
            current_epoch = sm.latest_acks_epoch + 1
            updated = osm.update_according_to_scheduled_list(sm, current_epoch)
            if updated or (sm.best_path is None):
                sm.best_path = osm.recalculate_score_and_find_best_path(sm)
            sm.sim_graph.best_paths.append(sm.best_path)
            sm.sim_graph.selected_paths.append(current_epoch_selected_path)
            sm.sim_graph.retrieved_timestamp_list.append(time.time())
            current_regret = current_epoch_selected_path.calculate_regret(
                sm.simulator_params.minimum_delivery_ratio)
            sm.sim_graph.accumulate_current_regret += current_regret
            sm.sim_graph.regret_list.append(sm.sim_graph.accumulate_current_regret / float(current_epoch))
            if (sm.latest_selected_path is None) or (sm.latest_selected_path.description != current_epoch_selected_path.description):
                sm.latest_selected_path = current_epoch_selected_path
                # 获取 mini_batch_size
                mini_batch_size = sm.simulator_params.mini_batch_size
                # 进行路径的设置
                kcm.kernel_config_loader.set_sec_path_mab_route_for_dynamic_batch(current_epoch_selected_path, mini_batch_size)
            elif sm.latest_selected_path.description == current_epoch_selected_path.description:
                # 利用之前的路径但是需要创建新的 sfse 和 hbase
                kcm.kernel_config_loader.reset_sec_path_mab_route_for_dynamic_batch()
            # ----------------------- 进行所选择的路径以及最优路径更新 -----------------------
        else:
            current_epoch_selected_path = sm.latest_selected_path

        # 2.4.2 发送一批数据包
        if sm.running_type == tm.RunningType.RealTest:
            received_ack_counts, expected_ack_counts = forward_real_packets_or_retrieve_acks_for_dynamic_batch(sm)
            if len(received_ack_counts) == 0:
                sm.retrieved_acks = False
                continue
            else:
                sm.retrieved_acks = True
        else:
            raise ValueError("unsupported real or virtual type: %d", sm.running_type)

        stat_update_model_time = datetime.datetime.now()

        # 2.4.3 进行当前的计算的路径的更新
        if sm.running_type == tm.RunningType.RealTest:
            current_calculated_path = current_epoch_selected_path
        else:
            raise ValueError("unsupported real or virtual type: %d", sm.running_type)

        # 2.4.4 计算传输失败率
        directed_abs_links, directed_abs_links_mapping = current_calculated_path.get_directed_abs_links()
        for index in range(len(received_ack_counts)):
            if index == 0:
                estimated_legal_ratio = min(float(received_ack_counts[index] / expected_ack_counts[index]), 1.0)
            else:
                # (89 / 100) / (84 / 100)

                # 探测 a 用了 50 个包, 探测 b 用了 45 个包, 对于 ----- a->b -----, 结果 a 返回了 40 个包, b 返回了 30 个包
                # 说明存在多少的包到达了 a, 40 / 50, 存在多少的包到达了 b,  30 / 45, 那么传输成功率就认为是 (30 / 45) / (40 / 50)
                delivery_ratio_before = float(received_ack_counts[index - 1]) / float(
                    expected_ack_counts[index - 1])  # 84 / 100
                delivery_ratio_current = float(received_ack_counts[index]) / float(
                    expected_ack_counts[index])  # 89 / 100
                numerator = delivery_ratio_current
                denominator = delivery_ratio_before
                if denominator == 0:
                    estimated_legal_ratio = 0
                else:
                    estimated_legal_ratio = min(numerator / denominator, 1.0)
            directed_abs_links[index].illegal_ratios.append(1 - estimated_legal_ratio)

        # 未进行探测的链路的非法率为 0
        for directed_abs_link in sm.sim_graph.sim_directed_abs_links:
            if directed_abs_link.description not in directed_abs_links_mapping:
                directed_abs_link.illegal_ratios.append(0.0)

        # 2.4.5 计算无偏估计
        for directed_pv_link in sm.sim_graph.sim_directed_abs_links:
            if directed_pv_link.description in directed_abs_links_mapping:
                # illegal_ratio = directed_pv_link.illegal_ratios[epoch - 1]
                illegal_ratio = directed_pv_link.illegal_ratios[-1]
                rectified_loss = osm.calculate_rectified_loss(sm, illegal_ratio,
                                                              directed_pv_link.explore_probabilities[-1])
                directed_pv_link.rectified_losses.append(rectified_loss)
            else:
                directed_pv_link.rectified_losses.append(0.0)

        # 2.4.6 更新各个节点的权重
        for directed_pv_link in sm.sim_graph.sim_directed_abs_links:
            # explore_probabilities 由于路径分可能会为 0, 即一条边其被选中的概率其实不为0, 但是由于进行路径分解其变为了0, rectified_loss 为0, epoch 应该为一个比较大的值
            current_epoch_weight = directed_pv_link.explore_probabilities[-1] * math.exp(
                -sm.simulator_params.learning_rate * directed_pv_link.rectified_losses[-1])
            directed_pv_link.weights.append(current_epoch_weight)

        # 2.4.7 将权重重新进行投影
        source_node = sm.sim_graph.sim_abstract_nodes_mapping[
            sm.sim_graph.graph_params.source_dest_params.source]
        dest_node = sm.sim_graph.sim_abstract_nodes_mapping[
            sm.sim_graph.graph_params.source_dest_params.destination]
        osm.projection_back_to_legal_plane(sm, source_node, dest_node)

        # 获取更新模型的时间
        update_model_time_elapsed = (datetime.datetime.now() - stat_update_model_time).total_seconds()
        sm.sim_graph.update_model_time_elapsed_list.append(update_model_time_elapsed)
