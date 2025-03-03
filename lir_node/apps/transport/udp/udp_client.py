from apps.user import client_user_input as uim
from defined_types import types as tm
from apps.network.ip import udp_ip_client as uihm
from apps.network.lir import udp_other_client as ulhm


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
        # 如果网络层选择为 ip 或者 srv6
        if self.client_user_input.selected_network_layer == tm.NetworkLayer.IP or self.client_user_input.selected_network_layer == tm.NetworkLayer.SRV6:
            udp_ip_handler = uihm.UdpIpClient(self.client_user_input, self.client_user_input.selected_network_layer)
            udp_ip_handler.start()
        # 如果网络层选择为 lir
        elif (self.client_user_input.selected_network_layer == tm.NetworkLayer.LIR or
              self.client_user_input.selected_network_layer == tm.NetworkLayer.ICING or
              self.client_user_input.selected_network_layer == tm.NetworkLayer.OPT or
              self.client_user_input.selected_network_layer == tm.NetworkLayer.SELIR or
              self.client_user_input.selected_network_layer == tm.NetworkLayer.FAST_SELIR or
              self.client_user_input.selected_network_layer == tm.NetworkLayer.MULTICAST_SELIR):
            udp_lir_handler = ulhm.UdpOtherClient(self.client_user_input, self.client_user_input.selected_network_layer)
            udp_lir_handler.start()
        else:
            # 否则就是不支持的网络层
            raise Exception("unsupported network layer")
