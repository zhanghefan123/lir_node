import sys
import time
from modules.config import interface_loader as ilm
from modules.config.env_loader import env_loader
from modules.config.interface_loader import is_all_interfaces_available
from modules.frr import frr_manager as fmm
from signal_decorator import exit_signal_listener
from apps.user import server_detailed_info as suim
from apps.user import client_detailed_info as cdim
from apps.transport.udp import udp_client as ucm
from apps.transport.udp import udp_server as usm
from modules.srv6 import srv6_manager as smm
from modules.server import http_server as hsm
from modules.tc import tc as tcm
from modules.kernel import kernel_configurator as kcm


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
        wait_for_all_interfaces_available()  # 等待所有接口准备完毕
        # if env_loader.node_id == 1:
        #     tcm.setup_tbf_qdisc()  # 进行源的接口的带宽设置
        kcm.load_kernel_configuration()  # 加载 lir 配置 (这个仅仅会在 all interfaces available 之后进行注入)
        if "true" == env_loader.enable_srv6:
            srv6_routes = smm.read_srv6_routes()  # 进行 srv6 routes 的读取 (放在 load_lir_configuration 之后)
            smm.insert_srv6_routes(srv6_routes)   # 进行 srv6 routes 的插入 (放在 load_lir_configuration 之后)
        hsm.start_flask_http_service()  # 进行 http 服务的启动

    def main_logic_for_raspberrypi(self):
        kcm.load_kernel_configuration()  # 加载 lir 配置 (这个仅仅会在 all interfaces available 之后进行注入)
        if "true" == env_loader.enable_srv6:
            print("zhf add code: insert srv6 route")
            srv6_routes = smm.read_srv6_routes()  # 进行 srv6 routes 的读取 (放在 load_lir_configuration 之后)
            print(srv6_routes)
            smm.insert_srv6_routes(srv6_routes)  # 进行 srv6 routes 的插入 (放在 load_lir_configuration 之后)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == "client":  # client 处理逻辑
            # 获取客户端信息
            client_detailed_info = cdim.ClientDetailedInfo()
            # 获取初始信息
            client_detailed_info.get_basic_level_user_input()
            # 启动 udp_client
            ucm.start_client(client_detailed_info)
        elif sys.argv[1] == "server":  # server 处理逻辑
            # 创建服务器信息
            server_detailed_info = suim.ServerDetailedInfo()
            # 获取用户输入
            server_detailed_info.get_user_input()
            # 调用 udp_server
            usm.start_server(server_detailed_info)
        elif sys.argv[1] == "raspberrypi":  # raspberrypi
            starter = Starter()
            starter.main_logic_for_raspberrypi()
        elif sys.argv[1] == "container":  # 容器启动的时候需要加载路由表项以及接口表项
            starter = Starter()
            starter.main_logic()
    else:
        print("user should input the client/server/raspberrypi/container")






