from modules.netlink import netlink_client as ncm
from modules.lir import lir_route_loader as lrlm
from modules.lir import lir_interface_loader as lilm
from modules.config import env_loader as elm


class LirConfigLoader:
    def __init__(self):
        """
        初始化 LiR 配置加载器
        """
        self.netlink_client = ncm.NetlinkClient()
        self.lir_routes = lrlm.load_lir_routes()
        self.lir_interfaces = lilm.load_lir_interfaces()

    def init_routing_and_forwarding_table(self):
        """
        初始化路由和接口表
        """
        # 总共 4 个节点, 他们的编号分别为 (1,2,3,4), 一个节点 3 条路由, 那么需要创建 5 个条目
        number_of_routes = len(self.lir_routes) + 2
        number_of_interfaces = len(self.lir_interfaces)
        send_data = f"{number_of_routes},{number_of_interfaces}"
        self.netlink_client.send_netlink_data(send_data, ncm.NetlinkMessageType.CMD_INIT_ROUTING_AND_FORWARDING_TABLE)

    def init_bloom_filter(self):
        """
        初始化布隆过滤器
        """
        send_data = f"{elm.env_loader.effective_bytes},{elm.env_loader.hash_seed},{elm.env_loader.number_of_hash_functions}"
        self.netlink_client.send_netlink_data(send_data, ncm.NetlinkMessageType.CMD_INIT_BLOOM_FILTER)

    def print_lir_routes_and_interfaces(self):
        """
        打印 LiR 的路由条目和接口条目
        """
        for lir_route in self.lir_routes:
            print(lir_route, flush=True)
        for lir_interface in self.lir_interfaces:
            print(lir_interface, flush=True)

    def start(self):
        """
        启动
        """
        self.init_routing_and_forwarding_table()
        self.init_bloom_filter()
        self.print_lir_routes_and_interfaces()


def load_lir_configuration():
    lir_config_loader = LirConfigLoader()
    lir_config_loader.start()
