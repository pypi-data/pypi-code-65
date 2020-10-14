from pathlib import Path
from dataclasses import dataclass

from .process import Process
from markipy import DEFAULT_LOG_PATH

_rsync_ = {'class': 'Rsync', 'version': 2}


@dataclass
class Host:
    user: str = ''
    ip: str = ''
    path: Path = ''
    remote: bool = False

    def __str__(self):
        if self.remote:
            return f'{self.user}@{self.ip}:{self.path}'
        else:
            return f'{self.path}'


class RsyncErrorSourceOrDestinationIsNone(Exception):
    def __init__(self, rsync):
        rsync.log.error('Check source of destination!')


class RsyncErrorOnlyOneCanBeRemote(Exception):
    def __init__(self, rsync):
        rsync.log.error('Only one from source or destination can be remote!')


class Rsync(Process):

    def __init__(self, source=None, destination=None, console=False, file_log=f'Rsync', log_path=DEFAULT_LOG_PATH):
        Process.__init__(self, console=console, file_log=file_log, log_path=log_path)
        self._init_atom_register_class(_rsync_)

        self.log.debug(self.ugrey(f'Initialized'))
        self.rsync_upload = ['rsync', '-avzh', '--info=flist2,name,progress2']
        self.rsync_check = ['rsync', '-avnc']

        self.source = source
        self.destination = destination

    def update_hosts(self, src, dst):
        self._check_input(src, dst)
        self.source = src
        self.destination = dst

    def sync(self):
        self.log.debug('Start sync')
        self.execute(self.rsync_upload + [f'{self.source}', f'{self.destination}'])
        self.log.debug('End sync')

    def control(self):
        self.log.debug('Start check')
        self.execute(self.rsync_check + [f'{self.source}', f'{self.destination}'])
        self.log.debug('End check')

    def _check_input(self, source, destination):
        if source and destination:
            if source.remote and destination.remote:
                raise RsyncErrorOnlyOneCanBeRemote(self)
        else:
            raise RsyncErrorSourceOrDestinationIsNone(self)



def test_rsync():
    source = Host(user='mark', ip='10.168.72.103', path=Path('/tmp/test/source/'), remote=False)
    destination = Host(user='mark', ip='10.168.72.103', path=Path('/tmp/test/destination/'), remote=True)
    rsync = Rsync(source, destination, console=True)
    rsync.check()
    rsync.sync()
    rsync.check()
