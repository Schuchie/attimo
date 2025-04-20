from pathlib import Path
from module.config.provider import ConfigProvider
from module.image_provider.provider import ImageProvider
from module.user_interface.provider import UiProvider

if __name__ == "__main__":

    main_dir = Path(__file__).parent.parent
    config_provider = ConfigProvider(main_dir / "resource" / "config" / "settings.yaml")
    image_provider = ImageProvider(main_dir, config_provider)
    ui_provider = UiProvider(main_dir, config_provider, image_provider)
    ui_provider.run()