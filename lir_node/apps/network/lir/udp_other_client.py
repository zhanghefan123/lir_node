import math
import socket
from typing import List
from PyInquirer import prompt
from apps.user import questions as qm
from apps.user import client_detailed_info as cdim
from apps.sender import sender as sm
from modules.config.env_loader import env_loader
from defined_types import types as tm


class UdpOtherClient:
    def __init__(self, client_detailed_info: cdim.ClientDetailedInfo):
        """
        初始化 udp_lir_client
        :param client_detailed_info: 客户端输入
        """
        self.client_detailed_info = client_detailed_info
        self.destinations = None
        self.socket_tmp = None
        self.number_of_processes = None
        self.destination_address = None
        self.transmission_pattern = None
        self.destination_port = None
        self.sockets = []

    def create_udp_socket_and_set_sockopt(self, destinations: List):
        """
        创建 udp_socket 并设置 socket 选项
        设置选项格式
        :return: 创建好的并且设置好选项的 udp_socket
        """
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        number_of_destinations = len(destinations)
        # (type, length, protocol, number_of_destinations, dest1, dest2, ..., alignment...)
        option_length = 2 + 1 + 1 + number_of_destinations
        option_alignment_length = math.ceil(float(option_length) / float(4)) * 4  # 进行 4 字节对齐后的总长度
        alignment_part = [0x0] * (option_alignment_length - option_length)  # 补齐的部分
        socket_options = [0x94, option_alignment_length] + [self.client_detailed_info.selected_network_layer] + [
            number_of_destinations] + destinations + alignment_part
        socket_options_in_bytes = bytearray(socket_options)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_DEBUG, 1)
        udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_OPTIONS, socket_options_in_bytes)
        return udp_socket

    @classmethod
    def get_number_of_processes(cls, number_of_processes: int = -1):
        """
        获取多进程的数量
        :return:
        """
        if -1 == number_of_processes:
            question_for_processes = qm.QUESTION_FOR_NUMBER_OF_PROCESSES
            number_of_processes = int(prompt(question_for_processes)["processes"])
            return number_of_processes
        else:
            return number_of_processes

    @classmethod
    def get_destinations(cls, client_detailed_info: cdim.ClientDetailedInfo):
        """
        设置 destinations
        :return:
        """
        if client_detailed_info.destinations is None:
            question_for_destination_node = qm.QUESTION_FOR_DESTINATION
            question_for_destination_node[0]["choices"] = client_detailed_info.sorted_name_list
            destination_count = int(prompt(qm.QUESTION_FOR_DESTINATION_COUNT)["count"])
            if (destination_count > 1) and (
                    env_loader.routing_table_type == tm.RoutingTableType.ARRAY_BASED_ROUTING_TABLE_TYPE):
                raise Exception("array based routing table type cannot support multiple destinations")
            destinations = []
            destination_name = None
            for index in range(destination_count):
                destination_name = prompt(question_for_destination_node)["destination"]
                destination_id = client_detailed_info.name_to_id_mapping[destination_name]
                destinations.append(destination_id)
            # 当只有一个目的节点的时候 -> 将这个目的节点的 ip 作为目的 ip
            if destination_count == 1:
                destination_address = client_detailed_info.name_to_first_ipv4_mapping[destination_name]
            else:
                destination_address = "1.1.1.1"

            return destinations, destination_address
        else:
            destinations = []
            destination_name = None
            for index in range(len(client_detailed_info.destinations)):
                destination_name = client_detailed_info.destinations[index]
                destination_id = client_detailed_info.name_to_id_mapping[destination_name]
                destinations.append(destination_id)
            if len(client_detailed_info.destinations) == 1:
                destination_address = client_detailed_info.name_to_first_ipv4_mapping[destination_name]
            else:
                destination_address = "1.1.1.1"
            return destinations, destination_address

    def send_data(self):
        """
        进行数据的发送
        :return:
        """
        # 获取发送包的进程的数量
        if self.transmission_pattern == tm.TransmissionType.SINGLE:  # 传输模式为一个个的发送
            sm.send_in_single(socket_tmp=self.socket_tmp,
                              dest_ip=self.destination_address,
                              dest_port=self.destination_port,
                              content=self.client_detailed_info.content)
        elif self.transmission_pattern == tm.TransmissionType.BATCH:  # 传输模式为一批批的发送
            sm.send_in_batch(socket_tmp=self.socket_tmp,
                             dest_ip=self.destination_address,
                             dest_port=self.destination_port,
                             batch_size=self.client_detailed_info.batch_size,
                             message_size=self.client_detailed_info.message_size,
                             interval=self.client_detailed_info.interval)
        elif self.transmission_pattern == tm.TransmissionType.FILE:  # 传输模式是以文件为单位
            sm.send_file(dest_ip=self.destination_address,
                         dest_port=self.destination_port,
                         number_of_processes=self.number_of_processes,
                         sockets=self.sockets,
                         file_size=self.client_detailed_info.file_size,
                         buffer_size=self.client_detailed_info.buffer_size)
        else:
            raise Exception(f"unsupported transmission pattern {self.transmission_pattern}")

    def start(self):
        """
        进行 udp_lir 客户端的启动
        :return: None
        """

        # 1. get processes
        self.number_of_processes = self.client_detailed_info.processes if self.client_detailed_info.processes != -1 else int(
            prompt(qm.QUESTION_FOR_NUMBER_OF_PROCESSES)["processes"])

        # 2. get destinations
        self.destinations, self.destination_address = self.get_destinations(self.client_detailed_info)

        # 3. get transmission pattern
        self.transmission_pattern = self.client_detailed_info.transmission_pattern if self.client_detailed_info.transmission_pattern != -1 else tm.TransmissionType.turn_str_into_type(prompt(qm.QUESTION_FOR_PACKET_TRANSMISSION_PATTERN)["pattern"])

        # 4. get destination port
        self.destination_port = self.client_detailed_info.destination_port if self.client_detailed_info.destination_port != -1 else int(prompt(qm.QUESTION_FOR_DESTINATION_PORT)["port"])

        # 5. get sockets
        for i in range(self.number_of_processes):
            socket_tmp = self.create_udp_socket_and_set_sockopt(self.destinations)
            self.sockets.append(socket_tmp)

        # 6. get first socket
        self.socket_tmp = self.sockets[0]

        # 7. send data
        self.send_data()
