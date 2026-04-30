import subprocess
import shlex


def setup_tbf_qdisc(interface="ln1_idx1", rate="4000mbit",
                    burst="500mb", latency="50ms"):
    """
    使用TC设置令牌桶过滤器(TBF)队列规则

    Args:
        interface: 网络接口名
        rate: 限制速率
        burst: 突发大小
        latency: 延迟时间
    """
    try:
        # 构建tc命令
        cmd = f"tc qdisc add dev {interface} root tbf rate {rate} burst {burst} latency {latency}"

        print(f"执行命令: {cmd}")

        # 安全地执行命令
        result = subprocess.run(
            shlex.split(cmd),
            capture_output=True,
            text=True,
            check=True
        )

        print("TC命令执行成功!")
        print(f"输出: {result.stdout}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"发生错误: {e}")
        return False


# 使用示例
if __name__ == "__main__":
    setup_tbf_qdisc()
