class NameToIdIpMappingLoader:
    def __init__(self, file_path: str):
        """
        ip 地址映射加载器的初始化
        """
        self.file_path = file_path
        self.container_name_to_ip_mapping = {}
        self.container_name_to_id_mapping = {}
        self.load()

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
                self.container_name_to_id_mapping[items[0]] = int(items[1])
                self.container_name_to_ip_mapping[items[0]] = items[2]

