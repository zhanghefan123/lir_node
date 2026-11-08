class NetworkLayer:
    SRV6 = 0
    IP = 4
    LIR = 1
    ICING = 2
    OPT = 3
    IPV4 = 4
    SELIR = 5
    IPV6 = 6
    FAST_SELIR = 7
    MULTICAST_SELIR = 8
    SESSION_SETUP = 9
    MULTICAST_SESSION_SETUP = 10
    EPIC_SESSION_SETUP = 11  # 这个要看内核之中的值是多少
    EPIC_DATA = 12
    ATLAS_DATA = 13
    MULTIPATH_SELIR = 14
    MULTICAST_OPT = 15
    SEC_PATH_MAB = (16)
    SEC_PATH_MAB_ACK = (17)
    OPT_ACK = (18)
    # ATLAS_DATA = 16
    # MULTIPATH_SELIR = 17
    # MULTICAST_OPT = 18
    # SEC_PATH_MAB = 13
    # SEC_PATH_MAB_ACK = 14
    # OPT_ACK = 15
    # 这个值不能超过 15 因为 version 最多只有 4 bit (MULTIPATH_SELIR 和 MULTICAST_OPT 已经进行了修改)

    STR_TO_PROTOCOL_MAP = {
        "SRV6": SRV6,
        "IP": IP,
        "LIR": LIR,
        "ICING": ICING,
        "OPT": OPT,
        "SELIR": SELIR,
        "FAST_SELIR": FAST_SELIR,
        "MULTICAST_SELIR": MULTICAST_SELIR,
        "EPIC_SESSION_SETUP": EPIC_SESSION_SETUP,
        "EPIC_DATA": EPIC_DATA,
        "ATLAS": ATLAS_DATA,  # 注意这里原代码是映射到 ATLAS_DATA
        "MULTIPATH_SELIR": MULTIPATH_SELIR,
        "MULTICAST_OPT": MULTICAST_OPT,
        # "SEC_PATH_MAB": SEC_PATH_MAB,
        # "SEC_PATH_MAB_ACK": SEC_PATH_MAB_ACK,
        # "OPT_ACK": OPT_ACK,
    }

    PROTOCOL_TO_STR_MAP = {
        SRV6: "SRV6",
        IP: "IP",
        LIR: "LIR",
        ICING: "ICING",
        OPT: "OPT",
        SELIR: "SELIR",
        FAST_SELIR: "FAST_SELIR",
        MULTICAST_SELIR: "MULTICAST_SELIR",
        EPIC_SESSION_SETUP: "EPIC_SESSION_SETUP",
        EPIC_DATA: "EPIC_DATA",
        ATLAS_DATA: "ATLAS",  # 对应原代码中的 ATLAS -> ATLAS_DATA 映射
        MULTIPATH_SELIR: "MULTIPATH_SELIR",
        MULTICAST_OPT: "MULTICAST_OPT",
        # SEC_PATH_MAB: "SEC_PATH_MAB",
        # SEC_PATH_MAB_ACK: "SEC_PATH_MAB_ACK",
        # OPT_ACK: "OPT_ACK"
    }

    @classmethod
    def turn_str_into_type(cls, network_layer_str: str) -> int:
        if network_layer_str not in cls.STR_TO_PROTOCOL_MAP.keys():
            raise ValueError("unsupported network layer: %s", network_layer_str)
        else:
            return cls.STR_TO_PROTOCOL_MAP[network_layer_str]

    @classmethod
    def turn_type_into_str(cls, network_layer_type: int) -> str:
        if network_layer_type not in cls.PROTOCOL_TO_STR_MAP.keys():
            raise ValueError("unsupported network layer: %d", network_layer_type)
        else:
            return cls.PROTOCOL_TO_STR_MAP[network_layer_type]


