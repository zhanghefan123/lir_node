class NetworkLayer:
    SRV6 = 3
    IP = 4
    LIR = 5
    ICING = 7
    OPT = 8
    SELIR = 11
    FAST_SELIR = 12
    MULTICAST_SELIR = 13
    EPIC_SESSION_SETUP = 16 # 这个要看内核之中的值是多少
    EPIC_DATA = 17


class RoutingTableType:
    ARRAY_BASED_ROUTING_TABLE_TYPE = 1
    HASH_BASED_ROUTING_TABLE_TYPE = 2
