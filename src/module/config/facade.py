from module.config.business.provider import ConfigProvider

class ConfigFacade:
    def __init__(self, config_provider: ConfigProvider):
        self.config_provider = config_provider


    def load_config(self, config_path):
        """
        Load config from config dir settings.yaml
        :param config_path: The path to the config file
        :return: None
        """
        self.config_provider.load_config(config_path)

    def get_config(self, key):
        """
        Load config from config dir settings.yaml
        :param key: The key to retrieve from the config
        :return: The value associated with the key
        """
        return self.config_provider.get_config(key)
    