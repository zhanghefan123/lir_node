import os
from defined_types.types import PathValidationTransmissionType
from modules.config import env_loader as elm
from modules.kernel import kernel_configurator as kcm
from defined_types import types as tm
from typing import List


class Route:
    def __init__(self, source: int, destination: int, path_length: int, link_identifiers: List, node_ids: List):
        """
        初始化 LiRRoute
        :param source: 源头
        :param destination: 目的
        :param path_length: 路径长度
        :param link_identifiers: 链路表示序列s
        :param node_ids: 节点标识序列
        """
        self.source = source
        self.destination = destination
        self.path_length = path_length
        self.link_identifiers = link_identifiers
        self.node_ids = node_ids

    def __str__(self):
        return (f"source: {self.source} "
                f"destination: {self.destination} "
                f"path_length: {self.path_length} "
                f"link_identifiers: {self.link_identifiers} "
                f"node_ids: {self.node_ids}")


def load_routes(transmission_type: int):
    """
    加载路由条目
    :return: 路由条目系列
    """
    """
    1,4,3,1,2,3,3,5,4
    1,3,2,1,2,3,3
    1,2,1,1,2
    """
    # setting routes_file_path
    routes_file_path = "unknown"
    if transmission_type == PathValidationTransmissionType.UNICAST_TRANSMISSION_TYPE:
        routes_file_path = f"/configuration/{elm.env_loader.container_name}/route/lir.txt"
    elif transmission_type == PathValidationTransmissionType.MULTIPATH_TRANSMISSION_TYPE:
        routes_file_path = f"/configuration/{elm.env_loader.container_name}/route/multipath.txt"
    elif transmission_type == PathValidationTransmissionType.MULTICAST_TRANSMISSION_TYPE:
        routes_file_path = f"/configuration/{elm.env_loader.container_name}/route/all_lir.txt"
    elif transmission_type == PathValidationTransmissionType.MAB_TRANSMISSION_TYPE:
        print("mab does not need any route", flush=True)
    else:
        raise ValueError(f"unsupported transmission type {transmission_type}")

    # 路由条目
    routes = []
    # 打开文件
    print(f"routes_file_path: {routes_file_path}")
    if os.path.exists(routes_file_path):
        with open(routes_file_path) as f:
            # 读取每一行
            all_lines = f.readlines()
            for line in all_lines:
                line = line.rstrip("\n")
                if line == "":
                    continue
                link_identifiers = []
                node_ids = []
                result = line.split(",")
                source = int(result[0])  # 1. 获取源
                destination = int(result[1])  # 2. 获取目的
                path_length = int(result[2])  # 3. 获取路径长度
                for index in range(3, 3 + path_length * 2):
                    if index % 2 == 1:
                        link_identifier = int(result[index])  # 4. 获取链路标识
                        link_identifiers.append(link_identifier)
                    else:
                        node_id = int(result[index])  # 5. 获取节点 id
                        node_ids.append(node_id)
                route = Route(source, destination, path_length, link_identifiers, node_ids)
                routes.append(route)
    kcm.kernel_config_loader.lir_routes = routes


def init_routing_table():
    """
    初始化路由表
    :return:
    """
    if elm.env_loader.routing_table_type == tm.RoutingTableType.ARRAY_BASED_ROUTING_TABLE_TYPE:  # 代表是 array based routing table type
        number_of_routes = len(kcm.kernel_config_loader.lir_routes) + 2
        send_data = f"{tm.RoutingTableType.ARRAY_BASED_ROUTING_TABLE_TYPE},{number_of_routes}"
        kcm.kernel_config_loader.netlink_client.send_netlink_data_and_retrieve_string(send_data,
                                                                                      tm.NetlinkMessageType.CMD_INIT_ROUTING_TABLE)
        print("init array based routing table", flush=True)
    elif elm.env_loader.routing_table_type == tm.RoutingTableType.HASH_BASED_ROUTING_TABLE_TYPE:  # 代表是 hash based routing table type
        number_of_buckets = 2000
        send_data = f"{tm.RoutingTableType.HASH_BASED_ROUTING_TABLE_TYPE},{number_of_buckets}"
        kcm.kernel_config_loader.netlink_client.send_netlink_data_and_retrieve_string(send_data,
                                                                                      tm.NetlinkMessageType.CMD_INIT_ROUTING_TABLE)
        print("init hash based routing table", flush=True)
    else:
        print("do not need to initialize routing table")


def insert_routing_table_entries():
    """
    进行路由条目的插入
    """
    for lir_route in kcm.kernel_config_loader.lir_routes:
        send_data = f"{lir_route.source},{lir_route.destination},{lir_route.path_length}"
        for index in range(lir_route.path_length):
            send_data += f",{lir_route.link_identifiers[index]},{lir_route.node_ids[index]}"
        kcm.kernel_config_loader.netlink_client.send_netlink_data_and_retrieve_string(send_data,
                                                                                      tm.NetlinkMessageType.CMD_INSERT_ROUTING_TABLE_ENTRY)


def print_lir_routes():
    """
    打印 LiR 的路由条目和接口条目
    """
    print("----------------- ALL ROUTES -----------------")
    for lir_route in kcm.kernel_config_loader.lir_routes:
        print(lir_route, flush=True)
    print("----------------- ALL ROUTES -----------------")
