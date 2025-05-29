import os
from doctest import Example


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
        self.node_id = None
        self.graph_node_id = None
        self.lir_single_time_encoding_count = None
        self.enable_srv6 = None  # 是否开启 SRv6 in str format

        self.load_from_env()
        if None in [self.listen_port, self.enable_frr, self.container_name, self.bf_effective_bits,
                    self.pvf_effective_bits, self.hash_seed, self.number_of_hash_functions, self.routing_table_type,
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
            self.node_id = int(os.getenv("NODE_ID"))
            self.graph_node_id = int(os.getenv("GRAPH_NODE_ID"))
            self.lir_single_time_encoding_count = int(os.getenv("LIR_SINGLE_TIME_ENCODING_COUNT"))
            self.enable_srv6 = os.getenv("ENABLE_SRV6")  # 是否开启 SRv6 in str format
        except Exception as e:
            print(f"load from env failed: {e}")

    def load_from_file(self):
        with open("/home/zeusnet/Projects/lir_node/lir_node/envs.txt") as f:
            for line in f.readlines():
                line = line.rstrip("\n")
                field, value = line.split("=")
                # 根据字段名设置对应的属性
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
                else:
                    print(f"Warning: Unknown environment variable '{field}'")


env_loader = EnvLoader()
