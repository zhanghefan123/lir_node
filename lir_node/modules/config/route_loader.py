from typing import List
from modules.config import env_loader as elm


class Route:
    def __init__(self, source: int, destination: int, path_length: int, link_identifiers: List, node_ids: List):
        """
        初始化 LiRRoute
        :param source: 源头
        :param destination: 目的
        :param path_length: 路径长度
        :param link_identifiers: 链路表示序列
        :param node_ids: 节点标识序列
        """
        self.source = source
        self.destination = destination
        self.path_length = path_length
        self.link_identifiers = link_identifiers
        self.node_ids = node_ids

    def __str__(self):
        return (f"source: {self.source} "
                f"destination: {self.destination} "
                f"path_length: {self.path_length} "
                f"link_identifiers: {self.link_identifiers} "
                f"node_ids: {self.node_ids}")


def load_routes() -> List[Route]:
    """
    加载路由条目
    :return: 路由条目系列
    """
    """
    1,4,3,1,2,3,3,5,4
    1,3,2,1,2,3,3
    1,2,1,1,2
    """
    # 路由文件
    routes_file_path = f"/configuration/{elm.env_loader.container_name}/route/lir.txt"
    # 路由条目
    routes = []
    # 打开文件
    with open(routes_file_path) as f:
        # 读取每一行
        all_lines = f.readlines()
        for line in all_lines:
            line = line.rstrip("\n")
            if line == "":
                continue
            link_identifiers = []
            node_ids = []
            result = line.split(",")
            source = int(result[0])  # 1. 获取源
            destination = int(result[1])  # 2. 获取目的
            path_length = int(result[2])  # 3. 获取路径长度
            for index in range(3, 3 + path_length * 2):
                if index % 2 == 1:
                    link_identifier = int(result[index])  # 4. 获取链路标识
                    link_identifiers.append(link_identifier)
                else:
                    node_id = int(result[index])  # 5. 获取节点 id
                    node_ids.append(node_id)
            route = Route(source, destination, path_length, link_identifiers, node_ids)
            routes.append(route)
    return routes
