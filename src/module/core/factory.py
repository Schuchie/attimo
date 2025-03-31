from module.core.facade import CoreFacade

def create_app() -> CoreFacade:
    #config = load_config()
    #display = create_display_facade(config)
    #image_provider = create_image_facade(config)
    return CoreFacade()