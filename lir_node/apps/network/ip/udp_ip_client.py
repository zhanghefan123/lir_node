import socket
from PyInquirer import prompt
from apps.user import questions as qm
from apps.sender import sender as sm
from apps.user import client_detailed_info as cdim
from apps.user.client_detailed_info import ClientDetailedInfo
from defined_types import types as tm


class UdpIpClient:
    def __init__(self, client_detailed_info: cdim.ClientDetailedInfo):
        """
        初始化使用 IP 作为网络层的 UDP 传输层
        :param client_detailed_info: 客户端, 用户的输入
        """
        self.socket = None
        self.selected_destination_ip = None
        self.number_of_processes = None
        self.transmission_pattern = None
        self.destination_port = None
        self.sockets = []
        self.client_detailed_info = client_detailed_info

    def create_socket(self):
        """
        进行 socket 的创建
        :return: 返回创建好的 udp_ip_socket
        """
        if self.client_detailed_info.selected_network_layer == tm.NetworkLayer.IP:
            udp_ip_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif self.client_detailed_info.selected_network_layer == tm.NetworkLayer.SRV6:
            udp_ip_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        else:
            raise Exception("unsupported network layer")
        return udp_ip_socket

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
    def get_transmission_pattern(cls, transmission_pattern: str = ""):
        """
        获取发送模式
        :return: 发送模式
        """
        if "" == transmission_pattern:
            return prompt(qm.QUESTION_FOR_PACKET_TRANSMISSION_PATTERN)["pattern"]
        else:
            return transmission_pattern

    @classmethod
    def get_destination_ip(cls, client_detailed_info: ClientDetailedInfo, destination_name: str = "") -> str:
        if "" == destination_name:
            if client_detailed_info.selected_network_layer == tm.NetworkLayer.IP:
                question_for_destination_node = qm.QUESTION_FOR_DESTINATION
                question_for_destination_node[0]["choices"] = list(client_detailed_info.name_to_first_ipv4_mapping.keys())
                selected_destination_name = prompt(question_for_destination_node)["destination"]
                selected_destination_ip = client_detailed_info.name_to_first_ipv4_mapping[
                    selected_destination_name]
            elif client_detailed_info.selected_network_layer == tm.NetworkLayer.SRV6:
                question_for_destination_node = qm.QUESTION_FOR_DESTINATION
                question_for_destination_node[0]["choices"] = list(client_detailed_info.name_to_first_ipv6_mapping.keys())
                selected_destination_name = prompt(question_for_destination_node)["destination"]
                selected_destination_ip = client_detailed_info.name_to_srv6_dest_ip_mapping[
                    selected_destination_name]
            else:
                raise Exception("unsupported network layer")
        else:
            if client_detailed_info.selected_network_layer == tm.NetworkLayer.IP:
                selected_destination_ip = client_detailed_info.name_to_first_ipv4_mapping[
                    destination_name]
                selected_destination_name = destination_name
            elif client_detailed_info.selected_network_layer == tm.NetworkLayer.SRV6:
                selected_destination_ip = client_detailed_info.name_to_srv6_dest_ip_mapping[
                    destination_name]
                selected_destination_name = destination_name
            else:
                raise Exception("unsupported network layer")
        print(f"用户选择的目的节点的 ipv6 地址为: {selected_destination_ip} 选择的目的接口是: {client_detailed_info.name_to_srv6_dest_ifname_mapping[selected_destination_name]}")
        return selected_destination_ip

    def send_data(self):
        """
        进行数据的发送
        :return: None
        """
        if self.transmission_pattern == tm.TransmissionType.SINGLE:  # 传输模式为一个个的发送
            sm.send_in_single(socket_tmp=self.socket,
                              dest_ip=self.selected_destination_ip,
                              dest_port=self.destination_port,
                              content=self.client_detailed_info.content)
        elif self.transmission_pattern == tm.TransmissionType.BATCH:  # 如果传输模式为一批批的发送
            sm.send_in_batch(socket_tmp=self.socket,
                             dest_ip=self.selected_destination_ip,
                             dest_port=self.destination_port,
                             batch_size=self.client_detailed_info.batch_size,
                             message_size=self.client_detailed_info.message_size,
                             interval=self.client_detailed_info.interval)
        elif self.transmission_pattern == tm.TransmissionType.FILE:  # 如果传输模式是以文件为单位
            sm.send_file(dest_ip=self.selected_destination_ip,
                         dest_port=self.destination_port,
                         number_of_processes=self.number_of_processes,
                         sockets=self.sockets,
                         file_size=self.client_detailed_info.file_size,
                         buffer_size=self.client_detailed_info.buffer_size)
        else:
            raise Exception(f"unsupported transmission pattern {self.transmission_pattern}")

    def start(self):
        """
        进行 udp_ip 客户端的启动
        :return:
        """

        # 1. get processes
        self.number_of_processes = self.client_detailed_info.processes if self.client_detailed_info.processes != -1 else int(prompt(qm.QUESTION_FOR_NUMBER_OF_PROCESSES)["processes"])

        # 2. get destination
        if self.client_detailed_info.destinations is None:
            self.selected_destination_ip = self.get_destination_ip(self.client_detailed_info)
        else:
            self.selected_destination_ip = self.get_destination_ip(self.client_detailed_info, self.client_detailed_info.destinations[0])

        # 3. get transmission pattern
        self.transmission_pattern = self.client_detailed_info.transmission_pattern if self.client_detailed_info.transmission_pattern != -1 else tm.TransmissionType.turn_str_into_type(prompt(qm.QUESTION_FOR_PACKET_TRANSMISSION_PATTERN)["pattern"])

        # 4. get destination port
        self.destination_port = self.client_detailed_info.destination_port if self.client_detailed_info.destination_port != -1 else int(prompt(qm.QUESTION_FOR_DESTINATION_PORT)["port"])

        # 5. get sockets
        for i in range(self.number_of_processes):
            socket_tmp = self.create_socket()
            self.sockets.append(socket_tmp)

        # 6. first socket
        self.socket = self.sockets[0]

        # 7. send data
        self.send_data()
