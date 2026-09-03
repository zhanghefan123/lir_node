"""
Fixed-batch 路径级 MAB（Path-bandit）：每条路径是一个 arm。

与边级 OSMD（对每条 pv-link 更新并做流分解/投影）不同，本文件实现的是“路径级” OSMD：
- **选择**：直接按路径概率 \(p_t(\text{path})\) 采样一条路径下发到内核。
- **反馈**：内核返回该 epoch 的端到端 ACK（最后一个采样点）的 retrieved/expected 计数。
- **更新**：把端到端非法率映射为 loss，并按 OSMD 规则更新路径权重，再投影回概率单纯形。

关键约束/假设：
- 由于 fixed-batch 可能一次 retrieve 回多个 epoch 的 feedback，必须使用“发送该 epoch 时的探索概率”做无偏校正，
  因此每条路径在发送时都会记录一份 `sending_epoch_probabilities`。
- bandit 反馈：每次只观测到被选中路径的端到端损失，未被选中路径的损失按 0 记（与边级 full-information 不同）。
"""
import datetime
import math
import time
from typing import List

from apps.network.lir import udp_other_client as uocm
from modules.kernel import kernel_configurator as kcm
from modules.online.entities import sim_path as sppm
from modules.online.entities.retrieved_feedback import RetrievedPathMabFeedback
from modules.online.steps import osmd_step as osm
from modules.online.steps import simulator as sem


def forward_real_packets_or_retrieve_acks_for_fixed_batch_path_mab(
        sm: sem.Simulator,
        current_epoch_selected_path: sppm.SimPath,
) -> List[RetrievedPathMabFeedback]:
    """
    fixed-batch 的“发送/回收”二阶段逻辑：

    - 若 `sm.old_epoch_path_list` 非空：优先尝试从内核 retrieve ACK。
      - 若 retrieve 成功拿到 1+ 个 epoch 的反馈，则把这些 feedback 依次与当时发送的路径绑定，并返回。
      - 若拿不到反馈（例如条件未满足），则走发送分支。
    - 若没有待回收的 epoch：走发送分支，下发路径并发送一批数据包，返回空列表。

    返回：
    - `[]` 表示本次只是发送了一个新 epoch，模型不更新。
    - `List[RetrievedPathMabFeedback]` 表示拿到了反馈，需要进行模型更新。
    """
    if len(sm.old_epoch_path_list) > 0:
        retrieved_feedbacks, received_string = kcm.kernel_config_loader.retrieve_kernel_information_for_path_mab()
        sm.sim_graph.received_string_list.append(received_string)
        if len(retrieved_feedbacks) > 0:
            for retrieved_feedback in retrieved_feedbacks:
                old_epoch_selected_path = sm.old_epoch_path_list.pop(0)
                retrieved_feedback.retrieved_epoch_selected_path = old_epoch_selected_path
                sm.latest_acks_epoch = retrieved_feedback.epoch_id
                sm.sim_graph.sending_elapsed_list.append(retrieved_feedback.sending_time_elapsed)
                sm.sim_graph.packet_sending_rate.append(
                    float(sm.client_detailed_info.batch_size)
                    / (retrieved_feedback.sending_time_elapsed / 1000 / 1000)
                )
                sm.sim_graph.retrieved_timestamp_list.append(time.time())
            return retrieved_feedbacks

    # ---- 发送分支：下发当前 epoch 路径并发送批量数据包 ----
    sm.sim_graph.sending_timestamp_list.append(time.time())
    sm.old_epoch_path_list.append(current_epoch_selected_path)

    batch_size = sm.simulator_params.number_of_pkts_per_link_or_batch_size * (
            len(current_epoch_selected_path.pv_routers) + 1
    )
    sm.latest_selected_path = current_epoch_selected_path
    kcm.kernel_config_loader.set_sec_path_mab_route_for_path_mab(
        current_epoch_selected_path, batch_size
    )

    sm.client_detailed_info.batch_size = batch_size
    if sm.udp_other_client is None:
        sm.udp_other_client = uocm.UdpOtherClient(sm.client_detailed_info)
    sm.udp_other_client.start()

    sm.latest_sending_epoch += 1
    sm.sim_graph.sending_epochs.append(sm.latest_sending_epoch)
    sm.sim_graph.relied_acks_epochs.append(sm.latest_acks_epoch)
    sm.sim_graph.selected_paths.append(current_epoch_selected_path)

    # 记录“发送该 epoch 时”的路径探索概率，用于后续做无偏校正（retrieve 可能滞后且一次回多个 epoch）。
    for sim_path in sm.sim_graph.available_paths:
        sim_path.sending_epoch_probabilities.append(sim_path.explore_probabilities[-1])
    return []


