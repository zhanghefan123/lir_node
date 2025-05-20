from modules.kernel import kernel_configurator as kcm
from modules.kernel import kernel_configurator_for_raspberrypi as kcrm


def load_lir_configuration():
    lir_config_loader = kcm.KernelConfigurator()
    lir_config_loader.start()


def raspberrypi_load_lir_configuration():
    lir_config_loader = kcrm.KernelConfiguratorForRsapberrypi()
    lir_config_loader.start()
