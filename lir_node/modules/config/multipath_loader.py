import os
from defined_types import types as tm
from modules.config import env_loader as elm
from modules.kernel import kernel_configurator as kcm


# 每个节点都需要执行的
def init_array_based_multipath_table():
    # 进行文件的读取
    number_of_paths_file = f"/configuration/{elm.env_loader.container_name}/num_of_paths.txt"
    number_of_paths = 0
    if os.path.exists(number_of_paths_file):
        with open(number_of_paths_file) as f:
            number_of_paths = int(f.read())

    file_path = f"/configuration/{elm.env_loader.container_name}/relationship.txt"
    number_of_relationships = 0
    if os.path.exists(file_path):
        with open(file_path) as f:
            number_of_relationships = len(f.readlines())
    else:
        pass

    # 进行加载
    if elm.env_loader.routing_table_type == tm.RoutingTableType.ARRAY_BASED_MULTIPATH_TABLE_TYPE:
        number_of_buckets = 100
        finalString = f"{number_of_buckets},{number_of_relationships},{number_of_paths}"
        kcm.kernel_config_loader.netlink_client.send_netlink_data_and_retrieve_string(finalString,
                                                                                      tm.NetlinkMessageType.CMD_INIT_MULTIPATH_TABLE)
        print("init array based multipath table", flush=True)
    else:
        print("not init array based multipath table", flush=True)


# 只有 fast selir 源节点需要执行
def insert_source_multipath_output_link_identifiers():
    """
    设置多路径源的出接口
    :return:
    """
    file_path = f"/configuration/{elm.env_loader.container_name}/multipath_output_link_identifiers.txt"
    if os.path.exists(file_path):
        with open(file_path) as f:
            # 读取每一行
            all_lines = f.readlines()
            first_line = all_lines[0]
            first_line = first_line.rstrip("\n")
            kcm.kernel_config_loader.netlink_client.send_netlink_data_and_retrieve_string(first_line,
                                                                                          tm.NetlinkMessageType.CMD_INSERT_OUTPUT_LINK_IDENTIFIERS)


# 只有 fast_selir 中间节点需要执行
def insert_relationship_between_target_node_id_and_paths():
    file_path = f"/configuration/{elm.env_loader.container_name}/relationship.txt"
    if os.path.exists(file_path):
        with open(file_path) as f:
            # 读取每一行
            all_lines = f.readlines()
            for line in all_lines:
                line = line.rstrip("\n")
                if line == "":
                    continue
                else:
                    kcm.kernel_config_loader.netlink_client.send_netlink_data_and_retrieve_string(line,
                                                                                                  tm.NetlinkMessageType.CMD_INSERT_RELATIONSHIP_BETWEEN_NEXT_NODE_ID_AND_PATHS)


# 只有 fast selir multipath 源节点和中间节点都需要执行
def insert_intermediate_multipath_output_link_identifiers():
    """
    设置中间节点多路径的出接口
    :return:
    """
    file_path = f"/configuration/{elm.env_loader.container_name}/multipath_output_link_identifiers.txt"
    if os.path.exists(file_path):
        with open(file_path) as f:
            # 读取每一行
            all_lines = f.readlines()
            first_line = all_lines[0]
            first_line = first_line.rstrip("\n")
            kcm.kernel_config_loader.netlink_client.send_netlink_data_and_retrieve_string(first_line,
                                                                                          tm.NetlinkMessageType.CMD_INSERT_OUTPUT_LINK_IDENTIFIERS)


# 只有 atlas 中间节点需要执行
def insert_intermediate_multipath_segments():
    """
    进行中间节点管理的 segments 的插入
    :return:
    """
    file_path = f"/configuration/{elm.env_loader.container_name}/intermediate_multipath_segments.txt"
    if os.path.exists(file_path):
        with open(file_path) as f:
            # 读取每一行
            all_lines = f.readlines()
            for line in all_lines:
                line = line.rstrip("\n")
                if line == "":
                    continue
                else:
                    kcm.kernel_config_loader.netlink_client.send_netlink_data_and_retrieve_string(line,
                                                                                                  tm.NetlinkMessageType.CMD_INTERMEDIATE_INSERT_SEGMENT)


# 只有 atlas 源节点需要执行
def insert_source_multipath_segments():
    """
    进行所有的 segments 的插入
    :return:
    """
    file_path = f"/configuration/{elm.env_loader.container_name}/multipath_segments.txt"
    if os.path.exists(file_path):
        with open(file_path) as f:
            # 读取每一行
            all_lines = f.readlines()
            for line in all_lines:
                line = line.rstrip("\n")
                if line == "":
                    continue
                else:
                    kcm.kernel_config_loader.netlink_client.send_netlink_data_and_retrieve_string(line,
                                                                                                  tm.NetlinkMessageType.CMD_SOURCE_INSERT_SEGMENT)
