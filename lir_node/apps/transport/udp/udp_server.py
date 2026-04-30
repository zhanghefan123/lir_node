import time
import socket
from defined_types import types as tm
from modules.config.env_loader import env_loader
from tools.network import interface_rate as irm
from apps.user import server_detailed_info as suim
from multiprocessing import Process, Value, Lock


def start_server(server_detailed_info: suim.ServerDetailedInfo):
    # 获取用户输入
    udp_server = UdpServer(server_detailed_info)
    # 启动 udp server
    udp_server.start()


class UdpServer:
    def __init__(self, server_detailed_info: suim.ServerDetailedInfo):
        self.socket_tmp = None
        self.socket_list = []
        self.server_detailed_info = server_detailed_info
        self.all_interface_address = None

    def handle_text_server(self):
        """
        进行文本服务器的启动
        :return: None
        """
        print(f"text server listening on {self.all_interface_address}:{self.server_detailed_info.selected_listen_port}",
              flush=True)
        while True:
            try:
                data, address = self.socket_tmp.recvfrom(1024)
                print("received", flush=True)
            except socket.timeout:
                print("long time not receive message --> break", flush=True)
                break

    def handle_file_server(self, socket_tmp: socket.socket, received_packets: Value, received_bytes: Value,
                           final_time_elapsed: Value, multiple_processes_lock: Lock):
        """
        进行文件服务器的启动
        :return: None
        """
        received_payload_size = 0
        buffer_size = 1024

        start = 0
        time_elapsed = 0
        received_packets_count = 0
        first_packet = True
        while True:
            try:
                data, addr = socket_tmp.recvfrom(buffer_size)
                if first_packet:
                    first_packet = False
                    start = time.time()
                else:
                    time_elapsed = time.time() - start
                received_packets_count += 1
                received_payload_size += len(data)
            except socket.timeout:
                print("long time not receive message --> break", flush=True)
                break

        # 在结束的时候计算一下 goodput
        print(f"File received. Total time: {time_elapsed} seconds", flush=True)
        if time_elapsed == 0:
            print(f"Goodput: {0} MBps | {0} Gbps ", flush=True)

        print(f"received bytes {received_payload_size}", flush=True)

        with multiple_processes_lock:
            if time_elapsed > final_time_elapsed.value:
                final_time_elapsed.value = time_elapsed
            received_bytes.value += received_payload_size
            received_packets.value += received_packets_count

    def handle_file_server_with_real_time_speed_recording_capbaility(self):
        # 进行接口名的获取
        selected_interface_name = self.server_detailed_info.selected_interface_name
        # 进行 socket 的创建
        socket_tmp = self.create_socket(self.server_detailed_info.selected_listen_port)
        # 利用 socket 进行实时的数据量的统计
        received_payload_size = 0
        buffer_size = 1024
        first_packet = True
        last_record_time = 0
        goodput_list = []
        throughput_list = []
        rx_bytes_previous = irm.get_interface_rx_bytes(interface_name=selected_interface_name)
        while True:
            try:
                data, addr = socket_tmp.recvfrom(buffer_size)
                received_payload_size += len(data)
                if first_packet:
                    first_packet = False
                    last_record_time = time.time()
                else:
                    time_elapsed = time.time() - last_record_time
                    if time_elapsed >= 1.0:
                        rx_bytes_now = irm.get_interface_rx_bytes(interface_name=selected_interface_name)
                        goodput = received_payload_size * 8 / time_elapsed / 1024 / 1024
                        throughput = (rx_bytes_now - rx_bytes_previous) * 8 / time_elapsed / 1024 / 1024
                        goodput_list.append(goodput)
                        throughput_list.append(throughput)
                        # 进行更新
                        last_record_time = time.time()
                        rx_bytes_previous = rx_bytes_now
                        received_payload_size = 0

            except socket.timeout:
                print(f"goodput list: {goodput_list}", flush=True)
                print(f"throughput list: {throughput_list}", flush=True)
                print("long time not receive message --> break", flush=True)
                break

    def handle_multiprocess_file_server(self):
        # 进行接口名的获取
        selected_interface_name = self.server_detailed_info.selected_interface_name

        # 进行接收数据量的获取
        # rx_bytes_start = 0
        rx_bytes_start = irm.get_interface_rx_bytes(interface_name=selected_interface_name)
        # rx_bytes_start += irm.get_interface_rx_bytes(interface_name="ln26_idx1")
        # rx_bytes_start += irm.get_interface_rx_bytes(interface_name="ln26_idx2")
        # rx_bytes_start += irm.get_interface_rx_bytes(interface_name="ln26_idx3")

        # 进行所有的遍历
        server_processes = []
        # received packets
        received_packets = Value("q", 0)
        # final value
        received_bytes = Value("q", 0)
        # time elapsed value
        time_elapsed = Value("f", 0)
        # value lock
        multiple_processes_lock = Lock()

        # 进行进程的启动
        for index in range(self.server_detailed_info.number_of_processes):
            current_port = self.server_detailed_info.selected_listen_port + index
            socket_tmp = self.create_socket(current_port)
            server_process_tmp = Process(target=self.handle_file_server, args=(socket_tmp, received_packets,
                                                                               received_bytes, time_elapsed,
                                                                               multiple_processes_lock))
            server_processes.append(server_process_tmp)
        for server_process in server_processes:
            server_process.start()
        for server_process in server_processes:
            server_process.join()

        time.sleep(5)
        # rx_bytes_end = 0
        rx_bytes_end = irm.get_interface_rx_bytes(interface_name=selected_interface_name)
        # rx_bytes_end += irm.get_interface_rx_bytes(interface_name="ln26_idx1")
        # rx_bytes_end += irm.get_interface_rx_bytes(interface_name="ln26_idx2")
        # rx_bytes_end += irm.get_interface_rx_bytes(interface_name="ln26_idx3")

        received_total_bytes = rx_bytes_end - rx_bytes_start
        # 进行结果的展示
        with multiple_processes_lock:
            selected_network_layer_str = tm.NetworkLayer.turn_type_into_str(
                self.server_detailed_info.selected_network_layer)
            if self.server_detailed_info.selected_network_layer == tm.NetworkLayer.MULTIPATH_SELIR or self.server_detailed_info.selected_network_layer == tm.NetworkLayer.MULTICAST_OPT:
                filename = f"/result/{selected_network_layer_str}_destinations_{self.server_detailed_info.number_of_destinations}_processes_{self.server_detailed_info.number_of_processes}.txt"
                result = f"Received total bytes: {received_total_bytes}\n"
                result += f"Time Elapsed: {time_elapsed.value}\n"
                result += f"Throughput: {received_total_bytes / time_elapsed.value / 1024 / 1024} MBps | {received_total_bytes / time_elapsed.value / 1024 / 1024 / 1024 * 8} Gbps\n"
                result += f"Goodput: {received_bytes.value / time_elapsed.value / 1024 / 1024} MBps | {received_bytes.value / time_elapsed.value / 1024 / 1024 / 1024 * 8} Gbps \n"
                result += f"Goodput ratio: {received_bytes.value / received_total_bytes * 100}%\n"
                with open(filename, "a") as f:
                    f.write(result + "\n")
                print(result, flush=True)
            else:
                filename = f"/result/{selected_network_layer_str}_result_node_name_{env_loader.container_name}_processes_{self.server_detailed_info.number_of_processes}_index_{self.server_detailed_info.simulation_index}.txt"
                result = ""
                result += f"Received total bytes: {received_total_bytes} | Throughput: {received_total_bytes / time_elapsed.value / 1024 / 1024} MBps | {received_total_bytes / time_elapsed.value / 1024 / 1024 / 1024 * 8} Gbps"
                result += "\n"
                result += f"Received payload bytes: {received_bytes.value} | Received packets: {received_packets.value} | Goodput: {received_bytes.value / time_elapsed.value / 1024 / 1024} MBps | {received_bytes.value / time_elapsed.value / 1024 / 1024 / 1024 * 8} Gbps"
                result += "\n"
                result += f"Goodput ratio: {received_bytes.value / received_total_bytes * 100}%"
                with open(filename, 'w') as f:
                    f.write(result)

                print(
                    f"Received total bytes: {received_total_bytes} | Throughput: {received_total_bytes / time_elapsed.value / 1024 / 1024} MBps | {received_total_bytes / time_elapsed.value / 1024 / 1024 / 1024 * 8} Gbps",
                    flush=True)
                print(
                    f"Received payload bytes: {received_bytes.value} | Received packets: {received_packets.value} | Goodput: {received_bytes.value / time_elapsed.value / 1024 / 1024} MBps | {received_bytes.value / time_elapsed.value / 1024 / 1024 / 1024 * 8} Gbps ",
                    flush=True)
                print(f"Goodput ratio: {received_bytes.value / received_total_bytes * 100}%", flush=True)

    def create_socket(self, current_port: int) -> socket.socket:
        if self.server_detailed_info.selected_ip_version == tm.IpVersion.Ipv4:
            socket_tmp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_tmp.settimeout(10)
            socket_tmp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            # socket_tmp.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024 * 1024 * 100)
            socket_tmp.bind((self.all_interface_address, current_port))
            return socket_tmp
        elif self.server_detailed_info.selected_ip_version == tm.IpVersion.Ipv6:
            socket_tmp = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            socket_tmp.settimeout(10)
            socket_tmp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            # socket_tmp.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024 * 1024 * 100)
            socket_tmp.bind((self.all_interface_address, current_port))
            return socket_tmp
        else:
            raise Exception("unsupported ip version")

    def set_all_interface_address(self):
        if self.server_detailed_info.selected_ip_version == tm.IpVersion.Ipv4:
            self.all_interface_address = "0.0.0.0"
        elif self.server_detailed_info.selected_ip_version == tm.IpVersion.Ipv6:
            self.all_interface_address = "::"
        else:
            raise Exception("unsupported ip version")

    def start(self):
        self.set_all_interface_address()
        if self.server_detailed_info.selected_server_type == tm.ServerType.TEXT:
            self.socket_tmp = self.create_socket(self.server_detailed_info.selected_listen_port)
            self.handle_text_server()
        elif self.server_detailed_info.selected_server_type == tm.ServerType.FILE:
            # self.handle_multiprocess_file_server()
            self.handle_file_server_with_real_time_speed_recording_capbaility()
        elif self.server_detailed_info.selected_server_type == tm.ServerType.MULTIPROCESS_FILE:
            self.handle_multiprocess_file_server()
        else:
            raise Exception("unsupported server type")
