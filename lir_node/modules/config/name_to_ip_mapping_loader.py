class NameToIdMappingLoader:
    def __init__(self, file_path: str):
        """
        ip 地址映射加载器的初始化
        """
        self.file_path = file_path
        self.mapping = {}
        self.load()

    def load(self):
        """
        进行 id 到 ip 的映射的加载
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
                self.mapping[items[0]] = items[1]