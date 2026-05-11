import os
from typing import List
from dataclasses import dataclass
from defined_types.types import SecPathMabType
from modules.online.steps import simulator as sem
from modules.config import env_loader as elm
from modules.kernel import kernel_configurator as kcm


@dataclass
class DescriptionAndData:
    description: str
    datas: str


# ---------------------------------------------------------
# 辅助函数 (Helper Functions)
# ---------------------------------------------------------

def format_float_slice(values: List[float]) -> str:
    """
    将浮点数列表格式化为逗号分隔的字符串
    对应 Go 里的 fmt.Sprintf("%f", value)
    """
    # f"{v:f}" 默认保留 6 位小数，与 Go 的 %f 行为一致
    return ",".join(f"{v:.10f}" for v in values)


def write_statistics_to_file(destination_dir: str, filename: str,
                             desc_and_datas: List[DescriptionAndData]):
    """将统计数据写入文件"""
    final_string = ""
    for desc_and_data in desc_and_datas:
        final_string += f"{desc_and_data.description}:{desc_and_data.datas}\n"

    file_path = os.path.join(destination_dir, filename)
    # 使用 context manager (with 语句) 自动管理文件关闭
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_string)


def get_packet_sending_rate(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    desc_and_data = DescriptionAndData(
        description="packet_sending_rate",
        datas=format_float_slice(sm.sim_graph.packet_sending_rate)
    )
    result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "packet_sending_rate.txt", result_list)


def get_sending_elapsed_list(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    desc_and_data = DescriptionAndData(
        description="sending_elapsed",
        datas=format_float_slice(sm.sim_graph.sending_elapsed_list)
    )
    result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "sending_elapsed.txt", result_list)


def get_epoch_unsampling_packets_list(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    desc_and_data = DescriptionAndData(
        description="epoch_unsampling_packets",
        datas=format_float_slice(sm.sim_graph.epoch_unsampling_packets_list),
    )
    result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "epoch_unsampling_packets.txt", result_list)


def get_epoch_sampling_packets_list(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    desc_and_data = DescriptionAndData(
        description="epoch_sampling_packets",
        datas=format_float_slice(sm.sim_graph.epoch_sampling_packets_list),
    )
    result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "epoch_sampling_packets.txt", result_list)


def get_sending_timestamp_list(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    desc_and_data = DescriptionAndData(
        description="sending_timestamp_list",
        datas=format_float_slice(sm.sim_graph.sending_timestamp_list)
    )
    result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "sending_timestamps.txt", result_list)


def get_retrieved_timestamp_list(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    desc_and_data = DescriptionAndData(
        description="retrieved_timestamp_list",
        datas=format_float_slice(sm.sim_graph.retrieved_timestamp_list)
    )
    result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "retrieved_timestamps.txt", result_list)


def get_determine_path_time_elapsed(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    desc_and_data = DescriptionAndData(
        description="determine_path_time_elapsed",
        datas=format_float_slice(sm.sim_graph.determine_path_time_elapsed_list)
    )
    result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "determine_path_time_elapsed.txt", result_list)


def get_update_model_time_elapsed(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    desc_and_data = DescriptionAndData(
        description="update_model_time_elapsed",
        datas=format_float_slice(sm.sim_graph.update_model_time_elapsed_list)
    )
    result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "update_model_time_elapsed.txt", result_list)


def get_collect_enough_ack_time_elapsed(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    desc_and_data = DescriptionAndData(
        description="collect_enough_ack_time_elapsed",
        datas=format_float_slice(sm.sim_graph.collect_enough_ack_time_elapsed_list)
    )
    result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "collect_enough_ack_time_elapsed.txt", result_list)


def get_reach_timeout_time_elapsed(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    desc_and_data = DescriptionAndData(
        description="reach_time_out_time_elapsed",
        datas=format_float_slice(sm.sim_graph.reach_timeout_time_elapsed_list)
    )
    result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "reach_timeout_time_elapsed.txt", result_list)


def get_sending_epochs(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    desc_and_data = DescriptionAndData(
        description="sending_epochs",
        datas=format_float_slice(sm.sim_graph.sending_epochs)
    )
    result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "sending_epochs.txt", result_list)


def get_relied_acks_epoch(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    desc_and_data = DescriptionAndData(
        description="relied_acks_epoch",
        datas=format_float_slice(sm.sim_graph.relied_acks_epochs)
    )
    result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "relied_acks_epoch.txt", result_list)


def get_pv_links_illegal_ratios(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    for abs_link in sm.sim_graph.sim_directed_abs_links:
        desc_and_data = DescriptionAndData(
            description=abs_link.description,
            datas=format_float_slice(abs_link.illegal_ratios)
        )
        result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "pv_links_illegal_ratio.txt", result_list)


def get_pv_links_weights(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    for pv_link in sm.sim_graph.sim_directed_abs_links:
        desc_and_data = DescriptionAndData(
            description=pv_link.description,
            datas=format_float_slice(pv_link.weights)
        )
        result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "pv_links_weights.txt", result_list)


def get_pv_links_explore_probabilities(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    for pv_link in sm.sim_graph.sim_directed_abs_links:
        desc_and_data = DescriptionAndData(
            description=pv_link.description,
            datas=format_float_slice(pv_link.explore_probabilities)
        )
        result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "pv_links_explore_probabilities.txt", result_list)


