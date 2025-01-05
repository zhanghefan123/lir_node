if __name__ == "__main__":
    import sys
    sys.path.append("../../")

from tools.network.interface_rate import get_interface_names
from PyInquirer import prompt
from apps.user import questions as qm


class ServerUserInput:
    def __init__(self):
        self.selected_listen_port = None
        self.selected_server_type = None
        self.selected_interface_name = None
        self.start()

    def get_listen_port(self):
        return int(prompt(qm.QUESTION_FOR_LISTEN_PORT)["port"])

    def get_server_type(self):
        return prompt(qm.QUESTION_FOR_SERVER_TYPE)["type"]

    def get_interface(self):
        question = qm.QUESTION_FOR_INTERFACE_NAME
        question[0]["choices"] = get_interface_names()
        return prompt(question)["interface"]

    def start(self):
        self.selected_listen_port = self.get_listen_port()
        self.selected_server_type = self.get_server_type()
        self.selected_interface_name = self.get_interface()


if __name__ == "__main__":
    server_user_input = ServerUserInput()
    print(server_user_input.selected_listen_port)
    print(server_user_input.selected_server_type)
    print(server_user_input.selected_interface_name)
    print("done")