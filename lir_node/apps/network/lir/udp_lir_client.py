import math
import socket
from typing import List
from PyInquirer import prompt
from apps.user import questions as qm
from apps.user import client_user_input as uim
from apps.sender import sender as sm
from modules.config.env_loader import env_loader
from defined_types import types as tm


class UdpLiRClient:
    def __init__(self, client_user_input: uim.ClientUserInput):
        """
        初始化 udp_lir_client
        :param client_user_input: 客户端输入
        """
        self.client_user_input = client_user_input
        self.destinations = None
        self.socket_tmp = None
        self.destination_address = None

    def create_udp_socket_and_set_sockopt(self, destinations: List):
        """
        创建 udp_socket 并设置 socket 选项
        :return: 创建好的并且设置好选项的 udp_socket
        """
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        number_of_destinations = len(destinations)
        option_length = 2 + 1 + number_of_destinations  # (type, length, number_of_destinations, dest1, dest2, ..., alignment...)
        option_alignment_length = math.ceil(float(option_length) / float(4)) * 4  # 进行 4 字节对齐后的总长度
        alignment_part = [0x0] * (option_alignment_length - option_length)  # 补齐的部分
        socket_options = [0x94, option_alignment_length] + [number_of_destinations] + destinations + alignment_part
        socket_options_in_bytes = bytearray(socket_options)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_DEBUG, 1)
        udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_OPTIONS, socket_options_in_bytes)
        return udp_socket

    def get_destinations(self):
        """
        设置 destinations
        :return:
        """
        question_for_destination_node = qm.QUESTION_FOR_DESTINATION
        question_for_destination_node[0]["choices"] = self.client_user_input.name_to_id_mapping.keys()
        destination_count = int(prompt(qm.QUESTION_FOR_DESTINATION_COUNT)["count"])
        if (destination_count > 1) and (env_loader.routing_table_type == tm.RoutingTableType.ARRAY_BASED_ROUTING_TABLE_TYPE):
            raise Exception("array based routing table type cannot support multiple destinations")
        destinations = []
        destination_name = None
        for index in range(destination_count):
            destination_name = prompt(question_for_destination_node)["destination"]
            destination_id = self.client_user_input.name_to_id_mapping[destination_name]
            destinations.append(destination_id)
        # 当只有一个目的节点的时候 -> 将这个目的节点的 ip 作为目的 ip
        if destination_count == 1:
            self.destination_address = self.client_user_input.name_to_ip_mapping[destination_name]
        else:
            self.destination_address = "1.1.1.1"

        return destinations

    def get_transmission_pattern(self):
        """
        获取发送模式
        :return: 发送模式
        """
        return prompt(qm.QUESTION_FOR_PACKET_TRANSMISSION_PATTERN)["pattern"]

    def send_data(self):
        """
        进行数据的发送
        :return:
        """
        while True:
            pattern = self.get_transmission_pattern()
            if pattern == "single":  # 传输模式为一个个的发送
                sm.send_in_single(socket_tmp=self.socket_tmp,
                                  dest_ip=self.destination_address,
                                  dest_port=self.client_user_input.selected_destination_port)
            elif pattern == "batch":  # 传输模式为一批批的发送
                sm.send_in_batch(socket_tmp=self.socket_tmp,
                                 dest_ip=self.destination_address,
                                 dest_port=self.client_user_input.selected_destination_port)
            elif pattern == "file":  # 传输模式是以文件为单位
                sm.send_file(socket_tmp=self.socket_tmp,
                             dest_ip=self.destination_address,
                             dest_port=self.client_user_input.selected_destination_port)
            elif pattern == "quit":
                break
            else:
                raise Exception("unsupported transmission pattern")

    def start(self):
        """
        进行 udp_lir 客户端的启动
        :return: None
        """
        # 获取目的节点列表
        self.destinations = self.get_destinations()
        # 获取临时 socket
        self.socket_tmp = self.create_udp_socket_and_set_sockopt(self.destinations)
        # 进行数据的发送
        self.send_data()












