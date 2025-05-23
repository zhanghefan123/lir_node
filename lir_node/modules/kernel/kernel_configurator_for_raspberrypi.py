from modules.netlink import netlink_client as ncm
from modules.config import env_loader as elm
from modules.config import interface_loader as ilm
from modules.config import route_loader as rlm
from defined_types import types as tm


class KernelConfiguratorForRsapberrypi:
    def __init__(self):
        """
        初始化 LiR 配置加载器
        """
        lir_interface_file_path = "/home/zeusnet/Projects/configuration/interface/interface.txt"
        lir_route_file_path = "/home/zeusnet/Projects/configuration/route/lir.txt"
        lir_all_route_file_path = "/home/zeusnet/Projects/configuration/route/all_lir.txt"
        self.netlink_client = ncm.NetlinkClient()
        self.lir_interfaces = ilm.load_interfaces(lir_interface_file_path=lir_interface_file_path)  # 这一步一定需要在之前完成
        self.lir_routes = rlm.load_routes(lir_route_file_path=lir_route_file_path, lir_all_route_file_path=lir_all_route_file_path)  # 加载路由条目, if is the array based routing table (only need to store source routes)
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
            number_of_buckets = 2000
            number_of_interfaces = len(self.lir_interfaces)
            send_data = f"{tm.RoutingTableType.HASH_BASED_ROUTING_TABLE_TYPE},{number_of_buckets},{number_of_interfaces}"
            self.netlink_client.send_netlink_data(send_data,
                                                  ncm.NetlinkMessageType.CMD_INIT_ROUTING_AND_FORWARDING_TABLE)
        else:
            raise Exception("unknown routing table type")

    def init_selir(self):
        """
        初始化 selir 的信息
        :return:
        """
        send_data = f"{elm.env_loader.pvf_effective_bits}"
        self.netlink_client.send_netlink_data(send_data, ncm.NetlinkMessageType.CMD_INIT_SELIR)

    def init_bloom_filter(self):
        """
        初始化布隆过滤器
        """
        send_data = f"{elm.env_loader.bf_effective_bits},{elm.env_loader.hash_seed},{elm.env_loader.number_of_hash_functions}"
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
            send_data = f"{index},{lir_interface.link_identifier},{lir_interface.ifindex},{lir_interface.peer_ip_address}"
            self.netlink_client.send_netlink_data(send_data, ncm.NetlinkMessageType.CMD_INSERT_INTERFACE_TABLE_ENTRY)

    def set_lir_single_time_encoding_count(self):
        """
        设置 lir 单次插入的元素的次数
        :return:
        """
        self.netlink_client.send_netlink_data(f"{elm.env_loader.lir_single_time_encoding_count}", ncm.NetlinkMessageType.CMD_SET_LIR_SINGLE_TIME_ENCODING_COUNT)

    def print_lir_routes_and_interfaces(self):
        """
        打印 LiR 的路由条目和接口条目
        """
        print("-----------------all-lir-routes-----------------", flush=True)
        for lir_route in self.lir_routes:
            print(lir_route, flush=True)
        print("-----------------all-lir-routes-----------------", flush=True)
        print("---------------all-lir-interfaces---------------", flush=True)
        for lir_interface in self.lir_interfaces:
            print(lir_interface, flush=True)
        print("---------------all-lir-interfaces---------------", flush=True)

    def start(self):
        """
        启动
        """
        pass  # 先不进行任何操作, 看是否可行
        self.set_node_id()
        self.init_routing_and_forwarding_table()
        self.init_selir()
        self.init_bloom_filter()
        self.insert_interface_table_entries()
        self.insert_routing_table_entries()
        self.set_lir_single_time_encoding_count()


