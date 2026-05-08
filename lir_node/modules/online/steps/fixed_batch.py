from modules.online.steps import fixed_batch_normal as fbnm
from modules.online.steps import fixed_batch_deda as fbdm
from modules.online.steps import simulator as sem


def start_fixed_batch(sm: sem.Simulator):
    if sm.simulator_params.enable_deda_algorithm:
        fbdm.start_fixed_batch_deda(sm)
    else:
        fbnm.start_fixed_batch_normal(sm)
