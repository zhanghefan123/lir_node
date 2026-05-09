from modules.online.entities import sim_normal_router as snrm
from typing import Optional


class ScheduledEvent:
    def __init__(self, node_id: int, normal_router: Optional[snrm.SimNormalRouter], employed_epoch_or_timestamp_ms: int,
                 corrupt_ratio_start: float, corrupt_ratio_end: float,
                 corrupt_special_packet_ratio_start: float, corrupt_special_packet_ratio_end: float):
        self.node_id = node_id
        self.normal_router = normal_router
        self.employed_epoch_or_timestamp_ms = employed_epoch_or_timestamp_ms
        self.corrupt_ratio_start = corrupt_ratio_start
        self.corrupt_ratio_end = corrupt_ratio_end
        self.corrupt_special_packet_ratio_start = corrupt_special_packet_ratio_start
        self.corrupt_special_packet_ratio_end = corrupt_special_packet_ratio_end

    def execute(self):
        self.normal_router.corrupt_ratio_start = self.corrupt_ratio_start
        self.normal_router.corrupt_ratio_end = self.corrupt_ratio_end
        self.normal_router.corrupt_special_packet_ratio_start = self.corrupt_special_packet_ratio_start
        self.normal_router.corrupt_special_packet_ratio_end = self.corrupt_special_packet_ratio_end
