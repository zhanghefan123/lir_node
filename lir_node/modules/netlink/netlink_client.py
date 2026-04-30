from pyroute2.netlink import NLM_F_REQUEST, genlmsg
from pyroute2.netlink.generic import GenericNetlinkSocket
from defined_types import types as tm

if __name__ == "__main__":
    import sys

    sys.path.append("../../")

VERSION_NR = 1


class NetlinkMessageFormat(genlmsg):
    nla_map = (
        ('RLINK_ATTR_UNSPEC', 'none'),
        ('RLINK_ATTR_DATA', 'asciiz'),
        ('RLINK_ATTR_LEN', 'uint32'),
    )


class NetlinkClient(GenericNetlinkSocket):
    def __init__(self):
        super().__init__()
        self.bind("EXMPL_GENL", NetlinkMessageFormat)

    def send_netlink_data(self, data: str, message_type: int):
        """
        进行 netlink 数据的发送
        :param data: 数据
        :param message_type: 消息类型
        :return:
        """
        # print(f"---------SEND NETLINK MSG (type == {tm.NetlinkMessageType.turn_type_into_str(message_type)}) TO KERNEL----------", flush=True)
        # send netlink message
        message = NetlinkMessageFormat()
        message["cmd"] = message_type
        message["version"] = VERSION_NR
        message["attrs"] = [("RLINK_ATTR_DATA", data)]
        # print(f"send message = {data}", flush=True)
        kernel_response = self.nlm_request(message, self.prid, msg_flags=NLM_F_REQUEST)
        # analyze response
        response_data = kernel_response[0]
        attr_data = response_data.get_attr('RLINK_ATTR_DATA')
        # print(f"response data = {attr_data}", flush=True)
        # print(f"---------SEND NETLINK MSG (type == {tm.NetlinkMessageType.turn_type_into_str(message_type)}) TO KERNEL----------", flush=True)
        # print(f"", flush=True)
        return attr_data


if __name__ == "__main__":
    netlink_client = NetlinkClient()
    while True:
        netlink_message_type_str_tmp = input("please input input message type: [1. ECHO] [q or quit to exit]:")
        if "q" == netlink_message_type_str_tmp or "quit" == netlink_message_type_str_tmp:
            break
        else:
            netlink_message_type = tm.NetlinkMessageType.turn_str_into_type(netlink_message_type_str_tmp)
            data_tmp = input("please input message you want to send:")
            netlink_client.send_netlink_data(data_tmp, netlink_message_type)
