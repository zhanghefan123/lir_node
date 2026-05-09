from modules.online.entities import sim_node_base as snbm


class SimNormalRouter(snbm.SimNodeBase):
    def __init__(self, node_name: str, node_index: int, corrupt_ratio_start: float,
                 corrupt_ratio_end: float, corrupt_special_packet_ratio_start: float,
                 corrupt_special_packet_ratio_end: float):
        # Initialize the embedded SimNodeBase
        # Equivalent to CreateSimNodeBase(nodeName, nodeIndex)
        super().__init__(node_name, node_index)
        self.corrupt_ratio_start = corrupt_ratio_start
        self.corrupt_ratio_end = corrupt_ratio_end
        self.corrupt_special_packet_ratio_start = corrupt_special_packet_ratio_start
        self.corrupt_special_packet_ratio_end = corrupt_special_packet_ratio_end
