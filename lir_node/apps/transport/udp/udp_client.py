from apps.user import client_user_input as uim
from defined_types import types as tm
from apps.network.ip import udp_ip_handler as uihm
from apps.network.lir import udp_lir_handler as ulhm


class UdpClient:
    def __init__(self, client_user_input: uim.ClientUserInput):
        self.client_user_input = client_user_input

    def start(self):
        if self.client_user_input.selected_network_layer == tm.NetworkLayer.IP:
            udp_ip_handler = uihm.UdpIpHandler(self.client_user_input)
            udp_ip_handler.start()
        elif self.client_user_input.selected_destination_name == tm.NetworkLayer.LIR:
            udp_lir_handler = ulhm.UdpLiRHandler(self.client_user_input)
            udp_lir_handler.start()
        else:
            raise Exception("unsupported network layer")
