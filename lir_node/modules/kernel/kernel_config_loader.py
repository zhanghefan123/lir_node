from modules.kernel import kernel_configurator as kcm


def load_lir_configuration():
    lir_config_loader = kcm.KernelConfigurator()
    lir_config_loader.start()
