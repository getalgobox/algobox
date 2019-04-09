import os
import service_api

class Config(object):
    # global configuration settings here, apply to all environments
    pass

class Development(Config):
        datastore_interface = "marketstore"

class Production(Config):
    pass


env = os.getenv("ALGOBOX_ENVIRONMENT", default="DEVELOPMENT")

config_map = {
    "DEVELOPMENT": Development(),
    "PRODUCTION": Production()
}

Config = config_map[env]
