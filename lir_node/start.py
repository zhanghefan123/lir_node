import sys
from modules.http_service import http_service as hsm
from modules.frr import frr_manager as fmm
from signal_decorator import exit_signal_listener
from modules.kernel import kernel_configurator as kcm
from apps.user import client_user_input as cuim
from apps.user import server_user_input as suim
from apps.transport.udp import udp_client as ucm
from apps.transport.udp import udp_server as usm


flask_process = None


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
        fmm.start_frr()
        kcm.load_lir_configuration()
        hsm.start_flask_http_service()  # 这是一个死循环


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
