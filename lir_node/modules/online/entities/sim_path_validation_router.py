from typing import List
from modules.online.entities import sim_node_base as snbm


class SimPathValidationRouter(snbm.SimNodeBase):
    def __init__(self, node_name: str, node_index: int):
        # 初始化父类 SimNodeBase
        super().__init__(node_name, node_index)

        self.weights: List[float] = []
        self.explore_probabilities: List[float] = []
