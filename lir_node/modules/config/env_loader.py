import os
from dataclasses import dataclass
from multiprocessing.managers import Value

from defined_types import types as tm


@dataclass
class MaliciousParams:
    corrupt_ratio_start: int = 0
    corrupt_ratio_end: int = 0
    corrupt_special_packet_ratio_start: int = 0
    corrupt_special_packet_ratio_end: int = 0


class EnvLoader:
    # ============================================================
    # 配置字段
    # ============================================================

    # 环境变量名称 -> EnvLoader 属性名称
    CONFIG_FIELDS = {
        "LISTEN_PORT": "listen_port",
        "ENABLE_FRR": "enable_frr",
        "CONTAINER_NAME": "container_name",

        "BF_EFFECTIVE_BITS": "bf_effective_bits",
        "PVF_EFFECTIVE_BITS": "pvf_effective_bits",
        "HASH_SEED": "hash_seed",
        "NUMBER_OF_HASH_FUNCTIONS": "number_of_hash_functions",

        "ROUTING_TABLE_TYPE": "routing_table_type",

        "NODE_ID": "node_id",
        "GRAPH_NODE_ID": "graph_node_id",

        "LIR_SINGLE_TIME_ENCODING_COUNT": "lir_single_time_encoding_count",

        "ENABLE_SRV6": "enable_srv6",
        "ENABLE_SEC_PATH_MAB": "enable_sec_path_mab",

        "NUMBER_OF_HOPS": "number_of_hops",
        "NUMBER_OF_SEGMENTS_PER_HOP": "number_of_segments_per_hop",

        "ROUTER_TYPE": "router_type",
        "SELIR_TYPE": "selir_type",
        "EPIC_TYPE": "epic_type",
        "SEC_PATH_MAB_TYPE": "sec_path_mab_type",

        "EXPERIMENT_TYPE": "experiment_type",
    }

    # 需要转换成 int 的字段
    INTEGER_FIELDS = {
        "BF_EFFECTIVE_BITS",
        "PVF_EFFECTIVE_BITS",
        "HASH_SEED",
        "NUMBER_OF_HASH_FUNCTIONS",

        "ROUTING_TABLE_TYPE",

        "NODE_ID",
        "GRAPH_NODE_ID",

        "LIR_SINGLE_TIME_ENCODING_COUNT",

        "NUMBER_OF_HOPS",
        "NUMBER_OF_SEGMENTS_PER_HOP",

        "ROUTER_TYPE",
        "SELIR_TYPE",
        "EPIC_TYPE",
        "SEC_PATH_MAB_TYPE",

        "EXPERIMENT_TYPE",
    }

    # 恶意节点相关参数
    MALICIOUS_FIELDS = {
        "CORRUPT_RATIO_START": "corrupt_ratio_start",
        "CORRUPT_RATIO_END": "corrupt_ratio_end",
        "CORRUPT_SPECIAL_PACKET_RATIO_START":
            "corrupt_special_packet_ratio_start",
        "CORRUPT_SPECIAL_PACKET_RATIO_END":
            "corrupt_special_packet_ratio_end",
    }

    # 环境变量模式下必须存在的字段
    REQUIRED_ENV_FIELDS = {
        *CONFIG_FIELDS.keys(),
        *MALICIOUS_FIELDS.keys(),
    }

    def __init__(
            self,
            config_file_path: str =
            "C:\\zhf_projects\\security\\security_topology\\images\\lir_node\\resources\\envs.txt",
    ):
        self.config_file_path = config_file_path

        # --------------------------------------------------------
        # 基础配置
        # --------------------------------------------------------
        self.listen_port = None
        self.enable_frr = None
        self.container_name = None

        self.bf_effective_bits = None
        self.pvf_effective_bits = None
        self.hash_seed = None
        self.number_of_hash_functions = None

        self.routing_table_type = None

        self.node_id = None
        self.graph_node_id = None

        self.lir_single_time_encoding_count = None

        self.enable_srv6 = None
        self.enable_sec_path_mab = None

        self.number_of_hops = None
        self.number_of_segments_per_hop = None

        # --------------------------------------------------------
        # 类型配置
        # --------------------------------------------------------
        self.router_type: int = -1
        self.selir_type: int = -1
        self.epic_type: int = -1
        self.sec_path_mab_type: int = -1
        self.experiment_type: int = 0

        # --------------------------------------------------------
        # 恶意节点配置
        # --------------------------------------------------------
        self.malicious_params = MaliciousParams()

        # --------------------------------------------------------
        # 加载配置
        # --------------------------------------------------------
        self.load()

    # ============================================================
    # 总入口
    # ============================================================

    def load(self):
        """
        优先从环境变量加载配置。

        如果环境变量不完整，则回退到配置文件。
        """

        missing_fields = self.get_missing_env_fields()

        if not missing_fields:
            print("load configuration from environment variables", flush=True)
            self.load_from_env()
        else:
            print(
                "environment variables are incomplete, "
                "fallback to configuration file",
                flush=True,
            )

            print(
                f"missing environment variables: "
                f"{', '.join(sorted(missing_fields))}",
                flush=True,
            )

            self.load_from_file()

        self.validate()

    # ============================================================
    # 环境变量检查
    # ============================================================

    def get_missing_env_fields(self):
        """
        返回缺失的环境变量。
        """

        required_fields = (
            self.REQUIRED_ENV_FIELDS
        )

        return [
            field
            for field in required_fields
            if os.getenv(field) is None
        ]

    # ============================================================
    # 从环境变量加载
    # ============================================================

    def load_from_env(self):
        try:
            # 普通配置
            for field in self.CONFIG_FIELDS:
                value = os.getenv(field)

                if value is None:
                    raise ValueError(
                        f"missing environment variable: {field}"
                    )

                self.set_config(field, value)

            # 恶意节点配置
            for field in self.MALICIOUS_FIELDS:
                value = os.getenv(field)

                if value is None:
                    raise ValueError(
                        f"missing environment variable: {field}"
                    )

                self.set_config(field, value)

        except Exception as e:
            raise RuntimeError(
                f"load configuration from env failed: {e}"
            ) from e

    # ============================================================
    # 从文件加载
    # ============================================================

    def load_from_file(self):
        print(
            f"load configuration from file: "
            f"{self.config_file_path}",
            flush=True,
        )

        try:
            with open(self.config_file_path, "r") as f:
                for raw_line in f:
                    line = raw_line.strip()

                    # 跳过空行和注释
                    if not line or line.startswith("#"):
                        continue

                    # 非 KEY=VALUE 格式
                    if "=" not in line:
                        print(
                            f"ignore invalid config line: {line}",
                            flush=True,
                        )
                        continue

                    field, value = line.split("=", 1)

                    field = field.strip()
                    value = value.strip()

                    self.set_config(field, value)

        except FileNotFoundError as e:
            raise RuntimeError(
                f"configuration file not found: "
                f"{self.config_file_path}"
            ) from e

        except Exception as e:
            raise RuntimeError(
                f"load configuration from file failed: {e}"
            ) from e

    # ============================================================
    # 统一设置配置
    # ============================================================

    def set_config(self, field: str, value):
        """
        统一处理：
        1. 字段识别
        2. 类型转换
        3. 属性赋值
        """

        # --------------------------------------------------------
        # 普通配置
        # --------------------------------------------------------
        if field in self.CONFIG_FIELDS:

            attr_name = self.CONFIG_FIELDS[field]

            if field in self.INTEGER_FIELDS:
                value = int(value)

            setattr(self, attr_name, value)
            return

        # --------------------------------------------------------
        # 恶意节点配置
        # --------------------------------------------------------
        if field in self.MALICIOUS_FIELDS:
            attr_name = self.MALICIOUS_FIELDS[field]

            setattr(
                self.malicious_params,
                attr_name,
                int(value),
            )
            return

        # --------------------------------------------------------
        # 未知字段
        # --------------------------------------------------------
        print(
            f"warning: unknown configuration field '{field}'",
            flush=True,
        )

    # ============================================================
    # 配置合法性检查
    # ============================================================

    def validate(self):
        """
        所有配置加载完成后统一校验。
        """

        self.validate_selir_type()
        self.validate_epic_type()
        self.validate_router_type()
        self.validate_sec_path_mab_type()

        print("configuration loaded successfully", flush=True)

    def validate_selir_type(self):
        valid_selir_types = {
            tm.SelirType.SLOW_VERSION,
            tm.SelirType.FAST_VERSION,
        }
        if self.selir_type not in valid_selir_types:
            raise ValueError(
                f"unsupported router type: {self.selir_type}"
            )

    def validate_epic_type(self):
        valid_epic_types = {
            tm.EpicType.EPIC_L3_VERSION,
            tm.EpicType.EPIC_L4_VERSION,
        }
        if self.epic_type not in valid_epic_types:
            raise ValueError(
                f"unsupported router type: {self.selir_type}"
            )

    def validate_router_type(self):
        valid_router_types = {
            tm.RouterType.NORMAL_ROUTER,
            tm.RouterType.PATH_VALIDATION_ROUTER,
        }

        if self.router_type not in valid_router_types:
            raise ValueError(
                f"unsupported router type: {self.router_type}"
            )

    def validate_sec_path_mab_type(self):
        valid_types = {
            tm.SecPathMabType.SEC_PATH_MAB_STRATEGY_FIXED_BATCH,
            tm.SecPathMabType.SEC_PATH_MAB_STRATEGY_DYNAMIC_BATCH,
            tm.SecPathMabType.SEC_PATH_MAB_STRATEGY_PATH_BANDIT,
        }

        if self.sec_path_mab_type not in valid_types:
            raise ValueError(
                f"unsupported sec_path_mab type: "
                f"{self.sec_path_mab_type}"
            )

    # ============================================================
    # 调试
    # ============================================================

    def print_config(self):
        """
        打印当前配置，方便排查 Docker 环境变量问题。
        """

        print(
            "================ CONFIGURATION ================",
            flush=True,
        )

        for field, attr_name in self.CONFIG_FIELDS.items():
            value = getattr(self, attr_name)

            print(
                f"{field:<40} = {value}",
                flush=True,
            )

        print(
            "---------------- MALICIOUS ----------------",
            flush=True,
        )

        for field, attr_name in self.MALICIOUS_FIELDS.items():
            value = getattr(
                self.malicious_params,
                attr_name,
            )

            print(
                f"{field:<40} = {value}",
                flush=True,
            )

        print(
            "===============================================",
            flush=True,
        )


env_loader = EnvLoader()
