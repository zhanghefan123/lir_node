import sys
from modules.http_service import http_service as hsm
from modules.frr import frr_manager as fmm
from signal_decorator import exit_signal_listener
from modules.kernel import kernel_configurator as kcm
from apps.user import user_input as uim
from apps.transport.udp import udp_client as ucm


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
    if (len(sys.argv)) == 2 and (sys.argv[1] == "client"): # client 处理逻辑
        # 获取用户输入
        user_input = uim.UserInput()
        # 调用 udp_client
        udp_client = ucm.UdpClient(user_input)
    elif (len(sys.argv)) == 2 and (sys.argv[1] == "server"): # server 处理逻辑
        # 获取用户输入
        user_input = uim.UserInput()
        # 调用 udp_server
        udp_server = ucm.
    else: # 正常逻辑
        starter = Starter()
        starter.main_logic()
