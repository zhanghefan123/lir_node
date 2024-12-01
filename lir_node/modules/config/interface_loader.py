import socket
import time
from typing import List
from modules.config import env_loader as elm


class Interface:
    def __init__(self, interface_name: str, link_identifier: int):
        """
        初始化 Interface
        :param interface_name: 接口名称
        :param link_identifier: 接口对应的链路标识
        """
        self.interface_name = interface_name
        self.link_identifier = link_identifier
        self.ifindex = None

    def __str__(self):
        return (f"interface_name: {self.interface_name} "
                f"link_identifier: {self.link_identifier} "
                f"ifindex: {self.ifindex}")


def load_interfaces() -> List[Interface]:
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
            lir_interface = Interface(interface_name, link_identifier)
            lir_interfaces.append(lir_interface)
    return lir_interfaces


def load_lir_interface_ifindexes(lir_interfaces: List[Interface]):
    """
    为所有的 lir_interfaces 设置 ifindex
    :param lir_interfaces: 所有的 lir_interfaces
    """
    while True:
        if is_all_interfaces_available(lir_interfaces):
            break
        time.sleep(1)
    mapping = get_current_interface_to_ifindex_mapping()
    for lir_interface in lir_interfaces:
        lir_interface.ifindex = mapping[lir_interface.interface_name]


def is_all_interfaces_available(lir_interfaces: List[Interface]) -> bool:
    """
    判断是否所有的接口都可用了
    :param lir_interfaces: 所有的接口
    :return: 是否可用
    """
    current_interface_to_ifindex_mapping = get_current_interface_to_ifindex_mapping()
    for lir_interface in lir_interfaces:
        if lir_interface.interface_name not in current_interface_to_ifindex_mapping.keys():
            return False
    return True


def get_current_interface_to_ifindex_mapping():
    """
    获取当前的从接口名 -> ifindex 的映射
    :return:
    """
    available_interfaces = socket.if_nameindex()
    return {item[1]: item[0] for item in available_interfaces}
