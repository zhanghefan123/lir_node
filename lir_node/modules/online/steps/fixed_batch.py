from modules.online.steps import fixed_batch_normal as fbnm
from modules.online.steps import fixed_batch_normal_throughput as fbntm
from modules.online.steps import fixed_batch_deda as fbdm
from modules.online.steps import simulator as sem
from modules.config import env_loader as elm
from modules.online.types.types import SecPathMabExperimentType


def start_fixed_batch(sm: sem.Simulator):
    if sm.simulator_params.enable_deda_algorithm:
        fbdm.start_fixed_batch_deda(sm)
    else:
        if SecPathMabExperimentType.TYPE_REGRET == elm.env_loader.experiment_type:
            fbnm.start_fixed_batch_normal(sm)
        elif SecPathMabExperimentType.TYPE_THROUGHPUT == elm.env_loader.experiment_type:
            fbntm.start_fixed_batch_normal_throughput(sm)
        else:
            raise ValueError(f"unsupported experiment type: {elm.env_loader.experiment_type}")

