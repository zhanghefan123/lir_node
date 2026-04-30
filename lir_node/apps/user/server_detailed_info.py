if __name__ == "__main__":
    import sys

    sys.path.append("../../")

from dataclasses import dataclass
from tools.network.interface_rate import get_interface_names
from PyInquirer import prompt
from apps.user import questions as qm
from defined_types import types as tm


@dataclass
class ServerDetailedInfo:
    selected_network_layer: int = -1
    number_of_processes: int = -1
    selected_listen_port: int = -1
    selected_server_type: int = -1
    selected_interface_name: str = ""
    selected_ip_version: int = -1
    # 这两个在用户键入的时候不需要填充
    simulation_index: int = -1
    number_of_destinations: int = -1

    def get_user_input(self):
        self.selected_network_layer = self.selected_network_layer if self.selected_network_layer != -1 else tm.NetworkLayer.turn_str_into_type(prompt(qm.QUESTION_FOR_PROTOCOL)["protocol"])
        self.number_of_processes = self.number_of_processes if self.number_of_processes != -1 else int(prompt(qm.QUESTION_FOR_NUMBER_OF_RECEIVING_PROCESSES)["processes"])
        self.selected_listen_port = self.selected_listen_port if self.selected_listen_port != -1 else int(prompt(qm.QUESTION_FOR_LISTEN_PORT)["port"])
        self.selected_server_type = self.selected_server_type if self.selected_server_type != -1 else tm.ServerType.turn_str_into_type(prompt(qm.QUESTION_FOR_SERVER_TYPE)["type"])
        question = qm.QUESTION_FOR_INTERFACE_NAME
        question[0]["choices"] = get_interface_names()
        self.selected_interface_name = self.selected_interface_name if self.selected_interface_name != "" else prompt(question)["interface"]
        self.selected_ip_version = self.selected_ip_version if self.selected_ip_version != -1 else tm.IpVersion.turn_str_into_type(prompt(qm.QUESTION_FOR_IP_VERSION)["version"])

