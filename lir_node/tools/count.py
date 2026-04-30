from typing import List


def calc_cascade_sample_counts(total_packets, link_success_rates) -> List[int]:
    """
    串联链路公平采样分配
    节点顺序: 1 → 2 → 3 → ... → n
    链路: [1→2成功率, 2→3成功率, ...]

    返回：每个节点应该发送多少包，使得最终成功接收数量尽量相等
    """
    num_nodes = len(link_success_rates) + 1
    node_probs = []

    p_accum = 1.0

    for p in link_success_rates:
        p_accum *= p
        node_probs.append(p_accum)

    # 权重 = 1 / 成功概率（概率越低，需要发越多）
    weights = [1.0 / p for p in node_probs]
    total_weight = sum(weights)

    # 按权重分配总发包数
    counts = [round(total_packets * w / total_weight) for w in weights]

    # 简单修正：总和可能差1~2，直接补到 total_packets
    diff = total_packets - sum(counts)
    for i in range(abs(diff)):
        counts[i % num_nodes] += 1 if diff > 0 else -1

    # 进行结果的返回
    return counts
