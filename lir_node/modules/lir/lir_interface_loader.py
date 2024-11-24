from typing import List
from modules.config import env_loader as elm


class LiRInterface:
    def __init__(self, interface_name: str, link_identifier: int):
        """
        初始化 LiRInterface
        :param interface_name: 接口名称
        :param link_identifier: 接口对应的链路标识
        """
        self.interface_name = interface_name
        self.link_identifier = link_identifier

    def __str__(self):
        return (f"interface_name: {self.interface_name} "
                f"link_identifier: {self.link_identifier}")


def load_lir_interfaces() -> List[LiRInterface]:
    """
    加载接口条目
    :return: 接口条目系列
    ln2_idx1->2
    ln2_idx2->3
    """
    # 接口文件
    lir_interface_file_path = f"/configuration/{elm.env_loader.container_name}/interface/interface.txt"
    # 接口条目
    lir_interfaces = []
    # 打开文件
    with open(lir_interface_file_path) as f:
        # 读取每一行
        all_lines = f.readlines()
        for line in all_lines:
            line = line.rstrip("\n")
            if line == "":
                continue
            result = line.split("->")
            interface_name = result[0]
            link_identifier = int(result[1])
            lir_interface = LiRInterface(interface_name,
                                         link_identifier)
            lir_interfaces.append(lir_interface)
    return lir_interfaces
