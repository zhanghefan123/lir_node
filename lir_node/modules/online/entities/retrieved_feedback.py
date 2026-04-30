from typing import List, Optional
from dataclasses import dataclass
from modules.online.entities import sim_path as spm


@dataclass
class RetrievedFeedback:
    epoch_id: int = 0  # 收到来自 epoch_id 的反馈
    sending_time_elapsed: int = 0  # 发送时间的延迟
    number_of_sample_nodes: int = 0  # 所选路径需要采样的节点的数量
    retrieved_ack_counts: Optional[List[int]] = None  # 实际收到的 ack 的数量
    expected_ack_counts: Optional[List[int]] = None  # 预计收到的 ack 的数量
    retrieved_epoch_selected_path: Optional[spm.SimPath] = None  # 获取到的 epoch 选择的路径

    def __init__(self, epoch_id: int,
                 sending_time_elapsed: int,
                 number_of_sample_nodes: int,
                 retrieved_ack_counts: List[int],
                 expected_ack_counts: List[int]):
        self.epoch_id = epoch_id
        self.sending_time_elapsed = sending_time_elapsed
        self.number_of_sample_nodes = number_of_sample_nodes
        self.retrieved_ack_counts = retrieved_ack_counts
        self.expected_ack_counts = expected_ack_counts

    def __str__(self) -> str:
        return (f"retrieved_epoch_id: {self.epoch_id}, sending_time_elapsed: {self.sending_time_elapsed}, number_of_sample_nodes: {self.number_of_sample_nodes},"
                f"retrieved_ack_counts: {self.retrieved_ack_counts}, expected_ack_counts: {self.expected_ack_counts}")