class PathValidationTransmissionType:
    UNICAST_TRANSMISSION_TYPE_NOT_SPECIFIED = 0
    UNICAST_TRANSMISSION_TYPE = 1
    MULTIPATH_TRANSMISSION_TYPE = 2
    MULTICAST_TRANSMISSION_TYPE = 3
    MAB_TRANSMISSION_TYPE = 4

    # 字符串 -> 数字 映射
    STR_TO_TYPE_MAP = {
        "UNICAST_TRANSMISSION_TYPE": UNICAST_TRANSMISSION_TYPE,
        "MULTIPATH_TRANSMISSION_TYPE": MULTIPATH_TRANSMISSION_TYPE,
        "MULTICAST_TRANSMISSION_TYPE": MULTICAST_TRANSMISSION_TYPE,
        "MAB_TRANSMISSION_TYPE": MAB_TRANSMISSION_TYPE,
    }

    # 数字 -> 字符串 映射
    TYPE_TO_STR_MAP = {
        UNICAST_TRANSMISSION_TYPE: "UNICAST_TRANSMISSION_TYPE",
        MULTIPATH_TRANSMISSION_TYPE: "MULTIPATH_TRANSMISSION_TYPE",
        MULTICAST_TRANSMISSION_TYPE: "MULTICAST_TRANSMISSION_TYPE",
        MAB_TRANSMISSION_TYPE: "MAB_TRANSMISSION_TYPE",
    }

    @classmethod
    def turn_str_into_type(cls, type_str: str) -> int:
        """字符串转换为传输类型数字"""
        if type_str not in cls.STR_TO_TYPE_MAP:
            raise ValueError(f"unsupported transmission type: {type_str}")
        return cls.STR_TO_TYPE_MAP[type_str]

    @classmethod
    def turn_type_into_str(cls, type_int: int) -> str:
        """传输类型数字转换为字符串"""
        if type_int not in cls.TYPE_TO_STR_MAP:
            raise ValueError(f"unsupported transmission type: {type_int}")
        return cls.TYPE_TO_STR_MAP[type_int]


class RoutingTableType:
    ARRAY_BASED_ROUTING_TABLE_TYPE = 1
    HASH_BASED_ROUTING_TABLE_TYPE = 2
    ARRAY_BASED_MULTIPATH_TABLE_TYPE = 3

    STR_TO_TYPE_MAP = {
        "ARRAY_BASED_ROUTING_TABLE_TYPE": ARRAY_BASED_ROUTING_TABLE_TYPE,
        "HASH_BASED_ROUTING_TABLE_TYPE": HASH_BASED_ROUTING_TABLE_TYPE,
        "ARRAY_BASED_MULTIPATH_TABLE_TYPE": ARRAY_BASED_MULTIPATH_TABLE_TYPE,
    }

    TYPE_TO_STR_MAP = {
        ARRAY_BASED_ROUTING_TABLE_TYPE: "ARRAY_BASED_ROUTING_TABLE_TYPE",
        HASH_BASED_ROUTING_TABLE_TYPE: "HASH_BASED_ROUTING_TABLE_TYPE",
        ARRAY_BASED_MULTIPATH_TABLE_TYPE: "ARRAY_BASED_MULTIPATH_TABLE_TYPE",
    }

    @classmethod
    def turn_str_into_type(cls, type_str: str) -> int:
        if type_str not in cls.STR_TO_TYPE_MAP:
            raise ValueError(f"unsupported routing table type: {type_str}")
        return cls.STR_TO_TYPE_MAP[type_str]

    @classmethod
    def turn_type_into_str(cls, type_int: int) -> str:
        if type_int not in cls.TYPE_TO_STR_MAP:
            raise ValueError(f"unsupported routing table type: {type_int}")
        return cls.TYPE_TO_STR_MAP[type_int]


class MultipathRoutingType:
    ATLAS_MULTIPATH_ROUTING = 1
    MULTIPATH_SELIR_ROUTING = 2

    STR_TO_TYPE_MAP = {
        "ATLAS_MULTIPATH_ROUTING": ATLAS_MULTIPATH_ROUTING,
        "MULTIPATH_SELIR_ROUTING": MULTIPATH_SELIR_ROUTING,
    }

    TYPE_TO_STR_MAP = {
        ATLAS_MULTIPATH_ROUTING: "ATLAS_MULTIPATH_ROUTING",
        MULTIPATH_SELIR_ROUTING: "MULTIPATH_SELIR_ROUTING",
    }

    @classmethod
    def turn_str_into_type(cls, type_str: str) -> int:
        if type_str not in cls.STR_TO_TYPE_MAP:
            raise ValueError(f"unsupported multipath routing type: {type_str}")
        return cls.STR_TO_TYPE_MAP[type_str]

    @classmethod
    def turn_type_into_str(cls, type_int: int) -> str:
        if type_int not in cls.TYPE_TO_STR_MAP:
            raise ValueError(f"unsupported multipath routing type: {type_int}")
        return cls.TYPE_TO_STR_MAP[type_int]


