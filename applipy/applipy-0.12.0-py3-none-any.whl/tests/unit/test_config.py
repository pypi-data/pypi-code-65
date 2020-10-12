from applipy import Config
from applipy.config.protocol import ConfigProtocol


class Upper(ConfigProtocol):

    def provide_for(self, protocol, key):
        if protocol in ('up', 'upper'):
            return key.upper()

        return None


class Capitalize(ConfigProtocol):

    def provide_for(self, protocol, key):
        if protocol == 'cap':
            return key.capitalize()

        return None


def test_config():

    raw_config = {
            'app': {'name': 'config-test', 'priority': 40},
            'app.type': 5,
            'db.password.value': 'up:seCret',
            'db.password.is_secret': True,
            'name': {'of': {'process': 'cap:foo'}},
            'name.of.file': 'upper:unknown'
    }
    protocols = [Upper(), Capitalize()]
    config = Config(raw_config, protocols)

    assert config['app.name'] == 'config-test'
    assert config.get('app.priority') == 40
    assert config.get('app.type') == 5
    assert config.get('db.password.value') == 'SECRET'
    assert config.get('db.password.is_secret') is True
    assert config['name'].get('of.process') == 'Foo'
    assert config['name']['of.file'] == 'UNKNOWN'
    assert config.get('app.not-there', 69) == 69

    assert config.keys() == {'app.name', 'app.priority', 'app.type', 'db.password.value', 'db.password.is_secret',
                             'name.of.process', 'name.of.file'}
