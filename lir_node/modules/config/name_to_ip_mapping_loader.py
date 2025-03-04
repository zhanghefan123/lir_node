class NameToIdIpMappingLoader:
    def __init__(self, file_path: str, container_name: str):
        """
        ip 地址映射加载器的初始化
        :param file_path 路径
        """
        self.file_path = file_path
        self.container_name = container_name
        self.name_to_first_ipv4_mapping = {}
        self.name_to_first_ipv6_mapping = {}
        self.name_to_id_mapping = {}
        self.load()
        self.exclude_self()

    def load(self):
        """
        加载从 container_name -> ip 的映射
        加载从 container_name -> id 的映射
        :return:
        """
        delimiter = "->"
        with open(self.file_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.rstrip("\n")
                if line == "":
                    continue
                items = line.split(delimiter)
                self.name_to_id_mapping[items[0]] = int(items[1])
                self.name_to_first_ipv4_mapping[items[0]] = items[2]
                self.name_to_first_ipv6_mapping[items[0]] = items[3]

    def exclude_self(self):
        """
        除去自己节点
        :return:
        """
        self.name_to_id_mapping.pop(self.container_name)
        self.name_to_first_ipv4_mapping.pop(self.container_name)
        self.name_to_first_ipv6_mapping.pop(self.container_name)
