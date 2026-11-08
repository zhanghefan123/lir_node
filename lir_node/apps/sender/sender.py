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
    print(f"get info for batch start | batch size {batch_size} | message size {message_size} | interval {interval}", flush=True)
    if (-1 == batch_size) or (-1 == message_size) or (-1 == interval):
        message_size, batch_size, interval = get_info_for_batch()
    # print("get info for batch end", flush=True)
    content = ("f" * message_size).encode()
    for index in range(batch_size):
        # print(content, (dest_ip, dest_port), flush=True)
        socket_tmp.sendto(content, (dest_ip, dest_port))
        time.sleep(interval)


def get_info_for_duration():
    """Get the duration for a duration-based throughput run."""
    return float(prompt(qm.QUESTION_FOR_DURATION_SECONDS)["seconds"])


def get_info_for_buffer():
    """
    获取 buffer 的大小 (一个 udp 包的大小)
    :return:
    """
    buffer_size = int(prompt(qm.QUESTION_FOR_BUFFER_SIZE)["count"])
    return buffer_size


def send_for_duration(sockets: List[socket.socket], dest_ip: str, dest_port: int,
                      number_of_processes: int, buffer_size: int = -1,
                      duration_seconds: float = -1):
    """
    Send UDP payloads continuously for a fixed wall-clock duration.
    :param sockets:
    :param number_of_processes: 进程数量
    :param dest_ip: 目的 ip
    :param dest_port: 目的端口
    :param buffer_size: 缓冲区大小
    :param duration_seconds: 时间
    :return:
    """
    if buffer_size == -1:
        buffer_size = get_info_for_buffer()
    if duration_seconds <= 0:
        duration_seconds = get_info_for_duration()
    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be positive")

    # 多进程
    processes = []

    # 发送的数据包的总数
    # Use one monotonic start/deadline for all workers so process-spawn skew is
    # not mistaken for a protocol throughput difference.
    scheduled_start = time.perf_counter() + 0.5
    send_packets = Value("i", 0)

    # 锁的定义
    multiprocesses_lock = Lock()

    # 准备进行多进程的发送
    for index in range(number_of_processes):
        modified_dest_port = dest_port + index
        socket_tmp = sockets[index]
        tmp_process = Process(target=send_for_duration_in_single_process,
                              args=(socket_tmp, dest_ip, modified_dest_port,
                                    index, buffer_size, send_packets,
                                    multiprocesses_lock, duration_seconds,
                                    scheduled_start))
        processes.append(tmp_process)

    # 进行所有进程的启动
    for p in processes:
        p.start()

    # 等待所有进程结束
    for p in processes:
        p.join()

    print(
        f"multiprocesses transmission successful | "
        f"duration={duration_seconds:.3f}s | "
        f"sent_packets={send_packets.value}",
        flush=True,
    )


def send_for_duration_in_single_process(socket_tmp: socket.socket, dest_ip: str,
                                        dest_port: int, process_index: int,
                                        buffer_size: int, send_packets: Value,
                                        multiprocesses_lock: Lock,
                                        duration_seconds: float,
                                        scheduled_start: float):
    send_packets_count = 0
    send_string = ("a" * buffer_size).encode()
    print(f"buffer size {buffer_size}", flush=True)
    print(f"process {process_index} start transmission", flush=True)
    while True:
        remaining = scheduled_start - time.perf_counter()
        if remaining <= 0:
            break
        if remaining > 0.002:
            time.sleep(min(remaining / 2, 0.001))

    deadline = scheduled_start + duration_seconds
    while time.perf_counter() < deadline:
        socket_tmp.sendto(send_string, (dest_ip, dest_port))
        send_packets_count += 1
    with multiprocesses_lock:
        send_packets.value += send_packets_count
    print(f"process {process_index} transmission successful", flush=True)
