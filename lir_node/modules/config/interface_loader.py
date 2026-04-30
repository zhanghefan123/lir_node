import os
import socket
from typing import List, Dict
from modules.config import env_loader as elm


class Interface:
    def __init__(self, interface_name: str, link_identifier: int, source_node_id: int, target_node_id: int,
                 peer_ip_address: str):
        """
        初始化 Interface
        :param interface_name: 接口名称
        :param link_identifier: 接口对应的链路标识
        :param source_node_id: 源节点
        :param target_node_id: 目的节点
        :param peer_ip_address: 对侧的 ip 地址
        """
        self.interface_name = interface_name
        self.link_identifier = link_identifier
        self.ifindex = None
        self.source_node_id = source_node_id
        self.target_node_id = target_node_id
        self.peer_ip_address = peer_ip_address

    def __str__(self):
        return (f"interface_name: {self.interface_name} "
                f"link_identifier: {self.link_identifier} "
                f"ifindex: {self.ifindex} "
                f"source_node_id: {self.source_node_id} "
                f"target_node_id: {self.target_node_id} "
                f"peer_ip_address: {self.peer_ip_address} ")


def load_all_interfaces() -> (List[Interface], Dict[str, Interface]):
    # 接口文件
    all_interface_file_path = f"/configuration/{elm.env_loader.container_name}/interface/all_interfaces.txt"
    # 接口条目
    all_lir_interfaces = []
    all_lir_interfaces_mapping = {}
    # 打开文件
    if os.path.exists(all_interface_file_path):
        with open(all_interface_file_path) as f:
            all_lines = f.readlines()
            for line in all_lines:
                line = line.rstrip("\n")
                if line == "":
                    continue
                result = line.split("->")
                interface_name = result[0]
                link_identifier = int(result[1])
                source_node_id = int(result[2])
                target_node_id = int(result[3])
                peer_interface_address = result[4][:-3]
                lir_interface = Interface(interface_name, link_identifier, source_node_id, target_node_id,
                                          peer_interface_address)
                all_lir_interfaces.append(lir_interface)
                all_lir_interfaces_mapping[f"{source_node_id}->{target_node_id}"] = lir_interface
    else:
        print("all_interfaces.txt does not exists", flush=True)
    # 进行结果的返回
    return all_lir_interfaces, all_lir_interfaces_mapping


def load_interfaces() -> List[Interface]:
    """
    加载接口条目
    :return: 接口条目系列
    ln2_idx1->2
    ln2_idx2->3
    """
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
            source_node_id = int(result[2])
            target_node_id = int(result[3])
            peer_interface_address = result[4][:-3]
            lir_interface = Interface(interface_name, link_identifier, source_node_id, target_node_id,
                                      peer_interface_address)
            lir_interfaces.append(lir_interface)
    return lir_interfaces


def load_lir_interface_ifindexes(lir_interfaces: List[Interface]):
    """
    为所有的 lir_interfaces 设置 ifindex
    :param lir_interfaces: 所有的 lir_interfaces
    """
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
