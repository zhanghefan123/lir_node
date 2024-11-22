from typing import List
from modules.config import env_loader as elm


class LiRRoute:
    def __init__(self, source: int, destination: int, path_length: int, link_identifiers: List, node_ids: List):
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


def load_lir_routes() -> List[LiRRoute]:
    """
    加载路由条目
    :return: 路由系列
    """
    lir_routes_file_path = f"/configuration/{elm.env_loader.container_name}/route/lir.txt"
    lir_routes = []
    with open(lir_routes_file_path) as f:
        all_lines = f.readlines()
        for line in all_lines:
            line = line.rstrip("\n")
            if line == "":
                continue
            link_identifiers = []
            node_ids = []
            result = line.split(",")
            source = int(result[0])
            destination = int(result[1])
            path_length = int(result[2])
            for index in range(0, path_length, 2):
                link_identifier = int(result[3+index])
                node_id = int(result[4+index])
                link_identifiers.append(link_identifier)
                node_ids.append(node_id)
            lir_route = LiRRoute(source, destination, path_length, link_identifiers, node_ids)
            lir_routes.append(lir_route)
    return lir_routes

















