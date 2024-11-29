import time
import socket
from apps.user import server_user_input as suim


class UdpServer:
    def __init__(self, server_user_input: suim.ServerUserInput):
        self.socket_tmp = None
        self.server_user_input = server_user_input

    def handle_text_server(self):
        """
        进行文本服务器的启动
        :return: None
        """
        all_interface_address = "0.0.0.0"
        self.socket_tmp.bind((all_interface_address, self.server_user_input.selected_listen_port))
        print(f"text server listening on {all_interface_address}:{self.server_user_input.selected_listen_port}", flush=True)
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
        all_interface_address = "0.0.0.0"
        buffer_size = 1024
        self.socket_tmp.bind((all_interface_address, self.server_user_input.selected_listen_port))
        print(f"file server listening on {all_interface_address}:{self.server_user_input.selected_listen_port}", flush=True)
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
        print(f"File received. Total time: {time_elapsed} seconds", flush=True)

    def create_socket(self):
        self.socket_tmp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        self.create_socket()
        if self.server_user_input.selected_server_type == "text":
            self.handle_text_server()
        elif self.server_user_input.selected_server_type == "file":
            self.handle_file_server()
        else:
            return
