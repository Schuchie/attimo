class ConfigFactory:
    def __init__(self):
        pass
        
    def get_facade(self):
        if not hasattr(self, 'config_provider'):
            from module.config.business.provider import ConfigProvider
            self.config_provider = ConfigProvider({})
        if not hasattr(self, 'config_facade'):
            from module.config.facade import ConfigFacade
            self.config_facade = ConfigFacade(self.config_provider)
        
        return self.config_facade