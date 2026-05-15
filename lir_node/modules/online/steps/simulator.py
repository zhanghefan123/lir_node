import logging
from typing import List, Set, Optional
from dataclasses import dataclass
from modules.online.entities import sim_path as sppm
from modules.online.entities.sim_path import SimPath
from modules.online.types import types as tm
from modules.online.entities import sim_graph as sgm
from apps.user import client_detailed_info as cdim
from queue import Queue
from apps.network.lir import udp_other_client as uocm

# 初始化全局日志器 (你可以替换为你自定义的 logger)
simulator_logger = logging.getLogger("ModuleSimulator")


@dataclass
class SimulatorParams:
    """Simulator 相关参数的配置类"""
    number_of_epochs: int = -1  # 总的批次数量
    number_of_pkts_per_link: int = -1  # 单个批次内部的包的数量
    mini_batch_size: int = -1  # 在 dynamic 发送的时候, 每个小 batch 的 size
    learning_rate: float = -1  # 学习率，控制每次更新权重的幅度
    minimum_delivery_ratio: float = -1  # 最小的交付率
    enable_dade_algorithm: bool = False  # 是否启用 dade 算法 (delay adaptive algorithm)
    enable_deda_algorithm: bool = False  # 是否启动 deda 算法 (delay and data adaptive algorithm)
    min_ack_for_rtt_estimation: int = 50
    experiment_time_elapsed_ms: int = 30 * 1000


class Simulator:
    def __init__(self, simulator_params: Optional[SimulatorParams],
                 simulation_graph_path: str,
                 client_detailed_info: Optional[cdim.ClientDetailedInfo]):
        """
        Simulator 的构造方法，对应 Go 中的 NewSimulator
        :param simulator_params: Simulator 相关的参数对象
        :param simulation_graph_path: 拓扑图配置文件的路径
        :param client_detailed_info: 实际用来传输的设置
        """

        # ----------------------------- 一般参数 -----------------------------
        self.sim_graph: Optional[sgm.SimGraph] = None  # 模拟图 (SimGraph)，初始为 None
        self.simulation_graph_path: str = simulation_graph_path  # 模拟图的配置文件
        self.simulator_params: SimulatorParams = simulator_params  # 模拟图的配置参数
        self.client_detailed_info: cdim.ClientDetailedInfo = client_detailed_info  # 发送udp客户端的信息
        self.udp_other_client: Optional[uocm.UdpOtherClient] = None  # 一开始不进行设置, 在发送包的时候设置
        self.simulator_init_steps: Set[str] = set()  # Go 中的 map[string]struct{} 在 Python 中是标准的 Set (集合)
        self.rectified_loss_calculating_type: str = tm.RectifiedLossCalculateType.TYPE_SCALING  # loss 计算方式
        self.sync_timestamp = 0
        self.scheduled_event_list = []
        self.packet_best_path_id = 1
        self.check_thread = None
        self.epoch_queue = Queue()
        # ----------------------------- 一般参数 -----------------------------

        # ----------------------------- fixed batch 相关参数 -----------------------------
        self.old_epoch_path_list: List[sppm.SimPath] = []  # 旧的还没获取 ack 的路径序列
        self.latest_sending_epoch: int = 0  # 当前的sending epoch
        # ----------------------------- fixed batch 相关参数 -----------------------------

        # ----------------------------- fixed/dynamic batch 相关参数 -----------------------------
        self.retrieved_acks: bool = True  # 是否返回了 ack
        self.latest_selected_path: Optional[sppm.SimPath] = None  # 当前下发的路径是什么
        self.latest_acks_epoch: int = 0  # 最新的 ack epoch
        self.best_path: Optional[SimPath] = None
        # ----------------------------- fixed/dynamic batch 相关参数 -----------------------------

        # ----------------------------- deda 相关参数 -----------------------------
        if self.simulator_params is not None:
            self.current_learning_rate: float = self.simulator_params.learning_rate
        else:
            self.current_learning_rate = 0.2
        self.constant_K: int = 6
        self.gap_list: List[int] = []  # 统计实际收到的反馈的延迟情况
        self.backward_loss_list: List[float] = []
        self.learning_rate_list: List[float] = []
        self.window_size: int = 30
        # ----------------------------- deda 相关参数 -----------------------------


# 全局 simulator
simulator_instance: Optional[Simulator] = Simulator(SimulatorParams(), "", None)


def get_windowed_backward_acc_loss(sm: Simulator) -> float:
    windowed_backward_loss_list = sm.backward_loss_list[(len(sm.backward_loss_list) - sm.window_size):]
    windowed_backward_acc_loss = 0
    for item in windowed_backward_loss_list:
        windowed_backward_acc_loss += item
    return windowed_backward_acc_loss


def get_windowed_max_gap(sm: Simulator) -> int:
    windowed_gap_list = sm.gap_list[(len(sm.gap_list) - sm.window_size):]
    windowed_max_gap = max(windowed_gap_list)
    return windowed_max_gap
