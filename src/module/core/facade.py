from module.config.facade import ConfigFacade

class CoreFacade:
    def __init__(self, configFacade: ConfigFacade):
        self.configFacade = configFacade

    def run(self):
        #image_path = self.image_provider.get_next_image()
        #self.display.show_image(image_path)
        print("Load config...")
        self.configFacade.load_config("config/settings.yaml")
        print("Config loaded successfully.")

        print("🚀 App is running...")

        pass
