from modules.online.steps import simulator as sem
from modules.config import env_loader as elm
from defined_types import types as dtm
from tools import count as cm
from modules.online.steps import osmd_step as osm

if __name__ != "__main__":
    from modules.kernel import kernel_configurator as kcm


def start_test(sm: sem.Simulator):
    # 1. 让所有的路径的概率相同 (并计算出每条边的概率)
    osm.init_all_edges_probabilities(sm)

    # 2 设置每条边的当前的概率
    osm.set_current_edges_probability(sm)

    # 3 根据边的概率进行流分解
    path_mapping = osm.decompose_to_get_path_probabilities(sm)

    # 4 决策当前路径 (原代码此处注释为 2.2，应为确定本轮路径)
    current_epoch_selected_path = osm.determine_current_epoch_selected_path(sm, path_mapping)

    # 5. 输出当前所选择的路径
    if elm.env_loader.sec_path_mab_type == dtm.SecPathMabType.SEC_PATH_MAB_STRATEGY_FIXED_BATCH:
        batch_size = (len(current_epoch_selected_path.pv_routers) + 1) * sm.simulator_params.number_of_pkts_per_link
        delivery_ratios = [1] * (len(current_epoch_selected_path.pv_routers) + 1)
        counts = cm.calc_cascade_sample_counts(batch_size, delivery_ratios)
        netlink_string = kcm.kernel_config_loader.set_sec_path_mab_route_for_fixed_batch(
            current_epoch_selected_path,
            batch_size,
            counts)
    else:
        mini_batch_size = sm.simulator_params.mini_batch_size
        netlink_string = kcm.kernel_config_loader.set_sec_path_mab_route_for_dynamic_batch(
            current_epoch_selected_path,
            mini_batch_size
        )

    # 6. 进行 netlink string 的打印
    print(f"netlink_string: {netlink_string}", flush=True)