class RouterType:
    NORMAL_ROUTER = 1
    PATH_VALIDATION_ROUTER = 2

    STR_TO_TYPE_MAP = {
        "NORMAL_ROUTER": NORMAL_ROUTER,
        "PATH_VALIDATION_ROUTER": PATH_VALIDATION_ROUTER,
    }

    TYPE_TO_STR_MAP = {
        NORMAL_ROUTER: "NORMAL_ROUTER",
        PATH_VALIDATION_ROUTER: "PATH_VALIDATION_ROUTER",
    }

    @classmethod
    def turn_str_into_type(cls, type_str: str) -> int:
        if type_str not in cls.STR_TO_TYPE_MAP:
            raise ValueError(f"unsupported router type: {type_str}")
        return cls.STR_TO_TYPE_MAP[type_str]

    @classmethod
    def turn_type_into_str(cls, type_int: int) -> str:
        if type_int not in cls.TYPE_TO_STR_MAP:
            raise ValueError(f"unsupported router type: {type_int}")
        return cls.TYPE_TO_STR_MAP[type_int]


class SelirType:
    SLOW_VERSION = 1
    FAST_VERSION = 2

    STR_TO_TYPE_MAP = {
        "SLOW_VERSION": SLOW_VERSION,
        "FAST_VERSION": FAST_VERSION,
    }

    TYPE_TO_STR_MAP = {
        SLOW_VERSION: "SLOW_VERSION",
        FAST_VERSION: "FAST_VERSION",
    }

    @classmethod
    def turn_str_into_type(cls, type_str: str) -> int:
        if type_str not in cls.STR_TO_TYPE_MAP:
            raise ValueError(f"unsupported router type: {type_str}")
        return cls.STR_TO_TYPE_MAP[type_str]

    @classmethod
    def turn_type_into_str(cls, type_int: int) -> str:
        if type_int not in cls.TYPE_TO_STR_MAP:
            raise ValueError(f"unsupported router type: {type_int}")
        return cls.TYPE_TO_STR_MAP[type_int]


class EpicType:
    EPIC_L3_VERSION = 1
    EPIC_L4_VERSION = 2

    STR_TO_TYPE_MAP = {
        "EPIC_L3_VERSION": EPIC_L3_VERSION,
        "EPIC_L4_VERSION": EPIC_L4_VERSION,
    }

    TYPE_TO_STR_MAP = {
        EPIC_L3_VERSION: "EPIC_L3_VERSION",
        EPIC_L4_VERSION: "EPIC_L4_VERSION",
    }

    @classmethod
    def turn_str_into_type(cls, type_str: str) -> int:
        if type_str not in cls.STR_TO_TYPE_MAP:
            raise ValueError(f"unsupported router type: {type_str}")
        return cls.STR_TO_TYPE_MAP[type_str]

    @classmethod
    def turn_type_into_str(cls, type_int: int) -> str:
        if type_int not in cls.TYPE_TO_STR_MAP:
            raise ValueError(f"unsupported router type: {type_int}")
        return cls.TYPE_TO_STR_MAP[type_int]


class ServerType:
    NOT_SPECIFIED = 0
    TEXT = 1
    FILE = 2
    MULTIPROCESS_FILE = 3

    TYPE_TO_STR_MAP = {
        TEXT: "text",
        FILE: "file",
        MULTIPROCESS_FILE: "multiprocess_file"
    }

    # 根据 TYPE_TO_STR_MAP 反向推导
    STR_TO_TYPE_MAP = {
        "text": TEXT,
        "file": FILE,
        "multiprocess_file": MULTIPROCESS_FILE
    }

    @classmethod
    def turn_str_into_type(cls, type_str: str) -> int:
        if type_str not in cls.STR_TO_TYPE_MAP:
            raise ValueError(f"unsupported server type: {type_str}")
        return cls.STR_TO_TYPE_MAP[type_str]

    @classmethod
    def turn_type_into_str(cls, type_int: int) -> str:
        if type_int not in cls.TYPE_TO_STR_MAP:
            raise ValueError(f"unsupported server type: {type_int}")
        return cls.TYPE_TO_STR_MAP[type_int]


