import json
from flask_cors import *
from flask import Flask, request
from gevent.pywsgi import WSGIServer
from apps.user.client_detailed_info import ClientDetailedInfo
from apps.user.server_detailed_info import ServerDetailedInfo
from modules.config import env_loader as elm
from modules.online.check_event_thread.check_event_thread import CheckThread
from modules.online.entities import sim_normal_router as snrm
from modules.online.check_event_thread import scheduled_event as sem
from tools import json_response as jrm
from apps.transport.udp import udp_client as ucm
from apps.transport.udp import udp_server as usm
from datetime import datetime
from modules.kernel import kernel_configurator as kcm
from defined_types import types as tmm
from modules.online.steps import simulator as sm
from modules.online.steps import start_simulator as ssm
from defined_types import types as dtm
import time

flask_instance = Flask(__name__)


def start_flask_http_service():
    CORS(flask_instance, supports_credentials=True)  # CORS 应对措施
    listen_ip_address = "0.0.0.0"
    listen_port = int(elm.env_loader.listen_port)
    http_server = WSGIServer((listen_ip_address, listen_port), flask_instance)
    print("http server start successfully", flush=True)
    http_server.serve_forever()


def modify_bloom_filter_parameters_core(data):
    bf_effective_bits = data["bf_effective_bits"]
    lir_config_loader = kcm.KernelConfigurator()
    lir_config_loader.modify_bloom_filter(bf_effective_bits)


# 进行布隆过滤器参数的修改
@flask_instance.route("/modifyBloomFilter", methods=["POST"])
def flask_modify_bloom_filter_paramters():
    data = json.loads(request.data)

    modify_bloom_filter_parameters_core(data)

    response_data = {
        "status": "success"
    }
    return jrm.get_json_response_from_map(response_data, 200)


def start_client_core(data):
    client_detailed_info = ClientDetailedInfo()

    client_detailed_info.selected_network_layer = data["selected_network_layer"]
    client_detailed_info.destination_port = data["destination_port"]
    client_detailed_info.transmission_pattern = data["transmission_pattern"]

    client_detailed_info.file_size = data["file_size"]
    client_detailed_info.processes = data["processes"]
    client_detailed_info.buffer_size = data["buffer_size"]
    client_detailed_info.message_size = data["message_size"]
    client_detailed_info.batch_size = data["batch_size"]

    client_detailed_info.destinations = data["destinations"]
    client_detailed_info.content = data["content"]

    ucm.start_client(client_detailed_info)


@flask_instance.route("/startClient", methods=["POST"])
def flask_start_client():
    data = json.loads(request.data)

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("格式化时间:", current_time, flush=True)

    start_client_core(data)

    response_data = {
        "status": "success"
    }
    return jrm.get_json_response_from_map(response_data, 200)


def start_server_core(data):
    server_detailed_info = ServerDetailedInfo()
    server_detailed_info.number_of_processes = data["processes"]
    server_detailed_info.selected_network_layer = data["selected_network_layer"]
    server_detailed_info.selected_listen_port = data["listen_port"]
    server_detailed_info.selected_server_type = data["server_type"]
    server_detailed_info.interface_name = data["interface"]
    server_detailed_info.simulation_index = data["simulation_index"]
    server_detailed_info.number_of_destinations = data["number_of_destinations"]
    server_detailed_info.ip_version = data["ip_version"]

    usm.start_server(server_detailed_info)


@flask_instance.route("/startServer", methods=["POST"])
def flask_start_server():
    data = json.loads(request.data)

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("格式化时间:", current_time, flush=True)

    start_server_core(data)

    response_data = {
        "status": "success"
    }
    return jrm.get_json_response_from_map(response_data, 200)


def init_osmd_core(data):
    # 进行 simulator params 的设置
    simulator_params = sm.SimulatorParams()
    simulator_params.number_of_epochs = data["number_of_epochs"]
    simulator_params.number_of_pkts_per_link = data["number_of_pkts_per_link"]
    simulator_params.mini_batch_size = data["mini_batch_size"]
    simulator_params.learning_rate = data["learning_rate"]
    simulator_params.minimum_delivery_ratio = data["minimum_delivery_ratio"]
    simulator_params.enable_dade_algorithm = data["enable_dade_algorithm"]
    simulator_params.enable_deda_algorithm = data["enable_deda_algorithm"]
    simulator_params.min_ack_for_rtt_estimation = data["min_ack_for_rtt_estimation"]
    simulator_params.experiment_time_elapsed_ms = data["experiment_time_elapsed_ms"]

    # 进行 client detailed info 的设置
    client_detailed_info = ClientDetailedInfo()

    client_detailed_info.selected_network_layer = tmm.NetworkLayer.SEC_PATH_MAB
    client_detailed_info.transmission_pattern = tmm.TransmissionType.BATCH
    client_detailed_info.file_size = -1
    client_detailed_info.processes = 1
    client_detailed_info.buffer_size = 1024
    client_detailed_info.destination_port = data["destination_port"]
    client_detailed_info.destinations = data["destinations"]
    client_detailed_info.message_size = data["message_size"]

    client_detailed_info.interval = data["packet_sending_interval"]
    client_detailed_info.content = ""

    simulation_graph_path = f"/configuration/{elm.env_loader.container_name}/topology/sec_path_mab_topology.json"

    # 进行 osmd 的启动
    ssm.init_by_http(simulator_params=simulator_params,
                     client_detailed_info=client_detailed_info,
                     simulation_graph_path=simulation_graph_path)


