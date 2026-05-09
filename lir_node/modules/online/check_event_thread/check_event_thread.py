import time
import threading
from modules.online.steps import simulator as sm
from modules.online.steps import osmd_step as osm
from modules.config import env_loader as elm
from modules.kernel import kernel_configurator as kcm


class CheckThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            time_elapsed = (time.time() - sm.simulator_instance.sync_timestamp) * 1000
            for scheduled_event in sm.simulator_instance.scheduled_event_list:
                if scheduled_event.employed_epoch_or_timestamp_ms < time_elapsed:
                    scheduled_event = sm.simulator_instance.scheduled_event_list.pop(0)
                    if elm.env_loader.node_id == 1:  # 如果是源, 那么就进行最优路径的判断, 然后进行设置
                        scheduled_event.execute()
                        best_path = osm.recalculate_score_and_find_best_path(sm.simulator_instance)
                        if sm.simulator_instance.packet_best_path_id == best_path.path_id:
                            pass
                        else:
                            # kcm.kernel_config_loader.set_best_path_id_for_source(best_path_id=best_path.path_id)
                            sm.simulator_instance.packet_best_path_id = best_path.path_id
                            print(
                                f"set best path for source = {sm.simulator_instance.packet_best_path_id} at timestamp: {scheduled_event.employed_epoch_or_timestamp_ms}",
                                flush=True)
                    else:  # 如果不是源, 那么就进行设置
                        # kcm.kernel_config_loader.set_malicious_params_from_event(scheduled_event)
                        print(
                            f"set malicious params for normal router {scheduled_event} at timestamp: {scheduled_event.employed_epoch_or_timestamp_ms}",
                            flush=True)
            if len(sm.simulator_instance.scheduled_event_list) == 0:
                print("break here", flush=True)
                break
            time.sleep(1 / 1000.0)  # sleep for 10 ms
