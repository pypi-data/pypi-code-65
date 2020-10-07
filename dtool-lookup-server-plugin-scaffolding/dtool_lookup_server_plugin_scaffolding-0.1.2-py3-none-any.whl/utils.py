from .config import Config

def config_to_dict(username):
    # TODO: check on privileges
    return Config.to_dict()