class IpVersion:
    Ipv4 = 0
    Ipv6 = 1

    STR_TO_TYPE_MAP = {
        "Ipv4": Ipv4,
        "Ipv6": Ipv6,
    }

    TYPE_TO_STR_MAP = {
        Ipv4: "Ipv4",
        Ipv6: "Ipv6",
    }

    @classmethod
    def turn_str_into_type(cls, type_str: str) -> int:
        if type_str not in cls.STR_TO_TYPE_MAP:
            raise ValueError(f"unsupported IP version: {type_str}")
        return cls.STR_TO_TYPE_MAP[type_str]

    @classmethod
    def turn_type_into_str(cls, type_int: int) -> str:
        if type_int not in cls.TYPE_TO_STR_MAP:
            raise ValueError(f"unsupported IP version: {type_int}")
        return cls.TYPE_TO_STR_MAP[type_int]


class TransmissionType:
    NOT_SPECIFIED = 0
    SINGLE = 1
    DURATION = 2
    BATCH = 3
    STATUS_BATCH = 4

    # 为了和其他类保持命名一致性，这里将原先的 TYPE_MAP 改名为 STR_TO_TYPE_MAP
    STR_TO_TYPE_MAP = {
        "single": SINGLE,
        "duration": DURATION,
        "batch": BATCH,
        "status_batch": STATUS_BATCH
    }

    # 新增 int -> str 的映射
    TYPE_TO_STR_MAP = {
        SINGLE: "single",
        DURATION: "duration",
        BATCH: "batch",
        STATUS_BATCH: "status_batch"
    }

    @classmethod
    def turn_str_into_type(cls, transmission_type_str: str) -> int:
        if transmission_type_str not in cls.STR_TO_TYPE_MAP:
            raise ValueError(f"not supported transmission type: {transmission_type_str}")
        return cls.STR_TO_TYPE_MAP[transmission_type_str]

    @classmethod
    def turn_type_into_str(cls, transmission_type_int: int) -> str:
        if transmission_type_int not in cls.TYPE_TO_STR_MAP:
            raise ValueError(f"not supported transmission type: {transmission_type_int}")
        return cls.TYPE_TO_STR_MAP[transmission_type_int]


class SecPathMabType:
    SEC_PATH_MAB_UNSPECIFIED = 0
    SEC_PATH_MAB_STRATEGY_FIXED_BATCH = 1  # 固定的批次的大小
    SEC_PATH_MAB_STRATEGY_DYNAMIC_BATCH = 2  # 非固定的批次的大小
    SEC_PATH_MAB_STRATEGY_PATH_BANDIT = 3  # 路径级 bandit（每条路径一个 arm）

    STR_TO_TYPE_MAP = {
        "SEC_PATH_MAB_STRATEGY_FIXED_BATCH": SEC_PATH_MAB_STRATEGY_FIXED_BATCH,
        "SEC_PATH_MAB_STRATEGY_DYNAMIC_BATCH": SEC_PATH_MAB_STRATEGY_DYNAMIC_BATCH,
        "SEC_PATH_MAB_STRATEGY_PATH_BANDIT": SEC_PATH_MAB_STRATEGY_PATH_BANDIT,
    }

    TYPE_TO_STR_MAP = {
        SEC_PATH_MAB_STRATEGY_FIXED_BATCH: "SEC_PATH_MAB_STRATEGY_FIXED_BATCH",
        SEC_PATH_MAB_STRATEGY_DYNAMIC_BATCH: "SEC_PATH_MAB_STRATEGY_DYNAMIC_BATCH",
        SEC_PATH_MAB_STRATEGY_PATH_BANDIT: "SEC_PATH_MAB_STRATEGY_PATH_BANDIT",
    }

    @classmethod
    def turn_str_into_type(cls, type_str: str) -> int:
        """字符串转换为 Netlink 消息类型数字"""
        if type_str not in cls.STR_TO_TYPE_MAP:
            raise ValueError(f"unsupported netlink message type: {type_str}")
        return cls.STR_TO_TYPE_MAP[type_str]

    @classmethod
    def turn_type_into_str(cls, type_int: int) -> str:
        """Netlink 消息类型数字转换为字符串"""
        if type_int not in cls.TYPE_TO_STR_MAP:
            raise ValueError(f"unsupported netlink message type: {type_int}")
        return cls.TYPE_TO_STR_MAP[type_int]


