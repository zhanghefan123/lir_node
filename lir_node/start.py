from modules.http_service import http_service as hsm
from modules.frr import frr_manager as fmm
from signal_decorator import exit_signal_listener
from modules.lir import lir_config_loader as lclm

flask_process = None


class Starter:
    def __init__(self):
        pass

    @exit_signal_listener.signal_decorator
    def main_logic(self):
        """
        主逻辑
            1. 启动 frr
            2. 启动 无限循环
        :return:
        """
        fmm.start_frr()
        lclm.load_lir_configuration()
        hsm.start_flask_http_service()  # 这是一个死循环


if __name__ == "__main__":
    starter = Starter()
    starter.main_logic()
