def get_interfaces_data():
    dev = {}
    with open('/proc/net/dev', 'r') as f:
        for line in f:
            if ':' in line:
                line = line.split(':')
                if_name = line[0].strip()
                line = line[1].split()
                if if_name == "lo":
                    continue
                dev[if_name] = {
                    'rx_bytes': int(line[0]),
                    'rx_packets': int(line[1]),
                    'rx_errors': int(line[2]),
                    'rx_dropped': int(line[3]),
                    'rx_fifo': int(line[4]),
                    'rx_frame': int(line[5]),
                    'rx_compressed': int(line[6]),
                    'rx_multicast': int(line[7]),
                    'tx_bytes': int(line[8]),
                    'tx_packets': int(line[9]),
                    'tx_errors': int(line[10]),
                    'tx_dropped': int(line[11]),
                    'tx_fifo': int(line[12]),
                    'tx_collisions': int(line[13]),
                    'tx_carrier': int(line[14]),
                    'tx_compressed': int(line[15])
                }
    return dev


def get_interface_rx_bytes(interface_name: str):
    """
    返回某个接口接收的字节数
    """
    dev = get_interfaces_data()
    return dev[interface_name]['rx_bytes']


def get_interface_names():
    """
    返回所有接口名称
    """
    return get_interfaces_data().keys()
