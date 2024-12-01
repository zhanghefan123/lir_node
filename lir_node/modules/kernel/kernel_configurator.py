from modules.netlink import netlink_client as ncm
from modules.config import env_loader as elm
from modules.config import interface_loader as ilm
from modules.config import route_loader as rlm
from defined_types import types as tm


class KernelConfigurator:
    def __init__(self):
        """
        初始化 LiR 配置加载器
        """
        self.netlink_client = ncm.NetlinkClient()
        self.lir_interfaces = ilm.load_interfaces()  # 这一步一定需要在之前完成
        self.lir_routes = rlm.load_routes()  # 加载路由条目
        ilm.load_lir_interface_ifindexes(self.lir_interfaces)  # 加载接口的 ifindex
        self.print_lir_routes_and_interfaces()

    def set_node_id(self):
        """
        进行节点 id 的设置, 这里使用的是图节点的 id 
        """
        self.netlink_client.send_netlink_data(f"{elm.env_loader.graph_node_id}", ncm.NetlinkMessageType.CMD_SET_NODE_ID)

    def init_routing_and_forwarding_table(self):
        """
        初始化路由和接口表
        """
        # 总共 4 个节点, 他们的编号分别为 (1,2,3,4), 一个节点 3 条路由, 那么需要创建 5 个条目
        if elm.env_loader.routing_table_type == tm.RoutingTableType.ARRAY_BASED_ROUTING_TABLE_TYPE:  # 代表是 array based routing table type
            number_of_routes = len(self.lir_routes) + 2
            number_of_interfaces = len(self.lir_interfaces)
            send_data = f"{tm.RoutingTableType.ARRAY_BASED_ROUTING_TABLE_TYPE},{number_of_routes},{number_of_interfaces}"
            self.netlink_client.send_netlink_data(send_data,
                                                  ncm.NetlinkMessageType.CMD_INIT_ROUTING_AND_FORWARDING_TABLE)
        elif elm.env_loader.routing_table_type == tm.RoutingTableType.HASH_BASED_ROUTING_TABLE_TYPE:  # 代表是 hash based routing table type
            number_of_buckets = 100
            number_of_interfaces = len(self.lir_interfaces)
            send_data = f"{tm.RoutingTableType.HASH_BASED_ROUTING_TABLE_TYPE},{number_of_buckets},{number_of_interfaces}"
            self.netlink_client.send_netlink_data(send_data,
                                                  ncm.NetlinkMessageType.CMD_INIT_ROUTING_AND_FORWARDING_TABLE)
        else:
            raise Exception("unknown routing table type")

    def init_bloom_filter(self):
        """
        初始化布隆过滤器
        """
        send_data = f"{elm.env_loader.effective_bits},{elm.env_loader.hash_seed},{elm.env_loader.number_of_hash_functions}"
        self.netlink_client.send_netlink_data(send_data, ncm.NetlinkMessageType.CMD_INIT_BLOOM_FILTER)

    def insert_routing_table_entries(self):
        """
        进行路由条目的插入
        """
        for lir_route in self.lir_routes:
            send_data = f"{lir_route.source},{lir_route.destination},{lir_route.path_length}"
            for index in range(lir_route.path_length):
                send_data += f",{lir_route.link_identifiers[index]},{lir_route.node_ids[index]}"
            self.netlink_client.send_netlink_data(send_data, ncm.NetlinkMessageType.CMD_INSERT_ROUTING_TABLE_ENTRY)

    def insert_interface_table_entries(self):
        """
        进行接口条目的插入
        """
        for index, lir_interface in enumerate(self.lir_interfaces):
            send_data = f"{index},{lir_interface.link_identifier},{lir_interface.ifindex}"
            self.netlink_client.send_netlink_data(send_data, ncm.NetlinkMessageType.CMD_INSERT_INTERFACE_TABLE_ENTRY)

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
        self.set_node_id()
        self.init_routing_and_forwarding_table()
        self.init_bloom_filter()
        self.insert_interface_table_entries()
        self.insert_routing_table_entries()


def load_lir_configuration():
    lir_config_loader = KernelConfigurator()
    lir_config_loader.start()
