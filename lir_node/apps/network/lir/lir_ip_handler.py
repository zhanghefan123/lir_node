import socket
from typing import List
from PyInquirer import prompt
from numpy import number
from pyroute2.dhcp import option

from apps.user import user_input as uim
from apps.user import questions as qm


class UdpLiRHandler:
    def __init__(self, user_input: uim.UserInput):
        self.user_input = user_input
        self.socket = None

    def create_udp_socket_and_set_sockopt(self, destinations: List):
        """
        创建 udp_socket 并设置 socket 选项
        :return: 创建好的并且设置好选项的 udp_socket
        """
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        number_of_destinations = len(destinations)
        option_length = 2 + number_of_destinations
        socket_options = [0x94, option_length] + destinations
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
        question_for_destination_node[0]["choices"] = self.user_input.name_to_ip_mapping.keys()
        destination_count = int(prompt(qm.QUESTION_FOR_DESTINATION_COUNT)["count"])
        destinations = []
        for index in range(destination_count):
            destination = prompt(question_for_destination_node)["destination"]


    def start(self):













