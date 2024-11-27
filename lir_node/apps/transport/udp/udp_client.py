from apps.user import user_input as uim
from defined_types import types as tm
from apps.network.ip import udp_ip_handler as uihm


class UdpClient:
    def __init__(self, user_input: uim.UserInput):
        self.user_input = user_input

    def start(self):
        if self.user_input.selected_network_layer == tm.NetworkLayer.IP:
            udp_ip_handler = uihm.UdpIpHandler(self.user_input)
            udp_ip_handler.start()
        elif self.user_input.selected_destination_name == tm.NetworkLayer.LIR:
            pass
