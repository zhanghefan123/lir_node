from PyInquirer import prompt
from apps.user import questions as qm
from defined_types import types as tm
from modules.config import env_loader as elm
from modules.config import name_to_ip_mapping_loader as ntimlm
from modules.config import name_to_srv6_dest_mapping_loader as ntsdml


class ClientUserInput:
    def __init__(self):
        self.selected_network_layer = None
        self.selected_destination_port = None
        self.selected_destination_name = None
        self.selected_transmission_pattern = None
        self.name_to_srv6_dest_ip_mapping = None
        self.name_to_srv6_dest_ifname_mapping = None
        self.name_to_first_ipv4_mapping = None
        self.name_to_first_ipv6_mapping = None
        self.name_to_id_mapping = None
        self.start()

    def get_network_layer(self):
        answer_for_protocol = prompt(qm.QUESTION_FOR_PROTOCOL)["protocol"]
        if answer_for_protocol == "SRV6":
            self.selected_network_layer = tm.NetworkLayer.SRV6
        elif answer_for_protocol == "IP":
            self.selected_network_layer = tm.NetworkLayer.IP
        elif answer_for_protocol == "LIR":
            self.selected_network_layer = tm.NetworkLayer.LIR
        elif answer_for_protocol == "ICING":
            self.selected_network_layer = tm.NetworkLayer.ICING
        elif answer_for_protocol == "OPT":
            self.selected_network_layer = tm.NetworkLayer.OPT
        elif answer_for_protocol == "SELIR":
            self.selected_network_layer = tm.NetworkLayer.SELIR
        elif answer_for_protocol == "FAST_SELIR":
            self.selected_network_layer = tm.NetworkLayer.FAST_SELIR
        elif answer_for_protocol == "MULTICAST_SELIR":
            self.selected_network_layer = tm.NetworkLayer.MULTICAST_SELIR
        else:
            raise Exception("unsupported network type")

    def get_destination_port(self):
        """
        获取目的端口
        :return: None
        """
        answers_for_destination_port = prompt(qm.QUESTION_FOR_DESTINATION_PORT)["port"]
        self.selected_destination_port = int(answers_for_destination_port)

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
        # ---------------------------------------------------------------------------------------------------
        # srv6_dest_mapping_loader
        # ---------------------------------------------------------------------------------------------------
        srv6_dest_mapping_loader = ntsdml.NameToSrv6DestMappingLoader(file_path=srv6_dest_file_path)
        self.name_to_srv6_dest_ip_mapping = srv6_dest_mapping_loader.container_name_to_ipv6_mapping
        self.name_to_srv6_dest_ifname_mapping = srv6_dest_mapping_loader.container_name_to_dest_ifname_mapping
        # ---------------------------------------------------------------------------------------------------

    def start(self):
        # 获取目的端口
        self.get_destination_port()
        # 获取选取的网络层
        self.get_network_layer()
        # 获取映射关系
        self.get_mappings()

