from PyInquirer import prompt

from apps.user import questions as qm
from apps.types import types as tm
from modules.config import name_to_ip_mapping_loader as ntimlm
from modules.config import env_loader as elm


class UserInput:
    def __init__(self):
        self.selected_network_layer = None
        self.selected_destination_port = None
        self.name_to_ip_mapping = None
        self.selected_destination_name = None
        self.selected_destination_ip = None
        self.start()

    def get_network_layer(self):
        answers_for_protocol = prompt(qm.QUESTION_FOR_PROTOCOL)["protocol"]
        if answers_for_protocol == "IP":
            self.selected_network_layer = tm.NetworkLayer.IP
        elif answers_for_protocol == "LIR":
            self.selected_network_layer = tm.NetworkLayer.LiR
        else:
            raise Exception("unsupported network type")

    def get_destination_port(self):
        answers_for_destination_port = prompt(qm.QUESTION_FOR_DESTINATION_PORT)["port"]
        self.selected_destination_port = int(answers_for_destination_port)

    def select_destination_node(self):
        question_for_destination_node = qm.QUESTION_FOR_DESTINATION
        question_for_destination_node[0]["choices"] = list(self.name_to_ip_mapping.keys())
        self.selected_destination_name = prompt(question_for_destination_node)["destination"]
        self.selected_destination_ip = self.name_to_ip_mapping[self.selected_destination_name]

    def start(self):
        self.get_destination_port()
        self.get_network_layer()
        if self.selected_network_layer == tm.NetworkLayer.IP:
            file_path = f"/configuration/{elm.env_loader.container_name}/address_mapping.conf"
            self.name_to_ip_mapping = ntimlm.NameToIdMappingLoader(file_path=file_path)
            self.select_destination_node()
        elif self.selected_network_layer == tm.NetworkLayer.LiR:
            pass

