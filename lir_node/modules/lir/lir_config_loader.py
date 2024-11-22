from modules.netlink import netlink_client as ncm
from modules.lir import lir_route_loader as lrlm


class LirConfigLoader:
    def __init__(self):
        self.netlink = ncm.NetlinkClient()
        self.lir_routes = lrlm.load_lir_routes()

    def init_routing_and_forwarding_table(self):
        # 总共 4 个节点 (1,2,3,4), 一个节点 3 条路由, 那么需要创建 5 个条目
        number_of_routes = len(self.lir_routes) + 2

    def init_bloom_filter(self):
        pass

    def start(self):
        self.init_routing_and_forwarding_table()
        self.init_bloom_filter()
