from modules.config import env_loader as elm
from modules.online.types.types import SecPathMabExperimentType
from modules.online.steps import simulator as sem
from modules.online.steps import dynamic_batch_normal as dbm
from modules.online.steps import dynamic_batch_throughput as dbtm

if __name__ != "__main__":
    from modules.kernel import kernel_configurator as kcm


def init_dynamic_batch(sm: sem.Simulator):
    kcm.kernel_config_loader.set_min_ack_for_rtt_estimation(sm.simulator_params.min_ack_for_rtt_estimation)


def start_dynamic_batch(sm: sem.Simulator):
    init_dynamic_batch(sm)
    if SecPathMabExperimentType.TYPE_REGRET == elm.env_loader.experiment_type:
        dbm.start_dynamic_batch(sm)
    elif SecPathMabExperimentType.TYPE_THROUGHPUT == elm.env_loader.experiment_type:
        dbtm.start_dynamic_batch_throughput(sm)
    else:
        raise ValueError(f"unsupported experiment type: {elm.env_loader.experiment_type}")
