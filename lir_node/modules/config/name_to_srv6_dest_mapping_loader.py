class NameToSrv6DestMappingLoader:
    def __init__(self, file_path: str):
        """
        srv6 目的地址映射加载器的初始化
        :param file_path: 路径
        """
        self.file_path = file_path
        self.container_name_to_ipv6_mapping = {}
        self.container_name_to_dest_ifname_mapping = {}
        self.load()

    def load(self):
        delimiter = "->"
        with open(self.file_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.rstrip("\n")
                if line == "":
                    continue
                items = line.split(delimiter)
                self.container_name_to_ipv6_mapping[items[0]] = items[1]
                self.container_name_to_dest_ifname_mapping[items[0]] = items[2]