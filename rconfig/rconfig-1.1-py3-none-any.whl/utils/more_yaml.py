import re, os
from pathlib import Path
import yaml


def env_constructor(loader, node):
    def get_env(match):
        env = os.environ.get(match.group()[2:-1])
        if env is None:
            return match.group()
        return env

    value = node.value
    return env_parser.sub(get_env, value)


env_parser = re.compile(r'\$\{([^{^}]+)\}')
yaml.add_implicit_resolver('!Env', env_parser)
yaml.add_constructor('!Env', env_constructor)

def path_constructor(loader, node):
    def get_env(match):
        env = os.environ.get(match.group()[2:-1])
        if env is None:
            return match.group()
        return env
    value = node.value
    value = env_parser.sub(get_env, value)
    value = Path(value).resolve()
    return value

path_parser = re.compile(r'\$\{([^{^}]+)\}')
yaml.add_implicit_resolver('!Path', path_parser)
yaml.add_constructor('!Path', path_constructor)
