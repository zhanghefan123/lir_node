from modules.online.types import types as tm
from modules.online.steps import real as rm
from modules.online.steps import test as tem
from modules.online.steps import simulator as sem
from modules.online.steps import init_simulator as ism
from apps.user import client_detailed_info as cdim


def start(sm: sem.Simulator):
    rm.start_real(sm)


def init_by_http(simulator_params: sem.SimulatorParams, client_detailed_info: cdim.ClientDetailedInfo,
                 simulation_graph_path: str):
    # 进行  simulator 的创建
    sem.simulator_instance = sem.Simulator(
        simulator_params=simulator_params,
        simulation_graph_path=simulation_graph_path,
        client_detailed_info=client_detailed_info,
    )
    # simulator 的初始化
    ism.initialize(sem.simulator_instance)


def start_by_http():
    # simulator_instance 的运行
    if sem.simulator_instance is None:
        print("simulator instance is None", flush=True)
    else:
        start(sem.simulator_instance)