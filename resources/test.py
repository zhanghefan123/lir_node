from tools import count as cm

if __name__ == '__main__':
    # 总发包数量
    TOTAL = 1000

    # 链路成功率（1→2，2→3）
    link_rates = [0.8, 0.7]

    res = cm.calc_cascade_sample_counts(TOTAL, link_rates)

    print(res)
