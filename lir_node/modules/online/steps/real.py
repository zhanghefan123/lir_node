from modules.config import env_loader as elm
from defined_types import types as dtm
from modules.online.steps import fixed_batch as fbm
from modules.online.steps import dynamic_batch as dbm
from modules.online.steps import simulator as sem
from modules.online.steps import statistics as stam


def start_real(sm: sem.Simulator):
    if elm.env_loader.sec_path_mab_type == dtm.SecPathMabType.SEC_PATH_MAB_STRATEGY_FIXED_BATCH:
        fbm.start_fixed_batch(sm)
    else:
        dbm.init_dynamic_batch(sm)
        dbm.start_dynamic_batch(sm)
    stam.get_statistics(sm, f"/configuration/{elm.env_loader.container_name}/output")
    stam.get_per_packet_info(sm, f"/configuration/{elm.env_loader.container_name}/output")

