import random
from typing import List


def sample_discrete(probabilities: List[float]) -> int:
    """
    使用 Python 内置库进行带权重的离散采样
    """
    # random.choices 接受 weights (概率分布) 并返回一个列表，这里取 [0]
    # population 是我们想要返回的样本池，这里就是下标 0 到 len-1
    return random.choices(
        population=range(len(probabilities)),
        weights=probabilities,
        k=1
    )[0]
