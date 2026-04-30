from dataclasses import dataclass
from typing import List, Optional, Dict
from defined_types import types as tm
from modules.config import env_loader as elm
from modules.config import name_to_ip_mapping_loader as ntimlm
from modules.config import name_to_srv6_dest_mapping_loader as ntsdml
from apps.user import questions as qm
from tools.extract import extract
from PyInquirer import prompt


@dataclass
class ClientDetailedInfo:
    # basic info
    selected_network_layer: int = -1
    destination_port: int = -1

    # type related variables
    transmission_pattern: int = -1

    # size related vaiables
    processes: int = -1
    file_size: int = -1
    buffer_size: int = -1
    message_size: int = -1
    batch_size: int = -1

    # content related variables
    destinations: Optional[List[str]] = None
    content: str = ""

    # time related variables
    interval: float = -1

    # all the mappigns
    name_to_srv6_dest_ip_mapping: Dict[str, str] = None
    name_to_srv6_dest_ifname_mapping: Dict[str, str] = None
    name_to_first_ipv4_mapping: Dict[str, str] = None
    name_to_first_ipv6_mapping: Dict[str, str] = None
    name_to_id_mapping: Dict[str, int] = None

    # 进行排序的名称
    sorted_name_list: List[str] = None

    def __init__(self):
        self.get_mappings()

    def get_mappings(self):
        """
        获取
        1. 从容器名 -> ip 的映射关系 (除去自己节点)
        2. 从容器名 -> id 的映射关系 (除去自己节点)
        :return:
        """
        container_name = elm.env_loader.container_name
        first_interface_file_path = f"/configuration/{elm.env_loader.container_name}/route/address_mapping.conf"
        srv6_dest_file_path = f"/configuration/{elm.env_loader.container_name}/route/ipv6_destination.txt"
        # first_interface_mapping_loader
        # ---------------------------------------------------------------------------------------------------
        first_interface_mapping_loader = ntimlm.NameToIdIpMappingLoader(file_path=first_interface_file_path,
                                                                        container_name=container_name)
        self.name_to_first_ipv4_mapping = first_interface_mapping_loader.name_to_first_ipv4_mapping
        self.name_to_first_ipv6_mapping = first_interface_mapping_loader.name_to_first_ipv6_mapping
        self.name_to_id_mapping = first_interface_mapping_loader.name_to_id_mapping
        self.sorted_name_list = self.get_sorted_name_list()
        # ---------------------------------------------------------------------------------------------------
        # srv6_dest_mapping_loader
        # ---------------------------------------------------------------------------------------------------
        srv6_dest_mapping_loader = ntsdml.NameToSrv6DestMappingLoader(file_path=srv6_dest_file_path)
        self.name_to_srv6_dest_ip_mapping = srv6_dest_mapping_loader.container_name_to_ipv6_mapping
        self.name_to_srv6_dest_ifname_mapping = srv6_dest_mapping_loader.container_name_to_dest_ifname_mapping
        # ---------------------------------------------------------------------------------------------------

    def get_sorted_name_list(self):
        # 获取经排序后的名字列表
        name_list = list(self.name_to_id_mapping.keys())
        name_list.sort(key=lambda x: extract(x))
        return name_list

    def get_basic_level_user_input(self):
        self.selected_network_layer = self.selected_network_layer if self.selected_network_layer != -1 else tm.NetworkLayer.turn_str_into_type(
            prompt(qm.QUESTION_FOR_PROTOCOL)["protocol"])


if __name__ == "__main__":
    client_detailed_info = ClientDetailedInfo()
    print(client_detailed_info.batch_size)
