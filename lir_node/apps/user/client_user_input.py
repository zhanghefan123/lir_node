from PyInquirer import prompt
from apps.user import questions as qm
from defined_types import types as tm
from modules.config import env_loader as elm
from modules.config import name_to_ip_mapping_loader as ntimlm


class ClientUserInput:
    def __init__(self):
        self.selected_network_layer = None
        self.selected_destination_port = None
        self.selected_destination_name = None
        self.selected_transmission_pattern = None
        self.name_to_ip_mapping = None
        self.name_to_id_mapping = None
        self.start()

    def get_network_layer(self):
        answers_for_protocol = prompt(qm.QUESTION_FOR_PROTOCOL)["protocol"]
        if answers_for_protocol == "IP":
            self.selected_network_layer = tm.NetworkLayer.IP
        elif answers_for_protocol == "LIR":
            self.selected_network_layer = tm.NetworkLayer.LIR
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
        1. 从容器名 -> ip 的映射关系
        2. 从容器名 -> id 的映射关系
        :return:
        """
        file_path = f"/configuration/{elm.env_loader.container_name}/address_mapping.conf"
        mapping_loader = ntimlm.NameToIdIpMappingLoader(file_path=file_path)
        self.name_to_ip_mapping = mapping_loader.container_name_to_ip_mapping
        self.name_to_id_mapping = mapping_loader.container_name_to_id_mapping

    def start(self):
        # 获取目的端口
        self.get_destination_port()
        # 获取选取的网络层
        self.get_network_layer()
        # 获取映射关系
        self.get_mappings()