class NetlinkMessageType:
    CMD_USERSPACE_TO_KERNEL_UNSPEC = 0  # 未指定的命令
    CMD_ECHO = 1  # 测试回显命令
    CMD_SET_NODE_ID = 2  # 插入节点 id
    CMD_INIT_ROUTING_TABLE = 3  # 初始化路由
    CMD_INIT_INTERFACE_TABLE = 4  # 初始化转发表
    CMD_INIT_MULTIPATH_TABLE = 5  # 初始化多路径表
    CMD_INIT_SELIR = 6  # 初始化 selir 数据结构
    CMD_INIT_EPIC = 7  # 初始化 epic 数据结构
    CMD_INIT_BLOOM_FILTER = 8  # 初始化布隆过滤器
    CMD_MODIFY_BLOOM_FILTER = 9  # 进行布隆过滤器的修改
    CMD_INSERT_INTERFACE_TABLE_ENTRY = 10  # 插入接口表条目
    CMD_INSERT_ROUTING_TABLE_ENTRY = 11  # 插入路由表条目
    CMD_SET_LIR_SINGLE_TIME_ENCODING_COUNT = 12  # 设置 lir 单次插入的元素次数
    CMD_PRINT_ROUTING_TABLE_ENTRIES = 13  # 释放 net 内的空间
    CMD_SOURCE_INSERT_SEGMENT = 14  # 源节点 插入 segment
    CMD_INTERMEDIATE_INSERT_SEGMENT = 15  # 中间节点 插入 segment
    CMD_INSERT_OUTPUT_LINK_IDENTIFIERS = 16  # 插入出接口链路标识
    CMD_INSERT_RELATIONSHIP_BETWEEN_NEXT_NODE_ID_AND_PATHS = 17  # 进行关系的插入
    CMD_SET_SEC_PATH_MAB_ROUTE = 18  # 获取用户空间下发的路径
    CMD_RESET_SEC_PATH_MAB_ROUTE = 19  # 进行所选择的路由的重置
    CMD_SET_ROUTER_TYPE = 20  # 设置路由器的类型
    CMD_SET_SEC_PATH_MAB_TYPE = 21  # 设置 sec_path_mab 策略
    CMD_SET_MALICIOUS_PARAMS = 22  # 进行恶意的参数的设置
    CMD_RETRIEVE_KERNEL_INFORMATION = 23  # 获取内核返回的 counters 和  acks
    CMD_SET_SCHDULED_MALICIOUS_PARAMS = 24  # 进行恶意参数改变的事件的追加
    CMD_SET_MIN_ACK_FOR_RTT_ESTIMATION = 25  # 设置对于 RTT 的估计
    CMD_SET_BEST_PATH_ID_FOR_SOURCE = 26  # 向源设置最佳路径
    CMD_RETRIEVE_PER_PACKET_INFO = 27  # 获取每个包的信息
    CMD_SET_TOPOLOGY_INFORMATION = 28  # 进行拓扑信息的设置
    CMD_SET_EXPERIMENT_TYPE = 29  # 进行实验类型的设置
    CMD_INSERT_SESSION_TABLE_ENTRIES = 30  # 向高速会话表之中进行表项的插入
    CMD_CLEAR_SEGMENT_LIST = 31  # 清空 segment
    CMD_CLEAR_MULTIPATH_STATE = 32  # 清除当前多路径协议状态
    CMD_RESET_PROCESSING_TIME_STATISTICS = 33  # 清空并开始记录节点处理时间
    CMD_RETRIEVE_PROCESSING_TIME_STATISTICS = 34  # 停止并读取节点处理时间
    CMD_CLEAR_SESSION_TABLE_ENTRIES = 35  # 清空当前网络命名空间中的所有会话表项

    # 字符串 -> 数字 映射
    STR_TO_TYPE_MAP = {
        "CMD_USERSPACE_TO_KERNEL_UNSPEC": CMD_USERSPACE_TO_KERNEL_UNSPEC,
        "CMD_ECHO": CMD_ECHO,
        "CMD_SET_NODE_ID": CMD_SET_NODE_ID,
        "CMD_INIT_ROUTING_TABLE": CMD_INIT_ROUTING_TABLE,
        "CMD_INIT_INTERFACE_TABLE": CMD_INIT_INTERFACE_TABLE,
        "CMD_INIT_MULTIPATH_TABLE": CMD_INIT_MULTIPATH_TABLE,
        "CMD_INIT_SELIR": CMD_INIT_SELIR,
        "CMD_INIT_EPIC": CMD_INIT_EPIC,
        "CMD_INIT_BLOOM_FILTER": CMD_INIT_BLOOM_FILTER,
        "CMD_MODIFY_BLOOM_FILTER": CMD_MODIFY_BLOOM_FILTER,
        "CMD_INSERT_INTERFACE_TABLE_ENTRY": CMD_INSERT_INTERFACE_TABLE_ENTRY,
        "CMD_INSERT_ROUTING_TABLE_ENTRY": CMD_INSERT_ROUTING_TABLE_ENTRY,
        "CMD_SET_LIR_SINGLE_TIME_ENCODING_COUNT": CMD_SET_LIR_SINGLE_TIME_ENCODING_COUNT,
        "CMD_PRINT_ROUTING_TABLE_ENTRIES": CMD_PRINT_ROUTING_TABLE_ENTRIES,
        "CMD_SOURCE_INSERT_SEGMENT": CMD_SOURCE_INSERT_SEGMENT,
        "CMD_INTERMEDIATE_INSERT_SEGMENT": CMD_INTERMEDIATE_INSERT_SEGMENT,

        "CMD_INSERT_OUTPUT_LINK_IDENTIFIERS": CMD_INSERT_OUTPUT_LINK_IDENTIFIERS,
        "CMD_INSERT_RELATIONSHIP_BETWEEN_NEXT_NODE_ID_AND_PATHS": CMD_INSERT_RELATIONSHIP_BETWEEN_NEXT_NODE_ID_AND_PATHS,
        "CMD_SET_SEC_PATH_MAB_ROUTE": CMD_SET_SEC_PATH_MAB_ROUTE,
        "CMD_RESET_SEC_PATH_MAB_ROUTE": CMD_RESET_SEC_PATH_MAB_ROUTE,
        "CMD_SET_ROUTER_TYPE": CMD_SET_ROUTER_TYPE,
        "CMD_SET_MALICIOUS_PARAMS": CMD_SET_MALICIOUS_PARAMS,
        "CMD_RETRIEVE_KERNEL_INFORMATION": CMD_RETRIEVE_KERNEL_INFORMATION,
        "CMD_SET_SCHDULED_MALICIOUS_PARAMS": CMD_SET_SCHDULED_MALICIOUS_PARAMS,
        "CMD_SET_BEST_PATH_ID_FOR_SOURCE": CMD_SET_BEST_PATH_ID_FOR_SOURCE,
        "CMD_RETRIEVE_PER_PACKET_INFO": CMD_RETRIEVE_PER_PACKET_INFO,
        "CMD_SET_TOPOLOGY_INFORMATION": CMD_SET_TOPOLOGY_INFORMATION,
        "CMD_SET_EXPERIMENT_TYPE": CMD_SET_EXPERIMENT_TYPE,
        "CMD_INSERT_SESSION_TABLE_ENTRIES": CMD_INSERT_SESSION_TABLE_ENTRIES,
        "CMD_CLEAR_MULTIPATH_STATE": CMD_CLEAR_MULTIPATH_STATE,
        "CMD_CLEAR_SEGMENT_LIST": CMD_CLEAR_SEGMENT_LIST,
        "CMD_RESET_PROCESSING_TIME_STATISTICS": CMD_RESET_PROCESSING_TIME_STATISTICS,
        "CMD_RETRIEVE_PROCESSING_TIME_STATISTICS": CMD_RETRIEVE_PROCESSING_TIME_STATISTICS,
        "CMD_CLEAR_SESSION_TABLE_ENTRIES": CMD_CLEAR_SESSION_TABLE_ENTRIES,
    }

    # 数字 -> 字符串 映射
    TYPE_TO_STR_MAP = {
        CMD_USERSPACE_TO_KERNEL_UNSPEC: "CMD_USERSPACE_TO_KERNEL_UNSPEC",
        CMD_ECHO: "CMD_ECHO",
        CMD_SET_NODE_ID: "CMD_SET_NODE_ID",
        CMD_INIT_ROUTING_TABLE: "CMD_INIT_ROUTING_TABLE",
        CMD_INIT_INTERFACE_TABLE: "CMD_INIT_INTERFACE_TABLE",
        CMD_INIT_MULTIPATH_TABLE: "CMD_INIT_MULTIPATH_TABLE",
        CMD_INIT_SELIR: "CMD_INIT_SELIR",
        CMD_INIT_EPIC: "CMD_INIT_EPIC",
        CMD_INIT_BLOOM_FILTER: "CMD_INIT_BLOOM_FILTER",
        CMD_MODIFY_BLOOM_FILTER: "CMD_MODIFY_BLOOM_FILTER",
        CMD_INSERT_INTERFACE_TABLE_ENTRY: "CMD_INSERT_INTERFACE_TABLE_ENTRY",
        CMD_INSERT_ROUTING_TABLE_ENTRY: "CMD_INSERT_ROUTING_TABLE_ENTRY",
        CMD_SET_LIR_SINGLE_TIME_ENCODING_COUNT: "CMD_SET_LIR_SINGLE_TIME_ENCODING_COUNT",
        CMD_PRINT_ROUTING_TABLE_ENTRIES: "CMD_PRINT_ROUTING_TABLE_ENTRIES",
        CMD_SOURCE_INSERT_SEGMENT: "CMD_SOURCE_INSERT_SEGMENT",
        CMD_INTERMEDIATE_INSERT_SEGMENT: "CMD_INTERMEDIATE_INSERT_SEGMENT",

        CMD_INSERT_OUTPUT_LINK_IDENTIFIERS: "CMD_INSERT_OUTPUT_LINK_IDENTIFIERS",
        CMD_INSERT_RELATIONSHIP_BETWEEN_NEXT_NODE_ID_AND_PATHS: "CMD_INSERT_RELATIONSHIP_BETWEEN_NEXT_NODE_ID_AND_PATHS",
        CMD_SET_SEC_PATH_MAB_ROUTE: "CMD_SET_SEC_PATH_MAB_ROUTE",
        CMD_RESET_SEC_PATH_MAB_ROUTE: "CMD_RESET_SEC_PATH_MAB_ROUTE",
        CMD_SET_ROUTER_TYPE: "CMD_SET_ROUTER_TYPE",
        CMD_SET_MALICIOUS_PARAMS: "CMD_SET_MALICIOUS_PARAMS",
        CMD_RETRIEVE_KERNEL_INFORMATION: "CMD_RETRIEVE_KERNEL_INFORMATION",
        CMD_SET_SCHDULED_MALICIOUS_PARAMS: "CMD_SET_SCHDULED_MALICIOUS_PARAMS",
        CMD_SET_BEST_PATH_ID_FOR_SOURCE: "CMD_SET_BEST_PATH_ID_FOR_SOURCE",
        CMD_RETRIEVE_PER_PACKET_INFO: "CMD_RETRIEVE_PER_PACKET_INFO",
        CMD_SET_TOPOLOGY_INFORMATION: "CMD_SET_TOPOLOGY_INFORMATION",
        CMD_SET_EXPERIMENT_TYPE: "CMD_SET_EXPERIMENT_TYPE",
        CMD_INSERT_SESSION_TABLE_ENTRIES: "CMD_INSERT_SESSION_TABLE_ENTRIES",
        CMD_CLEAR_MULTIPATH_STATE: "CMD_CLEAR_MULTIPATH_STATE",
        CMD_CLEAR_SEGMENT_LIST: "CMD_CLEAR_SEGMENT_LIST",
        CMD_RESET_PROCESSING_TIME_STATISTICS: "CMD_RESET_PROCESSING_TIME_STATISTICS",
        CMD_RETRIEVE_PROCESSING_TIME_STATISTICS: "CMD_RETRIEVE_PROCESSING_TIME_STATISTICS",
        CMD_CLEAR_SESSION_TABLE_ENTRIES: "CMD_CLEAR_SESSION_TABLE_ENTRIES",
    }

    @classmethod
    def turn_str_into_type(cls, type_str: str) -> int:
        """字符串转换为 Netlink 消息类型数字"""
        if type_str not in cls.STR_TO_TYPE_MAP:
            raise ValueError(f"unsupported netlink message type: {type_str}")
        return cls.STR_TO_TYPE_MAP[type_str]

    @classmethod
    def turn_type_into_str(cls, type_int: int) -> str:
        """Netlink 消息类型数字转换为字符串"""
        if type_int not in cls.TYPE_TO_STR_MAP:
            raise ValueError(f"unsupported netlink message type: {type_int}")
        return cls.TYPE_TO_STR_MAP[type_int]
