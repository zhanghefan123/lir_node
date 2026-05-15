import socket
import time
from PyInquirer import prompt
from apps.user import questions as qm
from multiprocessing import Process, Lock, Value
from typing import List


def send_in_single(socket_tmp: socket.socket, dest_ip: str, dest_port: int, content: str = ""):
    """
    进行逐个消息的发送，用于测试
    :param content: 实际要发送的内容
    :param socket_tmp: socket 变量
    :param dest_ip: 目的地址
    :param dest_port: 目的端口
    :return:
    """
    if content == "":
        while True:
            send_message = input("请输入要发送的内容: (quit to exit)")
            if send_message == "quit":
                break
            else:
                socket_tmp.sendto(send_message.encode(), (dest_ip, dest_port))
    else:
        print(f"send content: {content}", flush=True)
        socket_tmp.sendto(content.encode(), (dest_ip, dest_port))


def get_info_for_batch():
    """
    获取 message_size, batch_size, send_interval
    :return:
    """
    message_size = int(prompt(qm.QUESTION_FOR_MESSAGE_SIZE)["count"])
    batch_size = int(prompt(qm.QUESTION_FOR_BATCH_SIZE)["count"])
    interval = float(prompt(qm.QUESTION_FOR_SEND_INTERVAL)["interval"])
    return message_size, batch_size, interval


def send_batch_with_status(absolute_start_time, packet_index: int, socket_tmp: socket.socket, dest_ip: str,
                           dest_port: int, batch_size: int = -1, message_size: int = -1, interval: float = -1) -> int:
    """
    进行批量的消息的发送
    :param absolute_start_time 绝对启动时间
    :param packet_index 批次的索引
    :param batch_size: 一个批次的大小
    :param message_size: 一个消息的大小
    :param interval: 消息的间隔
    :param socket_tmp: socket 变量
    :param dest_ip: 目的 ip
    :param dest_port: 目的端口
    :return:
    """
    content = ("f" * message_size).encode()
    current_packet_index = packet_index
    get_time = time.perf_counter
    for _ in range(batch_size):
        target_time = absolute_start_time + (current_packet_index * interval)
        while True:
            current_time = get_time()
            if current_time < target_time:
                continue
            else:
                break
        current_packet_index += 1
        socket_tmp.sendto(content, (dest_ip, dest_port))
    return current_packet_index


def send_in_batch(socket_tmp: socket.socket, dest_ip: str, dest_port: int, batch_size: int = -1, message_size: int = -1,
                  interval: float = -1):
    """
    进行批量的消息的发送
    :param batch_size: 一个批次的大小
    :param message_size: 一个消息的大小
    :param interval: 消息的间隔
    :param socket_tmp: socket 变量
    :param dest_ip: 目的 ip
    :param dest_port: 目的端口
    :return:
    """
    if (-1 == batch_size) or (-1 == message_size) or (-1 == interval):
        message_size, batch_size, interval = get_info_for_batch()
    content = ("f" * message_size).encode()
    for index in range(batch_size):
        socket_tmp.sendto(content, (dest_ip, dest_port))
        time.sleep(interval)


def get_info_for_file():
    """
    获取 file_size
    :return:
    """
    file_size = int(prompt(qm.QUESTION_FOR_FILE_SIZE)["count"])
    return file_size


def get_info_for_buffer():
    """
    获取 buffer 的大小 (一个 udp 包的大小)
    :return:
    """
    buffer_size = int(prompt(qm.QUESTION_FOR_BUFFER_SIZE)["count"])
    return buffer_size


def send_file(sockets: List[socket.socket], dest_ip: str, dest_port: int, number_of_processes: int, file_size: int = -1,
              buffer_size: int = -1):
    """
    进行文件的发送
    :param sockets:
    :param number_of_processes: 进程数量
    :param dest_ip: 目的 ip
    :param dest_port: 目的端口
    :param number_of_processes 进程数量
    :param file_size 文件大小
    :param buffer_size: 缓冲区大小
    :return:
    """
    # 获取文件信息
    if file_size == -1:
        file_size = get_info_for_file()

    if buffer_size == -1:
        buffer_size = get_info_for_buffer()

    # 多进程
    processes = []

    # 发送的数据包的总数
    send_packets = Value("i", 0)

    # 锁的定义
    multiprocesses_lock = Lock()

    # 准备进行多进程的发送
    for index in range(number_of_processes):
        modified_dest_port = dest_port + index
        socket_tmp = sockets[index]
        tmp_process = Process(target=send_file_in_single_process, args=(
            socket_tmp, dest_ip, modified_dest_port, index, file_size, buffer_size, send_packets, multiprocesses_lock))
        processes.append(tmp_process)

    # 进行所有进程的启动
    for p in processes:
        p.start()

    # 等待所有进程结束
    for p in processes:
        p.join()

    print(f"multiprocesses transmission successful sending {send_packets.value} packets", flush=True)


def send_file_in_single_process(socket_tmp: socket.socket, dest_ip: str, dest_port: int, tmp_file_index: int,
                                file_size: int, buffer_size: int, send_packets: Value, multiprocesses_lock: Lock):
    # tmp_file_path = f"tmp_file_{tmp_file_index}.txt"
    # file_size = fm.generate_txt_file(tmp_file_path, file_size)
    send_packets_count = 0
    # with open(tmp_file_path, "rb") as f:
    bytes_sent = 0
    send_string = ("a" * buffer_size).encode()
    print(f"buffer size {buffer_size}", flush=True)
    print(f"process {tmp_file_index} start transmission", flush=True)
    while bytes_sent < file_size * 1024 * 1024:
        socket_tmp.sendto(send_string, (dest_ip, dest_port))
        bytes_sent += len(send_string)
        send_packets_count += 1
    with multiprocesses_lock:
        send_packets.value += send_packets_count
    print(f"process {tmp_file_index} transmission successful", flush=True)
