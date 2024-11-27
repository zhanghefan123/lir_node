import socket
from PyInquirer import prompt
from apps.user import user_input as uim
from apps.user import questions as qm
from apps.sender import sender as sm
from modules.config import env_loader as elm
from modules.config import name_to_ip_mapping_loader as ntimlm


class UdpIpHandler:
    def __init__(self, user_input: uim.UserInput):
        self.user_input = user_input
        self.socket = None
        self.name_to_ip_mapping = None
        self.selected_destination_name = None
        self.selected_destination_ip = None

    def create_socket(self):
        """
        进行 socket 的创建
        :return: 返回创建好的 udp_ip_socket
        """
        udp_ip_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return udp_ip_socket

    def get_transmission_pattern(self):
        """
        获取发送模式
        :return: 发送模式
        """
        return prompt(qm.QUESTION_FOR_PACKET_TRANSMISSION_PATTERN)["pattern"]

    def get_destination_name_and_ip(self):
        file_path = f"/configuration/{elm.env_loader.container_name}/address_mapping.conf"
        self.name_to_ip_mapping = ntimlm.NameToIdIpMappingLoader(file_path=file_path).container_name_to_ip_mapping
        question_for_destination_node = qm.QUESTION_FOR_DESTINATION
        question_for_destination_node[0]["choices"] = list(self.name_to_ip_mapping.keys())
        self.selected_destination_name = prompt(question_for_destination_node)["destination"]
        self.selected_destination_ip = self.name_to_ip_mapping[self.selected_destination_name]

    def send_data(self):
        """
        进行数据的发送
        :return:
        """
        while True:
            pattern = self.get_transmission_pattern()
            if pattern == "single":
                sm.send_in_single(socket_tmp=self.socket,
                                  dest_ip=self.selected_destination_ip,
                                  dest_port=self.user_input.selected_destination_port)
            elif pattern == "batch":
                sm.send_in_batch(socket_tmp=self.socket,
                                 dest_ip=self.selected_destination_ip,
                                 dest_port=self.user_input.selected_destination_port)
            elif pattern == "file":
                sm.send_file(socket_tmp=self.socket,
                             dest_ip=self.selected_destination_ip,
                             dest_port=self.user_input.selected_destination_port)
            else:
                break

    def start(self):
        self.get_destination_name_and_ip()
        self.socket = self.create_socket()
        self.send_data()
