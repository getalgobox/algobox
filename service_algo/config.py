import os

class Config(object):
    # global configuration settings here, apply to all environments
    pass

class Development(Config):
    DB_CONNECT_STR = "postgresql://algobox:algobox@localhost:5432/algobox"


class Production(Config):
    pass


env = os.getenv("ALGOBOX_ENVIRONMENT", default="DEVELOPMENT")

config_map = {
    "DEVELOPMENT": Development(),
    "PRODUCTION": Production()
}

Config = config_map[env]
