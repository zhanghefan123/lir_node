from modules.online.entities import sim_graph as sgm
from modules.online.steps import simulator as sem
INIT_GRAPH_FROM_CONFIGURATION_FILE = "InitGraphFromConfigurationFile"


def initialize(sm: sem.Simulator):
    init_graph_from_configuration_file(sm)


def init_graph_from_configuration_file(sm: sem.Simulator):
    """从配置文件中初始化图"""
    # 判断是否已经初始化过 (simulator_init_steps 是一个 set)
    if INIT_GRAPH_FROM_CONFIGURATION_FILE in sm.simulator_init_steps:
        # 假设 simulator_logger 已经定义
        # simulator_logger.info("already initialized graph from configuration file, skip this step")
        print("already initialized graph from configuration file, skip this step")
        return

    sm.sim_graph = sgm.SimGraph(sm.running_type)  # 假设导入了 SimGraph 类

    try:
        # step1: load graph params
        print("step 1: load_graph_params_from_configuration_file", flush=True)
        sm.sim_graph.load_graph_params_from_configuration_file(sm.simulation_graph_path)
    except Exception as e:
        raise RuntimeError(f"init graph from configuration file failed, {e}")

    try:
        # step2: load nodes
        print("step 2: load_nodes_from_node_params start", flush=True)
        sm.sim_graph.load_nodes_from_node_params()
    except Exception as e:
        raise RuntimeError(f"init graph nodes from configuration file failed, {e}")

    try:
        # step3: load source and destination
        print("step 3: load_source_and_dest", flush=True)
        sm.sim_graph.load_source_and_dest()
    except Exception as e:
        raise RuntimeError(f"load source and destination from configuration file failed, {e}")

    try:
        # step4 : load access links and pv links
        print("step 4: load_access_links_and_pv_links_params", flush=True)
        sm.sim_graph.load_access_links_and_pv_links_params()
    except Exception as e:
        raise RuntimeError(f"load pvLinks from configuration file failed, {e}")

    try:
        # step5: load real links
        print("step 5: load_real_links_from_link_params", flush=True)
        sm.sim_graph.load_real_links_from_link_params()
    except Exception as e:
        raise RuntimeError(f"init graph links from configuration file failed, {e}")

    try:
        # step6: load link identifiers
        print("step 6: load_link_identifiers", flush=True)
        sm.sim_graph.load_link_identifiers()
    except Exception as e:
        raise RuntimeError(f"load link identifiers failed, {e}")

    try:
        # step 7 calculate available paths
        print("step 7: calculate_available_paths", flush=True)
        sm.sim_graph.calculate_available_paths()
    except Exception as e:
        raise RuntimeError(f"calculate all available paths failed, {e}")

    try:
        # step8: 进行拓扑排序
        print("step 8: topology_sort", flush=True)
        sm.sim_graph.topology_sort()
    except Exception as e:
        raise RuntimeError(f"topology sort failed due to: {e}")

    # 标记该步骤已完成
    sm.simulator_init_steps.add(INIT_GRAPH_FROM_CONFIGURATION_FILE)
