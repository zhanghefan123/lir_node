QUESTION_FOR_PROTOCOL = [
    {
        "type": "list",
        "name": "protocol",
        "message": "请输入要使用的网络层协议: ",
        "choices": ["IP", "LIR"]
    }
]

QUESTION_FOR_DESTINATION_PORT = [
    {
        "type": "input",
        "name": "port",
        "message": "请输入目的端口: ",
        "default": "31313"
    }
]


QUESTION_FOR_LISTEN_PORT = [
    {
        "type": "input",
        "name": "port",
        "message": "请输入监听端口: ",
        "default": "31313"
    }
]

QUESTION_FOR_SERVER_TYPE = [
    {
        "type": "list",
        "name": "type",
        "message": "请输入服务器类型:",
        "choices": ["text", "file"]
    }
]

QUESTION_FOR_DESTINATION = [
    {
        "type": "list",
        "name": "destination",
        "message": "请选择目的节点: "
    }
]

QUESTION_FOR_DESTINATION_COUNT = [
    {
        "type": "input",
        "name": "count",
        "message": "请输入目的的数量: ",
        "default": "1",
    }
]

QUESTION_FOR_PACKET_TRANSMISSION_PATTERN = [
    {
        "type": "list",
        "name": "pattern",
        "message": "请选择三种发送模式之中的一种 [single] [batch] [file] [quit to exit]:",
        "choices": ["single", "batch", "file", "quit"]
    }
]

QUESTION_FOR_BATCH_SIZE = [
    {
        "type": "input",
        "name": "count",
        "message": "请输入单个批次要发送的消息的数量: ",
        "default": "500"
    }
]


QUESTION_FOR_MESSAGE_SIZE = [
    {
        "type": "input",
        "name": "count",
        "message": "请输入单个消息的字节数: ",
        "default": "100"
    }
]


QUESTION_FOR_SEND_INTERVAL = [
    {
        "type": "input",
        "name": "interval",
        "message": "请输入想要发送消息的时间间隔: ",
        "default": "0.01"
    }
]

QUESTION_FOR_FILE_SIZE = [
    {
        "type": "input",
        "name": "count",
        "message": "请输入要发送文件的大小 (字节): ",
        "default": "100"
    }
]
