import socket
from PyInquirer import prompt
from apps.user import client_user_input as uim
from apps.user import questions as qm
from apps.sender import sender as sm
from defined_types import types as tm


class UdpIpClient:
    def __init__(self, client_user_input: uim.ClientUserInput, selected_network_layer):
        """
        初始化使用 IP 作为网络层的 UDP 传输层
        :param client_user_input: 客户端, 用户的输入
        """
        self.client_user_input = client_user_input
        self.socket = None
        self.selected_destination_name = None
        self.selected_destination_ip = None
        self.selected_network_layer = selected_network_layer

    def create_socket(self):
        """
        进行 socket 的创建
        :return: 返回创建好的 udp_ip_socket
        """
        if self.selected_network_layer == tm.NetworkLayer.IP:
            udp_ip_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif self.selected_network_layer == tm.NetworkLayer.SRV6:
            udp_ip_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        else:
            raise Exception("unsupported network layer")
        return udp_ip_socket

    def get_transmission_pattern(self):
        """
        获取发送模式
        :return: 发送模式
        """
        return prompt(qm.QUESTION_FOR_PACKET_TRANSMISSION_PATTERN)["pattern"]

    def get_destination_name_and_ip(self):
        if self.selected_network_layer == tm.NetworkLayer.IP:
            question_for_destination_node = qm.QUESTION_FOR_DESTINATION
            question_for_destination_node[0]["choices"] = list(self.client_user_input.name_to_ip_mapping.keys())
            self.selected_destination_name = prompt(question_for_destination_node)["destination"]
            self.selected_destination_ip = self.client_user_input.name_to_ip_mapping[self.selected_destination_name]
        elif self.selected_network_layer == tm.NetworkLayer.SRV6:
            question_for_destination_node = qm.QUESTION_FOR_DESTINATION
            question_for_destination_node[0]["choices"] = list(self.client_user_input.name_to_ipv6_mapping.keys())
            self.selected_destination_name = prompt(question_for_destination_node)["destination"]
            self.selected_destination_ip = self.client_user_input.name_to_ipv6_mapping[self.selected_destination_name]
        else:
            raise Exception("unsupported network layer")

    def send_data(self):
        """
        进行数据的发送
        :return: None
        """
        while True:
            # 获取传输模式
            pattern = self.get_transmission_pattern()
            if pattern == "single":  # 传输模式为一个个的发送
                sm.send_in_single(socket_tmp=self.socket,
                                  dest_ip=self.selected_destination_ip,
                                  dest_port=self.client_user_input.selected_destination_port)
            elif pattern == "batch":  # 如果传输模式为一批批的发送
                sm.send_in_batch(socket_tmp=self.socket,
                                 dest_ip=self.selected_destination_ip,
                                 dest_port=self.client_user_input.selected_destination_port)
            elif pattern == "file":  # 如果传输模式是以文件为单位
                sm.send_file(socket_tmp=self.socket,
                             dest_ip=self.selected_destination_ip,
                             dest_port=self.client_user_input.selected_destination_port)
            elif pattern == "quit":
                break
            else:
                raise Exception("unsupported transmission pattern")

    def start(self):
        """
        进行 udp_ip 客户端的启动
        :return:
        """
        # 获取目的容器的名称和 ip
        self.get_destination_name_and_ip()
        # 进行 socket 的创建
        self.socket = self.create_socket()
        # 进行数据的发送
        self.send_data()
