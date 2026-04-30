from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class SourceDestParams:
    source: str
    destination: str


@dataclass_json
@dataclass
class KShortestPathParams:
    number_of_paths: int
    limit_of_cost: float


@dataclass_json
@dataclass
class RatioDistribution:
    start: float
    end: float


@dataclass_json
@dataclass
class SimNodeParam:
    index: int
    type: str
    # 核心修复在这里：必须加上 = None
    corrupt_ratio: Optional[RatioDistribution] = None
    corrupt_special_packet_ratio: Optional[RatioDistribution] = None


@dataclass_json
@dataclass
class SimAbsLinkParam:
    source_node: SimNodeParam
    target_node: SimNodeParam
    intermediate_node: SimNodeParam


@dataclass_json
@dataclass
class SimLinkParam:
    source_node: SimNodeParam
    target_node: SimNodeParam


@dataclass_json
@dataclass
class GraphParams:
    # 加上 = None
    source_dest_params: Optional[SourceDestParams] = None
    k_shortest_path_params: Optional[KShortestPathParams] = None

    # 如果确保 JSON 里一定有这些列表，可以不加默认值。
    # 如果某些列表可能缺失（如 available_paths），必须用 field(default_factory=list)
    nodes: List[SimNodeParam] = field(default_factory=list)
    access_links: List[SimAbsLinkParam] = field(default_factory=list)
    pv_links: List[SimAbsLinkParam] = field(default_factory=list)
    links: List[SimLinkParam] = field(default_factory=list)
    coverage_paths: List[str] = field(default_factory=list)

    # 你的 JSON 里面没有 available_paths，所以必须给默认值，否则会报 KeyError: 'available_paths'
    available_paths: List[str] = field(default_factory=list)


if __name__ == "__main__":
    with open("../../../../resources/topology.json", encoding="utf-8") as f:
        json_string = f.read()

    # 现在解析绝对不会再报错了！
    graph_params = GraphParams.from_json(json_string)

    # 测试打印一下
    print("解析成功！")
    print(f"源节点: {graph_params.source_dest_params.source}")
    print(f"节点0有drop_ratio吗? {graph_params.nodes[0].drop_ratio}")  # 应该是 None
    print(f"节点1有drop_ratio吗? {graph_params.nodes[1].drop_ratio}")  # 应该是 RatioDistribution 对象

    print(graph_params)