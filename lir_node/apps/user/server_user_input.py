import socket
import time

from PyInquirer import prompt
from apps.user import questions as qm


class ServerUserInput:
    def __init__(self):
        self.selected_listen_port = None
        self.selected_server_type = None
        self.start()

    def get_listen_port(self):
        return int(prompt(qm.QUESTION_FOR_LISTEN_PORT)["port"])

    def get_server_type(self):
        return prompt(qm.QUESTION_FOR_SERVER_TYPE)["type"]

    def start(self):
        self.selected_listen_port = self.get_listen_port()
        self.selected_server_type = self.get_server_type()
