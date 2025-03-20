import sys
import time
from asyncio import wait_for

from modules.config import interface_loader as ilm
from modules.config.env_loader import env_loader
from modules.config.interface_loader import is_all_interfaces_available
from modules.http_service import http_service as hsm
from modules.frr import frr_manager as fmm
from signal_decorator import exit_signal_listener
from modules.kernel import kernel_configurator as kcm
from apps.user import client_user_input as cuim
from apps.user import server_user_input as suim
from apps.transport.udp import udp_client as ucm
from apps.transport.udp import udp_server as usm
from modules.srv6 import srv6_manager as smm


flask_process = None


def wait_for_all_interfaces_available():
    """
    等待所有的接口都可用
    :return:
    """
    while True:
        if is_all_interfaces_available(ilm.load_interfaces()):
            break
        time.sleep(1)


class Starter:
    def __init__(self):
        pass

    @exit_signal_listener.signal_decorator
    def main_logic(self):
        """
        主逻辑
            1. 启动 frr
            2. 启动 无限循环
        :return:
        """
        fmm.start_frr()  # 启动 frr
        wait_for_all_interfaces_available()
        kcm.load_lir_configuration()  # 加载 lir 配置 (这个仅仅会在 all interfaces available 之后进行注入)
        if "true" == env_loader.enable_srv6:
            srv6_routes = smm.read_srv6_routes()  # 进行 srv6 routes 的读取 (放在 load_lir_configuration 之后)
            smm.insert_srv6_routes(srv6_routes)   # 进行 srv6 routes 的插入 (放在 load_lir_configuration 之后)
        # hsm.start_flask_http_service()  # 这是一个死循环
        while True:
            time.sleep(1)


if __name__ == "__main__":
    if (len(sys.argv)) == 2 and (sys.argv[1] == "client"):  # client 处理逻辑
        # 获取用户输入
        client_user_input = cuim.ClientUserInput()
        # 创建 udp_client
        udp_client = ucm.UdpClient(client_user_input)
        # 启动 udp_client
        udp_client.start()
    elif (len(sys.argv)) == 2 and (sys.argv[1] == "server"):  # server 处理逻辑
        # 获取用户输入
        server_user_input = suim.ServerUserInput()
        # 调用 udp_server
        udp_server = usm.UdpServer(server_user_input)
        # 启动 udp_server
        udp_server.start()
    else:  # 正常逻辑
        starter = Starter()
        starter.main_logic()
