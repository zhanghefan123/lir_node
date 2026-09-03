from modules.config import env_loader as elm
from defined_types import types as dtm
from modules.online.types import types as tm
from modules.online.steps import fixed_batch as fbm
from modules.online.steps import fixed_batch_path_mab as fbpm
from modules.online.steps import dynamic_batch as dbm
from modules.online.steps import simulator as sem
from modules.online.steps import statistics as stam


def start_real(sm: sem.Simulator):
    if elm.env_loader.sec_path_mab_type == dtm.SecPathMabType.SEC_PATH_MAB_STRATEGY_FIXED_BATCH:
        fbm.start_fixed_batch(sm)
    elif elm.env_loader.sec_path_mab_type == dtm.SecPathMabType.SEC_PATH_MAB_STRATEGY_DYNAMIC_BATCH:
        dbm.start_dynamic_batch(sm)
    else:
        fbpm.start_fixed_batch_path_mab(sm)

    # 只有在 regret experiment 的时候才需要
    # ---------------------------------------------------------------------------------------------------------------------
    if tm.SecPathMabExperimentType.TYPE_REGRET == elm.env_loader.experiment_type:
        stam.get_statistics(sm, f"/configuration/{elm.env_loader.container_name}/output")
        stam.get_per_packet_info(sm, f"/configuration/{elm.env_loader.container_name}/output")
    elif tm.SecPathMabExperimentType.TYPE_THROUGHPUT == elm.env_loader.experiment_type:
        print("experiment_type == TYPE_THROUGHPUT | do not need to get statistics", flush=True)
    else:
        raise ValueError(f"unsupported experiment_type {elm.env_loader.experiment_type}")
    # ---------------------------------------------------------------------------------------------------------------------
