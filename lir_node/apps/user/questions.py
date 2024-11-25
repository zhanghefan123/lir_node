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


QUESTION_FOR_DESTINATION = [
    {
        "type": "list",
        "name": "destination",
        "message": "请选择目的节点: "
    }
]