import random
from typing import Callable

# 等价于 type DecideFunction func() int
# 定义一个类型提示：一个不接受参数并返回 int 的函数
DecideFunction = Callable[[], int]


class ActionDecider:
    def __init__(self, decide_function: DecideFunction):
        # 接收并保存闭包函数
        self.decide_function = decide_function

    def should_take_action(self) -> bool:
        # 执行函数并判断结果是否为 1
        return self.decide_function() == 1


def create_uniform_decider(start: float, end: float, node_index: int) -> ActionDecider:
    """
    进行均匀分布的生成的损坏者的构建
    """
    # 检查范围是否合法。在 Python 中通常直接抛出 ValueError 代替 Go 的返回 error
    if start > end:
        raise ValueError("start must <= end")

    # 内部创建独立的随机源 (这里使用 node_index 作为种子, 确保每次运行结果一致)
    # 优化点：使用局部的 random.Random 实例，避免污染全局随机状态
    rng = random.Random(node_index)

    # 创建 decide function (闭包)
    def decide_function() -> int:
        # rng.random() 返回 [0.0, 1.0) 之间的浮点数
        current_drop_rate = start + rng.random() * (end - start)
        if rng.random() < current_drop_rate:
            return 1
        else:
            return 0

    # 创建并返回 decider
    decider = ActionDecider(decide_function)
    return decider
