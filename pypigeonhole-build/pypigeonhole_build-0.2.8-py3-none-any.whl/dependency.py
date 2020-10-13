from dataclasses import dataclass, field

INSTALL = 'INSTALL'
DEV = 'DEV'


@dataclass
class Installer:
    name: str
    env: str = None
    channels: list = field(default_factory=list)


# This means we lean on pip since we know pip. We are supposed to be neutral.
# This is for convenient usage, default to PIP.
PIP = Installer(name='PIP')


@dataclass
class Dependency:
    name: str
    version: str = ''
    url: str = None
    scope: str = DEV
    installer: Installer = PIP
    desc: str = None
