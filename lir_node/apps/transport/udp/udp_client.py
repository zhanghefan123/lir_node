from apps.user import client_user_input as uim
from defined_types import types as tm
from apps.network.ip import udp_ip_client as uihm
from apps.network.lir import udp_lir_client as ulhm


class UdpClient:
    def __init__(self, client_user_input: uim.ClientUserInput):
        """
        初始化 udp_client
        :param client_user_input:
        """
        self.client_user_input = client_user_input

    def start(self):
        """
        进行 udp_client 的启动
        :return: None
        """
        # 如果网络层选择为 ip
        if self.client_user_input.selected_network_layer == tm.NetworkLayer.IP:
            udp_ip_handler = uihm.UdpIpClient(self.client_user_input)
            udp_ip_handler.start()
        # 如果网络层选择为 lir
        elif self.client_user_input.selected_network_layer == tm.NetworkLayer.LIR:
            udp_lir_handler = ulhm.UdpLiRClient(self.client_user_input)
            udp_lir_handler.start()
        else:
            # 否则就是不支持的网络层
            raise Exception("unsupported network layer")
