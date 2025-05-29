import subprocess
from typing import List
from modules.config import env_loader as elm


def read_srv6_routes() -> List[str]:
    """
    读取 SRv6 路由信息
    :return: 路由信息列表
    """
    srv6_file_path = f"/configuration/{elm.env_loader.container_name}/route/srv6.txt"
    try:
        with open(srv6_file_path, "r") as f:
            all_routes = f.readlines()
            return all_routes
    except FileNotFoundError:
        print("no routes are recorded")
        return []


def insert_srv6_routes(srv6_routes: List[str]) -> None:
    """
    插入 SRv6 路由信息
    :param srv6_routes: SRv6 路由信息
    :return:
    """

    # 进行命令的执行
    for route in srv6_routes:
        try:
            result = subprocess.run(route, capture_output=True, shell=True, check=True)
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
        except Exception as e:
            print(f"error executing command {route}: {e}")