def start_fixed_batch_path_mab(sm: sem.Simulator):
    """
    路径级 OSMD 主循环。

    - `sm.retrieved_acks == True`：说明上一轮拿到了 feedback，概率已更新，可以重新采样新路径。
    - `sm.retrieved_acks == False`：说明上一轮只是发送但还没拿到 feedback，本轮沿用上一条路径继续发/或先尝试 retrieve。
    """
    osm.init_all_paths_probabilities(sm)

    while True:
        if sm.sync_timestamp + sm.simulator_params.experiment_time_elapsed_ms <= (time.time() * 1000):
            break
        else:
            pass
            # print(f"sync_timestamp: {sm.sync_timestamp} | experiment_time_elapsed: {sm.simulator_params.experiment_time_elapsed_ms} "
            #       f"| current_time: {time.time() * 1000}", flush=True)

        if sm.retrieved_acks:
            start_time = datetime.datetime.now()
            # 直接按路径概率采样（与边级版本“先设边概率→流分解→再采样路径”不同）
            current_epoch_selected_path = osm.determine_current_epoch_selected_path_direct(sm)
            determine_path_time_elapsed = (datetime.datetime.now() - start_time).total_seconds()
            sm.sim_graph.determine_path_time_elapsed_list.append(determine_path_time_elapsed)
        else:
            # 没拿到新反馈时，保持路径不变（避免 userspace 模型超前于 kernel 可回收的 epoch）
            current_epoch_selected_path = sm.latest_selected_path

        retrieved_feedbacks = forward_real_packets_or_retrieve_acks_for_fixed_batch_path_mab(
            sm, current_epoch_selected_path
        )
        if len(retrieved_feedbacks) == 0:
            sm.retrieved_acks = False
            continue
        sm.retrieved_acks = True

        stat_update_model_time = datetime.datetime.now()
        # 可能一次 retrieve 到多个 epoch 的 feedback，这里逐个处理并按收到顺序更新模型。
        for retrieved_feedback in retrieved_feedbacks:
            gap = sm.latest_sending_epoch - retrieved_feedback.epoch_id
            sm.gap_list.append(gap)
            current_calculated_path = retrieved_feedback.retrieved_epoch_selected_path

            # 端到端 delivery ratio：只使用最后一个采样点（path_mab 的反馈结构即为 end-to-end）
            if retrieved_feedback.expected_ack_count > 0:
                delivery_ratio = min(
                    float(retrieved_feedback.retrieved_ack_count)
                    / float(retrieved_feedback.expected_ack_count),
                    1.0,
                )
            else:
                delivery_ratio = 0.0
            illegal_ratio = 1.0 - delivery_ratio
            current_calculated_path.illegal_ratios.append(illegal_ratio)

            send_epoch_prob_idx = retrieved_feedback.epoch_id - 1
            path_explore_prob_at_send = current_calculated_path.sending_epoch_probabilities[send_epoch_prob_idx]
            # 无偏校正：loss / p_send，注意这里必须用发送时的概率而不是“当前已更新后的概率”
            rectified_loss = osm.calculate_rectified_loss(
                sm, illegal_ratio, path_explore_prob_at_send
            )
            current_calculated_path.rectified_losses.append(rectified_loss)

            # bandit 反馈：只有被选择的路径有观测到端到端损失，其余路径损失记 0。
            for sim_path in sm.sim_graph.available_paths:
                if sim_path.path_id != current_calculated_path.path_id:
                    sim_path.illegal_ratios.append(0.0)
                    sim_path.rectified_losses.append(0.0)

            # OSMD：在对偶空间更新每条路径的权重（指数更新），再投影回概率单纯形
            for sim_path in sm.sim_graph.available_paths:
                current_epoch_weight = sim_path.explore_probabilities[-1] * math.exp(
                    -sm.simulator_params.learning_rate * sim_path.rectified_losses[-1]
                )
                sim_path.weights.append(current_epoch_weight)
            osm.projection_paths_to_simplex(sm)

        update_model_time_elapsed = (datetime.datetime.now() - stat_update_model_time).total_seconds()
        sm.sim_graph.update_model_time_elapsed_list.append(update_model_time_elapsed)
