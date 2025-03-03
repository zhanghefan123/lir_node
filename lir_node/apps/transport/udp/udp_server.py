import time
import socket
from tools.network import interface_rate as irm
from apps.user import server_user_input as suim


class UdpServer:
    def __init__(self, server_user_input: suim.ServerUserInput):
        self.socket_tmp = None
        self.server_user_input = server_user_input
        self.all_interface_address = None

    def handle_text_server(self):
        """
        进行文本服务器的启动
        :return: None
        """
        self.socket_tmp.bind((self.all_interface_address, self.server_user_input.selected_listen_port))
        print(f"text server listening on {self.all_interface_address}:{self.server_user_input.selected_listen_port}", flush=True)
        while True:
            data, address = self.socket_tmp.recvfrom(1024)
            data = data.decode()
            if data == "exit":
                break
            else:
                print(data, flush=True)

    def handle_file_server(self):
        """
        进行文件服务器的启动
        :return: None
        """
        received_payload_size = 0
        buffer_size = 1024
        selected_listen_port = self.server_user_input.selected_listen_port
        selected_interface_name = self.server_user_input.selected_interface_name
        self.socket_tmp.bind((self.all_interface_address, selected_listen_port))
        print(f"file server listening on {self.all_interface_address}:{selected_listen_port} "
              f"and interface {selected_interface_name}", flush=True)
        rx_bytes_start = irm.get_interface_rx_bytes(interface_name=selected_interface_name)
        start = 0
        first_packet = True
        while True:
            data, addr = self.socket_tmp.recvfrom(buffer_size)
            if first_packet:
                first_packet = False
                start = time.time()
            content = data.decode()
            if content == "stop":
                time_elapsed = time.time() - start
                break
            received_payload_size += len(data)
        rx_bytes_end = irm.get_interface_rx_bytes(interface_name=selected_interface_name)
        # 在结束的时候计算一下 goodput
        print(f"File received. Total time: {time_elapsed} seconds", flush=True)
        print(f"Goodput: {received_payload_size / time_elapsed / 1024 / 1024} MB/s", flush=True)
        print(f"Throughput: {(rx_bytes_end - rx_bytes_start) / time_elapsed / 1024 / 1024} MB/s", flush=True)

    def create_socket(self):
        if self.server_user_input.selected_ip_version == "IPv4":
            self.socket_tmp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif self.server_user_input.selected_ip_version == "IPv6":
            self.socket_tmp = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        else:
            raise Exception("unsupported ip version")

    def set_all_interface_address(self):
        if self.server_user_input.selected_ip_version == "IPv4":
            self.all_interface_address = "0.0.0.0"
        elif self.server_user_input.selected_ip_version == "IPv6":
            self.all_interface_address = "::"
        else:
            raise Exception("unsupported ip version")

    def start(self):
        self.create_socket()
        self.set_all_interface_address()
        if self.server_user_input.selected_server_type == "text":
            self.handle_text_server()
        elif self.server_user_input.selected_server_type == "file":
            self.handle_file_server()
        else:
            raise Exception("unsupported server type")
