import os
import re
import time
import socket
from defined_types import types as tm
from modules.config.env_loader import env_loader
from tools.network import interface_rate as irm
from apps.user import server_detailed_info as suim
from multiprocessing import Process, Value, Lock


INITIAL_PACKET_TIMEOUT_SECONDS = 10.0
ACTIVE_STREAM_IDLE_TIMEOUT_SECONDS = 5.0


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

    def handle_file_server(self, socket_tmp: socket.socket,
                           received_packets: Value, received_bytes: Value,
                           first_packet_time: Value,
                           last_packet_time: Value,
                           multiple_processes_lock: Lock):
        """
        进行文件服务器的启动
        :return: None
        """
        received_payload_size = 0
        buffer_size = 1024

        local_first_packet_time = 0.0
        local_last_packet_time = 0.0
        received_packets_count = 0
        first_packet = True
        # 首包需要覆盖服务端启动、HTTP 调度和客户端进程创建时间；开始接收后
        # 再使用较短的空闲超时判断本轮传输已经结束。
        socket_tmp.settimeout(INITIAL_PACKET_TIMEOUT_SECONDS)
        while True:
            try:
                data, addr = socket_tmp.recvfrom(buffer_size)
                packet_time = time.perf_counter()
                if first_packet:
                    first_packet = False
                    local_first_packet_time = packet_time
                    socket_tmp.settimeout(ACTIVE_STREAM_IDLE_TIMEOUT_SECONDS)
                local_last_packet_time = packet_time
                received_packets_count += 1
                received_payload_size += len(data)
            except socket.timeout:
                print("long time not receive message --> break", flush=True)
                break

        # 在结束的时候计算一下 goodput
        local_elapsed = max(
            0.0, local_last_packet_time - local_first_packet_time
        )
        print(f"File received. Active time: {local_elapsed} seconds", flush=True)
        if local_elapsed == 0:
            print(f"Goodput: {0} MBps | {0} Gbps ", flush=True)

        print(f"received bytes {received_payload_size}", flush=True)

        with multiple_processes_lock:
            if local_first_packet_time > 0 and (
                    first_packet_time.value == 0 or
                    local_first_packet_time < first_packet_time.value):
                first_packet_time.value = local_first_packet_time
            if local_last_packet_time > last_packet_time.value:
                last_packet_time.value = local_last_packet_time
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

    def handle_multiprocess_file_server_v2(self):
        """Measure one isolated throughput window with consistent accounting.

        Application goodput is based on UDP payload delivered to the sockets.
        Link throughput is based on RX bytes across the node's experiment data
        interfaces. Both use the same global first-packet/last-packet interval
        across all receiver processes.
        """
        interface_pattern = re.compile(r"^ln\d+_idx\d+$")
        target_interfaces = sorted(
            interface_name
            for interface_name in os.listdir("/sys/class/net")
            if interface_pattern.match(interface_name)
        )
        if not target_interfaces:
            raise RuntimeError("no experiment data interfaces matched ln<node>_idx<link>")

        def read_total_rx_bytes():
            return sum(
                irm.get_interface_rx_bytes(interface_name=interface_name)
                for interface_name in target_interfaces
            )

        rx_bytes_start = read_total_rx_bytes()
        received_packets = Value("q", 0)
        received_payload_bytes = Value("q", 0)
        first_packet_time = Value("d", 0.0)
        last_packet_time = Value("d", 0.0)
        aggregate_lock = Lock()
        server_processes = []

        for process_index in range(
                self.server_detailed_info.selected_number_of_processes):
            current_port = (
                    self.server_detailed_info.selected_listen_port + process_index
            )
            receiver_socket = self.create_socket(current_port)
            process = Process(
                target=self.handle_file_server,
                args=(
                    receiver_socket,
                    received_packets,
                    received_payload_bytes,
                    first_packet_time,
                    last_packet_time,
                    aggregate_lock,
                ),
            )
            server_processes.append(process)

        for process in server_processes:
            process.start()
        for process in server_processes:
            process.join()

        rx_bytes_end = read_total_rx_bytes()
        received_total_bytes = max(0, rx_bytes_end - rx_bytes_start)
        elapsed_seconds = max(
            0.0, last_packet_time.value - first_packet_time.value
        )

        if elapsed_seconds <= 0 or received_packets.value <= 0:
            result = (
                "Result format version: 2\n"
                "Status: no_samples\n"
                f"Measured interfaces: {','.join(target_interfaces)}\n"
                f"Received total bytes: {received_total_bytes}\n"
                f"Received payload bytes: {received_payload_bytes.value}\n"
                f"Received packets: {received_packets.value}\n"
                f"Time Elapsed: {elapsed_seconds:.9f}\n"
            )
        else:
            throughput_mib_s = received_total_bytes / elapsed_seconds / (2 ** 20)
            throughput_gibit_s = received_total_bytes * 8 / elapsed_seconds / (2 ** 30)
            throughput_mb_s = received_total_bytes / elapsed_seconds / 1e6
            throughput_gbit_s = received_total_bytes * 8 / elapsed_seconds / 1e9
            goodput_mib_s = received_payload_bytes.value / elapsed_seconds / (2 ** 20)
            goodput_gibit_s = received_payload_bytes.value * 8 / elapsed_seconds / (2 ** 30)
            goodput_mb_s = received_payload_bytes.value / elapsed_seconds / 1e6
            goodput_gbit_s = received_payload_bytes.value * 8 / elapsed_seconds / 1e9
            goodput_ratio = (
                received_payload_bytes.value / received_total_bytes * 100
                if received_total_bytes > 0 else 0.0
            )
            result = (
                "Result format version: 2\n"
                "Status: success\n"
                "Measurement window: global first to last received application packet\n"
                "Total-byte scope: Linux RX byte counters over all ln*_idx* data interfaces\n"
                f"Measured interfaces: {','.join(target_interfaces)}\n"
                f"Receiver processes: {self.server_detailed_info.selected_number_of_processes}\n"
                f"Received total bytes: {received_total_bytes}\n"
                f"Received payload bytes: {received_payload_bytes.value}\n"
                f"Received packets: {received_packets.value}\n"
                f"Time Elapsed: {elapsed_seconds:.9f}\n"
                f"Throughput: {throughput_mib_s:.9f} MiB/s | "
                f"{throughput_gibit_s:.9f} Gibit/s\n"
                f"Throughput decimal: {throughput_mb_s:.9f} MB/s | "
                f"{throughput_gbit_s:.9f} Gbit/s\n"
                f"Goodput: {goodput_mib_s:.9f} MiB/s | "
                f"{goodput_gibit_s:.9f} Gibit/s\n"
                f"Goodput decimal: {goodput_mb_s:.9f} MB/s | "
                f"{goodput_gbit_s:.9f} Gbit/s\n"
                f"Goodput ratio: {goodput_ratio:.9f}%\n"
            )

        selected_network_layer_str = tm.NetworkLayer.turn_type_into_str(
            self.server_detailed_info.selected_network_layer
        )
        if self.server_detailed_info.selected_experiment_name:
            filename = f"/result/{self.server_detailed_info.selected_experiment_name}"
        elif self.server_detailed_info.selected_network_layer in (
                tm.NetworkLayer.MULTICAST_SELIR,
                tm.NetworkLayer.MULTICAST_OPT):
            filename = (
                f"/result/{selected_network_layer_str}_destinations_"
                f"{self.server_detailed_info.number_of_destinations}_processes_"
                f"{self.server_detailed_info.selected_number_of_processes}.txt"
            )
        else:
            filename = (
                f"/result/{selected_network_layer_str}_result_node_name_"
                f"{env_loader.container_name}_processes_"
                f"{self.server_detailed_info.selected_number_of_processes}_index_"
                f"{self.server_detailed_info.simulation_index}.txt"
            )

        is_multicast = self.server_detailed_info.selected_network_layer in (
            tm.NetworkLayer.MULTICAST_SELIR,
            tm.NetworkLayer.MULTICAST_OPT,
        )
        with open(filename, "a" if is_multicast else "w") as result_file:
            result_file.write(result + ("\n" if is_multicast else ""))
        print(result, flush=True)

    def create_socket(self, current_port: int) -> socket.socket:
        if self.server_detailed_info.selected_ip_version == tm.IpVersion.Ipv4:
            socket_tmp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_tmp.settimeout(INITIAL_PACKET_TIMEOUT_SECONDS)
            socket_tmp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            socket_tmp.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 16 * 1024 * 1024)
            socket_tmp.bind((self.all_interface_address, current_port))
            return socket_tmp
        elif self.server_detailed_info.selected_ip_version == tm.IpVersion.Ipv6:
            socket_tmp = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            socket_tmp.settimeout(INITIAL_PACKET_TIMEOUT_SECONDS)
            socket_tmp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            socket_tmp.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 16 * 1024 * 1024)
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
            self.handle_multiprocess_file_server_v2()
        else:
            raise Exception("unsupported server type")
