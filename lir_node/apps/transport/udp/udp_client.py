from apps.user import client_detailed_info as cdim
from defined_types import types as tm
from apps.network.ip import udp_ip_client as uihm
from apps.network.lir import udp_other_client as ulhm


def start_client(client_detailed_info: cdim.ClientDetailedInfo):
    # 如果网络层选择为 ip 或者 srv6
    if client_detailed_info.selected_network_layer == tm.NetworkLayer.IP or client_detailed_info.selected_network_layer == tm.NetworkLayer.SRV6:
        udp_ip_handler = uihm.UdpIpClient(client_detailed_info)
        udp_ip_handler.start()
    # 如果网络层选择为 lir
    else:
        udp_lir_handler = ulhm.UdpOtherClient(client_detailed_info)
        udp_lir_handler.start()
