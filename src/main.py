from module.core.factory import CoreFactory

if __name__ == "__main__":
    coreFactory = CoreFactory()
    app = coreFactory.get_facade()
    app.run()