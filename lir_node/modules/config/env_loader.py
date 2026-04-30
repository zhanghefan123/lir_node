import os
from multiprocessing.managers import Value
from typing import Optional
from defined_types import types as tm


class MaliciousParams:
    def __init__(self):
        self.corrupt_ratio_start: int = 0
        self.corrupt_ratio_end: int = 0
        self.corrupt_special_packet_ratio_start: int = 0
        self.corrupt_special_packet_ratio_end: int = 0


class EnvLoader:
    def __init__(self):
        self.listen_port = None
        self.enable_frr = None
        self.container_name = None
        self.bf_effective_bits = None
        self.pvf_effective_bits = None
        self.hash_seed = None
        self.number_of_hash_functions = None
        self.routing_table_type = None
        self.transmission_type = None
        self.node_id = None
        self.graph_node_id = None
        self.lir_single_time_encoding_count = None
        self.enable_srv6 = None  # 是否开启 SRv6 in str format
        self.number_of_nodes = None  # 总共的节点数量是多少
        self.multipath_routing_type = None  # 多路径路由类型
        self.malicious_params: Optional[MaliciousParams] = None  # 恶意参数
        self.router_type: int = -1  # 路由器的类型
        self.sec_path_mab_type: int = -1  # 选择的 sec_path_mab 策略的类型

        self.load_from_env()
        if None in [self.listen_port, self.enable_frr, self.container_name, self.bf_effective_bits,
                    self.pvf_effective_bits, self.hash_seed, self.number_of_hash_functions, self.routing_table_type,
                    self.transmission_type,
                    self.node_id, self.graph_node_id, self.lir_single_time_encoding_count, self.enable_srv6]:
            # 如果全部存在值的话
            self.load_from_file()
        else:
            pass

    def load_from_env(self):
        try:
            self.listen_port = os.getenv("LISTEN_PORT")
            self.enable_frr = os.getenv("ENABLE_FRR")
            self.container_name = os.getenv("CONTAINER_NAME")
            self.bf_effective_bits = int(os.getenv("BF_EFFECTIVE_BITS"))
            self.pvf_effective_bits = int(os.getenv("PVF_EFFECTIVE_BITS"))
            self.hash_seed = int(os.getenv("HASH_SEED"))
            self.number_of_hash_functions = int(os.getenv("NUMBER_OF_HASH_FUNCTIONS"))
            self.routing_table_type = int(os.getenv("ROUTING_TABLE_TYPE"))
            self.transmission_type = int(os.getenv("TRANSMISSION_TYPE"))
            self.node_id = int(os.getenv("NODE_ID"))
            self.graph_node_id = int(os.getenv("GRAPH_NODE_ID"))
            self.lir_single_time_encoding_count = int(os.getenv("LIR_SINGLE_TIME_ENCODING_COUNT"))
            self.enable_srv6 = os.getenv("ENABLE_SRV6")  # 是否开启 SRv6 in str format
            self.number_of_nodes = int(os.getenv("NUMBER_OF_NODES"))  # 节点的数量
            self.multipath_routing_type = int(os.getenv("MULTIPATH_ROUTING_TYPE"))  # 多路径路由类型

            # 初始化恶意参数
            self.malicious_params = MaliciousParams()
            self.malicious_params.corrupt_ratio_start = int(os.getenv("CORRUPT_RATIO_START"))
            self.malicious_params.corrupt_ratio_end = int(os.getenv("CORRUPT_RATIO_END"))
            self.malicious_params.corrupt_special_packet_ratio_start = int(
                os.getenv("CORRUPT_SPECIAL_PACKET_RATIO_START"))
            self.malicious_params.corrupt_special_packet_ratio_end = int(os.getenv("CORRUPT_SPECIAL_PACKET_RATIO_END"))

            # 初始化路由器类型
            router_type = int(os.getenv("ROUTER_TYPE"))
            if (router_type != tm.RouterType.NORMAL_ROUTER) and (router_type != tm.RouterType.PATH_VALIDATION_ROUTER):
                raise ValueError("unsupported router type")
            else:
                self.router_type = router_type

            # 初始化 sec_path_mab 策略的类型
            sec_path_mab_type = int(os.getenv("SEC_PATH_MAB_TYPE"))
            if (sec_path_mab_type != tm.SecPathMabType.SEC_PATH_MAB_STRATEGY_FIXED_BATCH) and (
                    sec_path_mab_type != tm.SecPathMabType.SEC_PATH_MAB_STRATEGY_DYNAMIC_BATCH):
                raise ValueError("unsupported router type")
            else:
                self.sec_path_mab_type = sec_path_mab_type

        except Exception as e:
            print(f"load from env failed: {e}")

    def load_from_file(self):
        print("load from file", flush=True)
        try:
            with open("C:\\zhf_projects\\security\\security_topology\\images\\lir_node\\resources\\envs.txt") as f:
                for line in f.readlines():
                    line = line.strip()  # 去除换行符和首尾空格

                    # 跳过空行和注释行
                    if not line or line.startswith("#"):
                        continue

                    if "=" not in line:
                        continue

                    # 仅在第一个等号处分割，防止 value 中包含等号
                    field, value = line.split("=", 1)
                    field = field.strip()
                    value = value.strip()

                    # ---------------- 基础配置 ----------------
                    if field == "LISTEN_PORT":
                        self.listen_port = value
                    elif field == "ENABLE_FRR":
                        self.enable_frr = value
                    elif field == "CONTAINER_NAME":
                        self.container_name = value
                    elif field == "BF_EFFECTIVE_BITS":
                        self.bf_effective_bits = int(value)
                    elif field == "PVF_EFFECTIVE_BITS":
                        self.pvf_effective_bits = int(value)
                    elif field == "HASH_SEED":
                        self.hash_seed = int(value)
                    elif field == "NUMBER_OF_HASH_FUNCTIONS":
                        self.number_of_hash_functions = int(value)
                    elif field == "ROUTING_TABLE_TYPE":
                        self.routing_table_type = int(value)
                    elif field == "NODE_ID":
                        self.node_id = int(value)
                    elif field == "GRAPH_NODE_ID":
                        self.graph_node_id = int(value)
                    elif field == "LIR_SINGLE_TIME_ENCODING_COUNT":
                        self.lir_single_time_encoding_count = int(value)
                    elif field == "ENABLE_SRV6":
                        self.enable_srv6 = value

                    # ---------------- 补全缺失的基础变量 ----------------
                    elif field == "TRANSMISSION_TYPE":
                        self.transmission_type = int(value)
                    elif field == "NUMBER_OF_NODES":
                        self.number_of_nodes = int(value)
                    elif field == "MULTIPATH_ROUTING_TYPE":
                        self.multipath_routing_type = int(value)

                    # ---------------- 恶意参数配置 ----------------
                    elif field.startswith("CORRUPT_"):
                        # 如果是第一次遇到恶意参数，初始化 MaliciousParams
                        if self.malicious_params is None:
                            self.malicious_params = MaliciousParams()

                        if field == "CORRUPT_RATIO_START":
                            self.malicious_params.corrupt_ratio_start = int(value)
                            print("start_ratio:", self.malicious_params.corrupt_ratio_start, flush=True)
                        elif field == "CORRUPT_RATIO_END":
                            self.malicious_params.corrupt_ratio_end = int(value)
                            print("end_ratio:", self.malicious_params.corrupt_ratio_end, flush=True)
                        elif field == "CORRUPT_SPECIAL_PACKET_RATIO_START":
                            self.malicious_params.corrupt_special_packet_ratio_start = int(value)
                        elif field == "CORRUPT_SPECIAL_PACKET_RATIO_END":
                            self.malicious_params.corrupt_special_packet_ratio_end = int(value)
                        else:
                            print(f"Warning: Unknown malicious parameter '{field}'")

                    # ---------------- 路由器类型及校验 ----------------
                    elif field == "ROUTER_TYPE":
                        router_type = int(value)
                        if (router_type != tm.RouterType.NORMAL_ROUTER) and (
                                router_type != tm.RouterType.PATH_VALIDATION_ROUTER):
                            raise ValueError(f"unsupported router type configured in envs.txt: {router_type}")
                        else:
                            self.router_type = router_type

                    else:
                        print(f"Warning: Unknown environment variable '{field}'")

        except FileNotFoundError:
            print("Error: /home/zeusnet/Projects/lir_node/lir_node/envs.txt not found.", flush=True)
        except Exception as e:
            print(f"load from file failed: {e}", flush=True)


env_loader = EnvLoader()
