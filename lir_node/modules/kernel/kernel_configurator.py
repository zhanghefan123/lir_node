import os
from multiprocessing.managers import Value

from modules.config.env_loader import env_loader
from modules.online.entities import sim_path as sppm
from modules.netlink import netlink_client as ncm
from modules.config import interface_loader as ilm
from modules.config import route_loader as rlm
from defined_types import types as tm
from modules.online.entities.sim_end_host import SimEndHost
from typing import List, Optional
from modules.config import env_loader as elm
from modules.online.entities import retrieved_feedback as rfm


class KernelConfigurator:
    def __init__(self):
        """
        初始化 LiR 配置加载器
        """
        self.netlink_client = ncm.NetlinkClient()
        self.lir_interfaces = ilm.load_interfaces()  # 这一步一定需要在之前完成
        self.lir_routes = rlm.load_routes()  # 加载路由条目, if is the array based routing table (only need to store source routes)
        ilm.load_lir_interface_ifindexes(self.lir_interfaces)  # 加载接口的 ifindex
        self.print_lir_routes_and_interfaces()

    def set_node_id(self):
        """
        进行节点 id 的设置, 这里使用的是图节点的 id 
        """
        self.netlink_client.send_netlink_data(f"{elm.env_loader.graph_node_id}", tm.NetlinkMessageType.CMD_SET_NODE_ID)

    def init_routing_table(self):
        """
        初始化路由表
        :return:
        """
        if elm.env_loader.routing_table_type == tm.RoutingTableType.ARRAY_BASED_ROUTING_TABLE_TYPE:  # 代表是 array based routing table type
            number_of_routes = len(self.lir_routes) + 2
            send_data = f"{tm.RoutingTableType.ARRAY_BASED_ROUTING_TABLE_TYPE},{number_of_routes}"
            self.netlink_client.send_netlink_data(send_data,
                                                  tm.NetlinkMessageType.CMD_INIT_ROUTING_TABLE)
            print("init array based routing table", flush=True)
        elif elm.env_loader.routing_table_type == tm.RoutingTableType.HASH_BASED_ROUTING_TABLE_TYPE:  # 代表是 hash based routing table type
            number_of_buckets = 2000
            send_data = f"{tm.RoutingTableType.HASH_BASED_ROUTING_TABLE_TYPE},{number_of_buckets}"
            self.netlink_client.send_netlink_data(send_data,
                                                  tm.NetlinkMessageType.CMD_INIT_ROUTING_TABLE)
            print("init hash based routing table", flush=True)
        else:
            print("do not need to initialize routing table")

    def init_forwarding_table(self):
        """
        初始化接口表
        """
        number_of_interfaces = len(self.lir_interfaces)
        send_data = f"{number_of_interfaces}"
        self.netlink_client.send_netlink_data(send_data, tm.NetlinkMessageType.CMD_INIT_INTERFACE_TABLE)

    def init_array_based_multipath_table(self):
        """
        初始化基于数组的 multipath_table
        :return:
        """
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
        if elm.env_loader.routing_table_type == tm.RoutingTableType.ARRAY_BASED_MULTIPATH_TABLE_TYPE:
            number_of_buckets = 100
            finalString = f"{env_loader.multipath_routing_type},{number_of_buckets},{env_loader.number_of_nodes},{number_of_relationships},{number_of_paths}"
            self.netlink_client.send_netlink_data(finalString, tm.NetlinkMessageType.CMD_INIT_MULTIPATH_TABLE)
            print("init array based multipath table", flush=True)
        else:
            print("not init array based multipath table", flush=True)

    def init_selir(self):
        """
        初始化 selir 的信息
        :return:
        """
        send_data = f"{elm.env_loader.pvf_effective_bits}"
        self.netlink_client.send_netlink_data(send_data, tm.NetlinkMessageType.CMD_INIT_SELIR)

    def init_bloom_filter(self):
        """
        初始化布隆过滤器
        """
        send_data = f"{elm.env_loader.bf_effective_bits},{elm.env_loader.hash_seed},{elm.env_loader.number_of_hash_functions}"
        self.netlink_client.send_netlink_data(send_data, tm.NetlinkMessageType.CMD_INIT_BLOOM_FILTER)

    def modify_bloom_filter(self, bf_effective_bits: int):
        send_data = f"{bf_effective_bits}"
        self.netlink_client.send_netlink_data(send_data, tm.NetlinkMessageType.CMD_MODIFY_BLOOM_FILTER)

    def insert_routing_table_entries(self):
        """
        进行路由条目的插入
        """
        for lir_route in self.lir_routes:
            send_data = f"{lir_route.source},{lir_route.destination},{lir_route.path_length}"
            for index in range(lir_route.path_length):
                send_data += f",{lir_route.link_identifiers[index]},{lir_route.node_ids[index]}"
            self.netlink_client.send_netlink_data(send_data, tm.NetlinkMessageType.CMD_INSERT_ROUTING_TABLE_ENTRY)

    def insert_interface_table_entries(self):
        """
        进行接口条目的插入
        """
        for index, lir_interface in enumerate(self.lir_interfaces):
            send_data = f"{index},{lir_interface.link_identifier},{lir_interface.ifindex},{lir_interface.source_node_id},{lir_interface.target_node_id},{lir_interface.peer_ip_address}"
            self.netlink_client.send_netlink_data(send_data, tm.NetlinkMessageType.CMD_INSERT_INTERFACE_TABLE_ENTRY)

    def set_lir_single_time_encoding_count(self):
        """
        设置 lir 单次插入的元素的次数
        :return:
        """
        self.netlink_client.send_netlink_data(f"{elm.env_loader.lir_single_time_encoding_count}",
                                              tm.NetlinkMessageType.CMD_SET_LIR_SINGLE_TIME_ENCODING_COUNT)

    def clear_segments_by_destination(self, destination: int):
        """
        根据目的节点 index 进行删除
        :return:
        """
        final_string = f"{destination}"
        self.netlink_client.send_netlink_data(final_string, tm.NetlinkMessageType.CMD_CLEAR_SEGMENT_LIST)

    def insert_source_multipath_segments(self):
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
                        self.netlink_client.send_netlink_data(line, tm.NetlinkMessageType.CMD_SOURCE_INSERT_SEGMENT)

    def insert_destination_routing_table_entries(self):
        """
        向目的节点进行paths的插入
        :return:
        """
        file_path = f"/configuration/{elm.env_loader.container_name}/route/dest_multipath.txt"
        if os.path.exists(file_path):
            with open(file_path) as f:
                # 读取每一行
                all_lines = f.readlines()
                for line in all_lines:
                    line = line.rstrip("\n")
                    if line == "":
                        continue
                    else:
                        self.netlink_client.send_netlink_data(line,
                                                              tm.NetlinkMessageType.CMD_INSERT_DEST_ROUTING_TABLE_ENTRY)

    def insert_source_multipath_output_link_identifiers(self):
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
                self.netlink_client.send_netlink_data(first_line,
                                                      tm.NetlinkMessageType.CMD_INSERT_OUTPUT_LINK_IDENTIFIERS)

    def insert_relationship_between_target_node_id_and_paths(self):
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
                        self.netlink_client.send_netlink_data(line,
                                                              tm.NetlinkMessageType.CMD_INSERT_RELATIONSHIP_BETWEEN_NEXT_NODE_ID_AND_PATHS)

    def insert_intermediate_multipath_segments(self):
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
                        self.netlink_client.send_netlink_data(line,
                                                              tm.NetlinkMessageType.CMD_INTERMEDIATE_INSERT_SEGMENT)

    def insert_intermediate_multipath_output_link_identifiers(self):
        """
        设置中间节点多路径的出接口
        :return:
        """
        file_path = f"/configuration/{elm.env_loader.container_name}/intermediate_multipath_output_link_identifiers.txt"
        if os.path.exists(file_path):
            with open(file_path) as f:
                # 读取每一行
                all_lines = f.readlines()
                first_line = all_lines[0]
                first_line = first_line.rstrip("\n")
                self.netlink_client.send_netlink_data(first_line,
                                                      tm.NetlinkMessageType.CMD_INSERT_OUTPUT_LINK_IDENTIFIERS)

    def set_sec_path_mab_route_for_fixed_batch(self, current_epoch_selected_path: sppm.SimPath, batch_size: int,
                                               counts: List[int]) -> str:
        """
        获取用户空间下发的路径 (对于固定 batch 大小的方式)
        :return:
        """
        source_end_host = current_epoch_selected_path.node_list[0].actual_node
        destination_end_host = current_epoch_selected_path.node_list[-1].actual_node
        if isinstance(source_end_host, SimEndHost):
            source_id = source_end_host.index
        else:
            raise ValueError("source not end host")
        if isinstance(destination_end_host, SimEndHost):
            destination_id = destination_end_host.index
        else:
            raise ValueError("destinatio not end host")
        link_identifiers = len(current_epoch_selected_path.pv_routers) + 1
        final_string = f"{source_id},{destination_id},{link_identifiers}"
        # append link identifiers
        for interface in current_epoch_selected_path.interfaces:
            final_string += f",{interface.link_identifier}"
        # append number of node ids
        final_string += f",{len(current_epoch_selected_path.pv_routers) + 1}"
        # append node ids
        for node in current_epoch_selected_path.pv_routers:
            final_string += f",{node.index}"
        final_string += f",{destination_id}"
        # append final batch size (batch size 的作用是进行内核的 sequence 的生成)
        final_string += f",{batch_size}"
        for count in counts:
            final_string += f",{count}"
        self.netlink_client.send_netlink_data(final_string, tm.NetlinkMessageType.CMD_SET_SEC_PATH_MAB_ROUTE)
        # 将生成的 netlink string 进行返回
        return final_string

    def set_sec_path_mab_route_for_dynamic_batch(self, current_epoch_selected_path: sppm.SimPath, mini_batch_size: int):
        """
        获取用户空间下发的路径 (对于动态 batch 大小的方式)
        :return:
        """
        source_end_host = current_epoch_selected_path.node_list[0].actual_node
        destination_end_host = current_epoch_selected_path.node_list[-1].actual_node
        if isinstance(source_end_host, SimEndHost):
            source_id = source_end_host.index
        else:
            raise ValueError("source not end host")
        if isinstance(destination_end_host, SimEndHost):
            destination_id = destination_end_host.index
        else:
            raise ValueError("destinatio not end host")
        link_identifiers = len(current_epoch_selected_path.pv_routers) + 1
        final_string = f"{source_id},{destination_id},{link_identifiers}"
        # append link identifiers
        for interface in current_epoch_selected_path.interfaces:
            final_string += f",{interface.link_identifier}"
        # append number of node ids
        final_string += f",{len(current_epoch_selected_path.pv_routers) + 1}"
        # append node ids
        for node in current_epoch_selected_path.pv_routers:
            final_string += f",{node.index}"
        final_string += f",{destination_id}"
        # append batch size
        final_string += f",{mini_batch_size}"
        self.netlink_client.send_netlink_data(final_string, tm.NetlinkMessageType.CMD_SET_SEC_PATH_MAB_ROUTE)
        # 将生成的 netlink string 进行返回
        return final_string

    def reset_sec_path_mab_route_for_fixed_batch(self, batch_size: int, counts: List[int]):
        final_string = f"{batch_size}"
        for count in counts:
            final_string += f",{count}"
        self.netlink_client.send_netlink_data(final_string, tm.NetlinkMessageType.CMD_RESET_SEC_PATH_MAB_ROUTE)

    def reset_sec_path_mab_route_for_dynamic_batch(self):
        self.netlink_client.send_netlink_data("", tm.NetlinkMessageType.CMD_RESET_SEC_PATH_MAB_ROUTE)

    def set_router_type(self):
        final_string = f"{elm.env_loader.router_type}"
        self.netlink_client.send_netlink_data(final_string,
                                              tm.NetlinkMessageType.CMD_SET_ROUTER_TYPE)

    def set_sec_path_mab_type(self):
        final_string = f"{elm.env_loader.sec_path_mab_type}"
        self.netlink_client.send_netlink_data(final_string,
                                              tm.NetlinkMessageType.CMD_SET_SEC_PATH_MAB_TYPE)

    def set_malicious_params_from_env(self):
        final_string = (
            f"{elm.env_loader.malicious_params.corrupt_ratio_start},{elm.env_loader.malicious_params.corrupt_ratio_end},"
            f"{elm.env_loader.malicious_params.corrupt_special_packet_ratio_start},{elm.env_loader.malicious_params.corrupt_special_packet_ratio_end}")

        self.netlink_client.send_netlink_data(final_string, tm.NetlinkMessageType.CMD_SET_MALICIOUS_PARAMS)

    def set_scheduled_malicious_params(self, employed_epoch: int, corrupt_ratio_start: int, corrupt_ratio_end: int,
                                       corrupt_special_packet_ratio_start: int, corrupt_special_packet_ratio_end: int):
        final_string = (f"{employed_epoch},{corrupt_ratio_start},{corrupt_ratio_end},"
                        f"{corrupt_special_packet_ratio_start},{corrupt_special_packet_ratio_end}")
        self.netlink_client.send_netlink_data(final_string, tm.NetlinkMessageType.CMD_SET_SCHDULED_MALICIOUS_PARAMS)

    def retrieve_kernel_information_for_fixed_batch(self) -> List[rfm.RetrievedFeedback]:
        retrieved_feedbacks = []
        received_string = self.netlink_client.send_netlink_data("", tm.NetlinkMessageType.CMD_RETRIEVE_KERNEL_INFORMATION)
        if received_string.startswith("Err:"):
            return retrieved_feedbacks
        else:
            feedbacks_in_str = list(received_string.split(","))
            # print(f"feedbacks in str = {feedbacks_in_str}", flush=True)
            number_of_feedbacks = int(feedbacks_in_str.pop(0))
            feedbacks_in_str.pop(len(feedbacks_in_str)-1)

            for i in range(number_of_feedbacks):
                retrieved_ack_counts = []
                expected_ack_counts = []
                index = 0
                number_of_sample_nodes = 0
                epoch_id = -1
                sending_time_elapsed = -1
                while True:
                    if index == 0:
                        epoch_id = int(feedbacks_in_str[index])
                    elif index == 1:
                        sending_time_elapsed = int(feedbacks_in_str[index])
                    elif index == 2:
                        number_of_sample_nodes = int(feedbacks_in_str[index])
                    else:
                        if index % 2 == 1:
                            retrieved_ack_counts.append(int(feedbacks_in_str[index]))
                        else:
                            expected_ack_counts.append(int(feedbacks_in_str[index]))
                    if index == (2 + number_of_sample_nodes * 2):
                        retrieved_feedbacks.append(rfm.RetrievedFeedback(epoch_id=epoch_id,
                                                                         sending_time_elapsed=sending_time_elapsed,
                                                                         number_of_sample_nodes=number_of_sample_nodes,
                                                                         retrieved_ack_counts=retrieved_ack_counts,
                                                                         expected_ack_counts=expected_ack_counts))
                        break
                    index += 1
                feedbacks_in_str = feedbacks_in_str[3+number_of_sample_nodes*2:]
            # 把 feedback 全部打印出来
            return retrieved_feedbacks

    # def original_retrieve_kernel_information_for_fixed_batch(self) -> (int, int, List[int], List[int], bool):
    #     """
    #     向源节点进行 counters 和 acks 的返回
    #     :return:
    #     """
    #     final_string = f""
    #     received_string = self.netlink_client.send_netlink_data(final_string,
    #                                                             tm.NetlinkMessageType.CMD_RETRIEVE_KERNEL_INFORMATION)
    #     received_string = str(received_string)
    #     if received_string.startswith("Err:"):
    #         return -1, 0, [], [], False
    #     else:
    #         epoch_id_and_acks_in_str = received_string.split(",")
    #         received_acks = []
    #         expected_acks = []
    #         epoch_id = -1
    #         sending_time_elapsed = 0
    #         for index in range(len(epoch_id_and_acks_in_str)):
    #             if index == 0:
    #                 epoch_id = int(epoch_id_and_acks_in_str[index])
    #             elif index == 1:
    #                 sending_time_elapsed = int(epoch_id_and_acks_in_str[index])
    #             else:
    #                 if index % 2 == 0:
    #                     received_acks.append(int(epoch_id_and_acks_in_str[index]))
    #                 else:
    #                     expected_acks.append(int(epoch_id_and_acks_in_str[index]))
    #         # print(f"retrieved epoch: {epoch_id} received_acks: {received_acks} expected_acks: {expected_acks}", flush=True)
    #         return epoch_id, sending_time_elapsed, received_acks, expected_acks, True
        
    def retrieve_kernel_information_for_dynamic_batch(self) -> (int, int, int, int, int, List[int], List[int], bool):
        final_string = f""
        received_string = self.netlink_client.send_netlink_data(final_string,
                                                                tm.NetlinkMessageType.CMD_RETRIEVE_KERNEL_INFORMATION)
        received_string = str(received_string)
        if received_string.startswith("Err:"):
            return -1, 0, 0, 0, 0, [], [], False
        else:
            # print("received string: ", received_string, flush=True)
            epoch_id_and_acks_in_str = received_string.split(",")
            received_acks = []
            expected_acks = []
            epoch_id = -1
            collect_enough_ack_time_elapsed = 0
            reach_timeout_time_elapsed = 0
            number_of_sampling_packets = 0
            number_of_unsamping_packets = 0
            for index in range(len(epoch_id_and_acks_in_str)):
                if index == 0:
                    epoch_id = int(epoch_id_and_acks_in_str[index])
                elif index == 1:
                    collect_enough_ack_time_elapsed = int(epoch_id_and_acks_in_str[index])
                elif index == 2:
                    reach_timeout_time_elapsed = int(epoch_id_and_acks_in_str[index])
                elif index == 3:
                    number_of_sampling_packets = int(epoch_id_and_acks_in_str[index])
                elif index == 4:
                    number_of_unsamping_packets = int(epoch_id_and_acks_in_str[index])
                else:
                    if index % 2 == 1:
                        received_acks.append(int(epoch_id_and_acks_in_str[index]))
                    else:
                        expected_acks.append(int(epoch_id_and_acks_in_str[index]))
            # print(f"retrieved epoch: {epoch_id} received_acks: {received_acks} expected_acks: {expected_acks}", flush=True)
            return (epoch_id, collect_enough_ack_time_elapsed, reach_timeout_time_elapsed,
                    number_of_sampling_packets, number_of_unsamping_packets,
                    received_acks, expected_acks, True)

    def set_min_ack_for_rtt_estimation(self, value):
        final_string = f"{value}"
        self.netlink_client.send_netlink_data(final_string, tm.NetlinkMessageType.CMD_SET_MIN_ACK_FOR_RTT_ESTIMATION)

    def print_lir_routes_and_interfaces(self):
        """
        打印 LiR 的路由条目和接口条目
        """
        print("----------------- ALL ROUTES -----------------")
        for lir_route in self.lir_routes:
            print(lir_route, flush=True)
        print("----------------- ALL ROUTES -----------------")
        print("----------------- ALL INTERFACES -----------------")
        for lir_interface in self.lir_interfaces:
            print(lir_interface, flush=True)
        print("----------------- ALL INTERFACES -----------------")

    def start(self):
        """
        启动
        """
        self.set_node_id()
        self.set_router_type()
        self.set_sec_path_mab_type()
        self.init_forwarding_table()
        self.init_routing_table()
        self.init_array_based_multipath_table()
        self.init_selir()
        self.init_bloom_filter()
        self.insert_interface_table_entries()
        self.insert_routing_table_entries()
        self.insert_destination_routing_table_entries()
        self.set_lir_single_time_encoding_count()
        self.set_malicious_params_from_env()
        # ------ 进行源的 multipath_segments / output_link_identifiers 的插入 ------
        self.insert_source_multipath_segments()
        self.insert_source_multipath_output_link_identifiers()
        # ------ 进行源的 multipath_segments / output_link_identifiers 的插入 ------
        # -----  进行中间节点的 multipath_segments / output_link_identifiers 的插入 -----
        self.insert_relationship_between_target_node_id_and_paths()
        self.insert_intermediate_multipath_segments()
        self.insert_intermediate_multipath_output_link_identifiers()
        # -----  进行中间节点的 multipath_segments / output_link_identifiers 的插入 -----


kernel_config_loader: Optional[KernelConfigurator] = None


def load_kernel_configuration():
    global kernel_config_loader
    kernel_config_loader = KernelConfigurator()
    kernel_config_loader.start()