@flask_instance.route("/initOsmd", methods=["POST"])
def flask_init_osmd():
    data = json.loads(request.data)

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("格式化时间:", current_time)

    init_osmd_core(data)

    response_data = {
        "status": "success"
    }

    return jrm.get_json_response_from_map(response_data, 200)


def start_osmd_core():
    ssm.start_by_http()


@flask_instance.route("/startOsmd", methods=["POST"])
def flask_start_osmd():
    start_osmd_core()

    response_data = {
        "status": "success"
    }

    return jrm.get_json_response_from_map(response_data, 200)


def start_retrieve_acks_core():
    if sm.simulator_instance is None:
        print("simulator_instance is none", flush=True)
    else:
        if elm.env_loader.sec_path_mab_type == dtm.SecPathMabType.SEC_PATH_MAB_STRATEGY_FIXED_BATCH:
            epoch_id, sending_time_elapsed, received_ack_counts, expected_ack_counts, retrieved = kcm.kernel_config_loader.retrieve_kernel_information_for_fixed_batch()
            if retrieved:
                print(f"epoch_id: {epoch_id}, "
                      f"sending_time_elapsed: {sending_time_elapsed}, "
                      f"received_ack_counts: {received_ack_counts}, "
                      f"expected_ack_counts: {expected_ack_counts}", flush=True)
            else:
                print("not retrieved", flush=True)
        else:
            epoch_id, collect_enough_acks_time_elapsed, reach_timeout_time_elapsed, current_epoch_sent_packets, received_ack_counts, expected_ack_counts, retrieved = kcm.kernel_config_loader.retrieve_kernel_information_for_dynamic_batch()
            if retrieved:
                print(f"epoch_id: {epoch_id}, "
                      f"collect_enough_acks_time_elapsed: {collect_enough_acks_time_elapsed}, "
                      f"sending_time_elapsed: {reach_timeout_time_elapsed}, "
                      f"current_epoch_sent_packets: {current_epoch_sent_packets}, "
                      f"received_ack_counts: {received_ack_counts}, "
                      f"expected_ack_counts: {expected_ack_counts}",
                      flush=True)
            else:
                print("not retrieved", flush=True)


@flask_instance.route("/startRetrieveAcks", methods=["POST"])
def flask_start_retrieve_acks():
    start_retrieve_acks_core()
    response_data = {
        "status": "success"
    }
    return jrm.get_json_response_from_map(response_data, 200)


def set_scheduled_malicious_params_core(data):
    employed_epoch_or_timestamp_ms = data["employed_epoch_or_timestamp_ms"]
    set_node_id = data["node_id"]
    corrupt_ratio_start = data["corrupt_ratio_start"]
    corrupt_ratio_end = data["corrupt_ratio_end"]
    corrupt_special_packet_ratio_start = data["corrupt_special_packet_ratio_start"]
    corrupt_special_packet_ratio_end = data["corrupt_special_packet_ratio_end"]
    if set_node_id == elm.env_loader.node_id:
        scheduled_event = sem.ScheduledEvent(set_node_id, None, employed_epoch_or_timestamp_ms, corrupt_ratio_start,
                                             corrupt_ratio_end,
                                             corrupt_special_packet_ratio_start, corrupt_special_packet_ratio_end)
        print(f"set scheduled malicious params for normal router: {corrupt_ratio_start},{corrupt_ratio_end},"
              f"{corrupt_special_packet_ratio_start},{corrupt_special_packet_ratio_end} "
              f"at employed_epoch_or_timestamp_ms = {employed_epoch_or_timestamp_ms}", flush=True)

    elif 1 == elm.env_loader.node_id:
        normal_router = sm.simulator_instance.sim_graph.sim_abstract_nodes_mapping[
            f"NormalRouter-{set_node_id}"].actual_node
        if isinstance(normal_router, snrm.SimNormalRouter):
            scheduled_event = sem.ScheduledEvent(set_node_id, normal_router, employed_epoch_or_timestamp_ms, corrupt_ratio_start, corrupt_ratio_end,
                                                 corrupt_special_packet_ratio_start, corrupt_special_packet_ratio_end)
            print(f"set scheduled malicious params for source: {corrupt_ratio_start},{corrupt_ratio_end},"
                  f"{corrupt_special_packet_ratio_start},{corrupt_special_packet_ratio_end}", flush=True)
        else:
            raise RuntimeError("could not resolve scheduled malicious params")
    else:
        raise RuntimeError("could not resolve scheduled malicious params")
    # 源节点插入 event (为了查出最优路径), 其他节点插入 event (为了进行 corrupt ratio 的设置)
    sm.simulator_instance.scheduled_event_list.append(scheduled_event)


@flask_instance.route("/setSchduledMaliciousParams", methods=["POST"])
def set_scheduled_malicious_params():
    data = json.loads(request.data)
    set_scheduled_malicious_params_core(data)
    response_data = {
        "status": "success"
    }
    return jrm.get_json_response_from_map(response_data, 200)


@flask_instance.route("/startSync", methods=["POST"])
def start_sync():
    start_sync_core()
    response_data = {
        "status": "success"
    }
    return jrm.get_json_response_from_map(response_data, 200)


def start_sync_core():
    sm.simulator_instance.sync_timestamp = time.time()
    sm.simulator_instance.check_thread = CheckThread()
    sm.simulator_instance.check_thread.start()