def get_selected_path(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    # 使用 Python 的列表推导式直接提取并拼接 PathId
    path_ids = [str(sim_path.path_id) for sim_path in sm.sim_graph.selected_paths]
    final_string = ",".join(path_ids)

    desc_and_data = DescriptionAndData(
        description="selected path",
        datas=final_string
    )
    write_statistics_to_file(destination_dir, "selected_paths.txt", [desc_and_data])

    # ---------------------------------------------------------
    # 主导出入口 (Main Entry Point)
    # ---------------------------------------------------------


def get_sending_epoch_probabilities(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    for pv_link in sm.sim_graph.sim_directed_abs_links:
        desc_and_data = DescriptionAndData(
            description=pv_link.description,
            datas=format_float_slice(pv_link.sending_epoch_probabilities)
        )
        result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "sending_epoch_probabilities.txt", result_list)


def get_deda_accumulated_loss_z_list(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    for pv_link in sm.sim_graph.sim_directed_abs_links:
        desc_and_data = DescriptionAndData(
            description=pv_link.description,
            datas=format_float_slice(pv_link.accumulated_loss_z_list)
        )
        result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "loss_z.txt", result_list)


def get_deda_accumulated_weighted_loss_m_list(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    for pv_link in sm.sim_graph.sim_directed_abs_links:
        desc_and_data = DescriptionAndData(
            description=pv_link.description,
            datas=format_float_slice(pv_link.weighted_accumulated_loss_m_list)
        )
        result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "weighted_loss_m.txt", result_list)


def get_deda_learning_rate_list(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    desc_and_data = DescriptionAndData(
        description="learning_rate",
        datas=format_float_slice(sm.learning_rate_list)
    )
    result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "learning_rate_list.txt", result_list)


def get_per_packet_selected_path_list(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    desc_and_data = DescriptionAndData(
        description="per_packet_selected_path",
        datas=format_float_slice(sm.sim_graph.per_packet_selected_path)
    )
    result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "per_packet_selected_path_list.txt", result_list)


def get_per_packet_best_path_list(sm: sem.Simulator, destination_dir: str):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    result_list = []
    desc_and_data = DescriptionAndData(
        description="per_packet_selected_path",
        datas=format_float_slice(sm.sim_graph.per_packet_selected_path)
    )
    result_list.append(desc_and_data)
    write_statistics_to_file(destination_dir, "per_packet_best_path_list.txt", result_list)


def get_per_packet_info(sm: sem.Simulator, destination_output_dir: str):
    final_list = []
    while True:
        result_string = kcm.kernel_config_loader.get_per_packet_information()
        if result_string != "":
            str_list = result_string.split(",")
            value_list = [int(item) for item in str_list]
            final_list.extend(value_list)
            if len(value_list) != 400 * 2:
                break
        else:
            break
    for i in range(0, len(final_list), 2):
        sm.sim_graph.per_packet_selected_path.append(final_list[i])
        sm.sim_graph.per_packet_best_path.append(final_list[i])
    print(f"total send packets: {len(final_list) / 2}", flush=True)
    get_per_packet_selected_path_list(sm, f"{destination_output_dir}/per_packet")
    get_per_packet_best_path_list(sm, f"{destination_output_dir}/per_packet")


def get_statistics(sm: sem.Simulator, destination_output_dir: str):
    """get simulator statistics after the end of simulation"""
    if elm.env_loader.sec_path_mab_type == SecPathMabType.SEC_PATH_MAB_STRATEGY_FIXED_BATCH:
        print("get fixed batch experimental result", flush=True)
        get_sending_epochs(sm, f"{destination_output_dir}/fixed")
        get_relied_acks_epoch(sm, f"{destination_output_dir}/fixed")
        get_sending_timestamp_list(sm, f"{destination_output_dir}/fixed")
        get_sending_epoch_probabilities(sm, f"{destination_output_dir}/fixed")
        get_selected_path(sm, f"{destination_output_dir}/fixed")
        get_retrieved_timestamp_list(sm, f"{destination_output_dir}/fixed")
    else:
        print("get dynamic batch experimental result", flush=True)
        get_epoch_unsampling_packets_list(sm, f"{destination_output_dir}/dynamic")
        get_epoch_sampling_packets_list(sm, f"{destination_output_dir}/dynamic")
        get_collect_enough_ack_time_elapsed(sm, f"{destination_output_dir}/dynamic")
        get_reach_timeout_time_elapsed(sm, f"{destination_output_dir}/dynamic")
        get_selected_path(sm, f"{destination_output_dir}/dynamic")
        get_retrieved_timestamp_list(sm, f"{destination_output_dir}/dynamic")

    print("get common part experimental result", flush=True)
    get_determine_path_time_elapsed(sm, f"{destination_output_dir}/common/performance")
    get_update_model_time_elapsed(sm, f"{destination_output_dir}/common/performance")
    get_packet_sending_rate(sm, f"{destination_output_dir}/common/performance")
    get_sending_elapsed_list(sm, f"{destination_output_dir}/common/performance")

    get_pv_links_weights(sm, f"{destination_output_dir}/common/links")
    get_pv_links_illegal_ratios(sm, f"{destination_output_dir}/common/links")
    get_pv_links_explore_probabilities(sm, f"{destination_output_dir}/common/links")

    if sm.simulator_params.enable_deda_algorithm:
        print("get deda result", flush=True)
        get_deda_accumulated_loss_z_list(sm, f"{destination_output_dir}/deda")
        get_deda_accumulated_weighted_loss_m_list(sm, f"{destination_output_dir}/deda")
        get_deda_learning_rate_list(sm, f"{destination_output_dir}/deda")
