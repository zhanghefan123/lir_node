import socket
import time
from tools import file as fm
from PyInquirer import prompt
from apps.user import questions as qm


def send_in_single(socket_tmp: socket.socket, dest_ip: str, dest_port: int):
    """
    进行逐个消息的发送，用于测试
    :param socket_tmp: socket 变量
    :param dest_ip: 目的地址
    :param dest_port: 目的端口
    :return:
    """
    while True:
        send_message = input("请输入要发送的内容: (quit to exit)")
        if send_message == "quit":
            break
        else:
            socket_tmp.sendto(send_message.encode(), (dest_ip, dest_port))


def get_info_for_batch():
    """
    获取 message_size, batch_size, send_interval
    :return:
    """
    message_size = int(prompt(qm.QUESTION_FOR_MESSAGE_SIZE)["count"])
    batch_size = int(prompt(qm.QUESTION_FOR_BATCH_SIZE)["count"])
    interval = float(prompt(qm.QUESTION_FOR_SEND_INTERVAL)["interval"])
    return message_size, batch_size, interval


def send_in_batch(socket_tmp: socket.socket, dest_ip: str, dest_port: int):
    """
    进行批量的消息的发送
    :param socket_tmp: socket 变量
    :param dest_ip: 目的 ip
    :param dest_port: 目的端口
    :return:
    """
    message_size, batch_size, interval = get_info_for_batch()
    send_message = ("f" * message_size).encode()
    for index in range(batch_size):
        socket_tmp.sendto(send_message, (dest_ip, dest_port))
        time.sleep(interval)
        if index % 100 == 0:
            print(f"current send {index} packets", flush=True)


def get_info_for_file():
    """
    获取 file_size
    :return:
    """
    file_size = int(prompt(qm.QUESTION_FOR_FILE_SIZE)["count"])
    return file_size


def send_file(socket_tmp: socket.socket, dest_ip: str, dest_port: int, buffer_size=1024):
    """
    进行文件的发送
    :param socket_tmp: socket 变量
    :param dest_ip: 目的 ip
    :param dest_port: 目的端口
    :param buffer_size: 缓冲区大小
    :return:
    """
    file_size = get_info_for_file()
    tmp_file_path = "tmp_file.txt"
    file_size = fm.generate_txt_file(tmp_file_path, file_size)
    stop_signal = "stop".encode()
    with open(tmp_file_path, "rb") as f:
        bytes_sent = 0
        while bytes_sent < file_size:
            chunk = f.read(buffer_size)
            socket_tmp.sendto(chunk, (dest_ip, dest_port))
            bytes_sent += len(chunk)
        socket_tmp.sendto(stop_signal, (dest_ip, dest_port))
    print("File transmission successful", flush=True)
