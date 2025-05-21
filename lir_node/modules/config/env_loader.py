import os


class EnvLoader:
    def __init__(self):
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


env_loader = EnvLoader()
