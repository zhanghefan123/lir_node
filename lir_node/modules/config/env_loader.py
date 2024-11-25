import os


class EnvLoader:
    def __init__(self):
        self.listen_port = os.getenv("LISTEN_PORT")
        self.enable_frr = os.getenv("ENABLE_FRR")
        self.container_name = os.getenv("CONTAINER_NAME")
        self.effective_bits = int(os.getenv("EFFECTIVE_BITS"))
        self.hash_seed = int(os.getenv("HASH_SEED"))
        self.number_of_hash_functions = int(os.getenv("NUMBER_OF_HASH_FUNCTIONS"))
        self.routing_table_type = int(os.getenv("ROUTING_TABLE_TYPE"))


env_loader = EnvLoader()
