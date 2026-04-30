# 假设这些类、函数和常量在你项目的其他模块中定义
from modules.online.entities import sim_node_base as snbm


class SimEndHost(snbm.SimNodeBase):
    def __init__(self, node_name: str, node_index: int):
        # 初始化父类 SimNodeBase
        super().__init__(node_name, node_index)
