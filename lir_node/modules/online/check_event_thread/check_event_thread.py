import time
import threading
from datetime import datetime
from modules.online.steps import simulator as sm
from modules.online.steps import osmd_step as osm
from modules.config import env_loader as elm
from modules.kernel import kernel_configurator as kcm


class CheckThread(threading.Thread):
    def __init__(self, timestamp: datetime):
        super().__init__()
        self.timestamp = timestamp

    def _current_time_ms(self) -> float:
        return time.time() * 1000

    def _event_deadline_ms(self, scheduled_event) -> float:
        return sm.simulator_instance.sync_timestamp + scheduled_event.employed_epoch_or_timestamp_ms

    def _handle_event(self, scheduled_event):
        if elm.env_loader.node_id == 1:
            if not scheduled_event.params_changed():
                return
            scheduled_event.execute()
            best_path = osm.recalculate_score_and_find_best_path(sm.simulator_instance)
            if sm.simulator_instance.packet_best_path_id == best_path.path_id:
                return
            kcm.kernel_config_loader.set_best_path_id_and_regret_values_for_source(
                best_path_id=best_path.path_id,
                regret_values=[item.regret_value for item in
                               sm.simulator_instance.sim_graph.available_paths])
            sm.simulator_instance.packet_best_path_id = best_path.path_id
            print(
                f"set best path for source = {sm.simulator_instance.packet_best_path_id} at timestamp: {scheduled_event.employed_epoch_or_timestamp_ms}",
                flush=True)
        else:
            kcm.kernel_config_loader.set_malicious_params_from_event(scheduled_event)
            print(
                f"set malicious params for normal router {elm.env_loader.node_id} at timestamp: {scheduled_event.employed_epoch_or_timestamp_ms}",
                flush=True)

    def _process_due_events(self):
        while True:
            with sm.simulator_instance.scheduled_event_lock:
                if not sm.simulator_instance.has_scheduled_events():
                    return
                next_event = sm.simulator_instance.peek_scheduled_event()
                if self._current_time_ms() < self._event_deadline_ms(next_event):
                    return
                scheduled_event = sm.simulator_instance.pop_scheduled_event()
            self._handle_event(scheduled_event)

    def run(self):
        print("start timestamp level thread", flush=True)
        while True:
            with sm.simulator_instance.scheduled_event_lock:
                if not sm.simulator_instance.has_scheduled_events():
                    break
                next_deadline_ms = self._event_deadline_ms(sm.simulator_instance.peek_scheduled_event())

            if self._current_time_ms() >= next_deadline_ms:
                self._process_due_events()
                continue

            time.sleep((next_deadline_ms - self._current_time_ms()) / 1000.0)

        print("end timestamp level thread", flush=True)
