from dataclasses import dataclass


@dataclass
class SimNodeBase:
    node_name: str
    index: int


if __name__ == "__main__":
    # 使用方式完全一样
    node = SimNodeBase(node_name="Router-1", index=0)

    # 打印出来也会非常漂亮：SimNodeBase(node_name='Router-1', index=0)
    print(node)
