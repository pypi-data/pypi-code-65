from setux.logger import debug
from setux.core.manage import ArgsChecker


class Distro(ArgsChecker):
    manager = 'groups'

    def get(self):
        ret, out, err = self.run(f'grep {self.key} /etc/group')
        groups = set()
        for line in out:
            name, x, gid, users = line.split(':')
            if self.key in users.split(','):
                groups.add(name)
        return groups

    def add(self, group, check=True):
        groups = self.get()
        if group not in groups:
            self.distro.group(group).set()
            groups.add(group)
            debug(f'groups add {self.key} to {group}')
            self.do_set(user=self.key, groups=groups, check=check)

    def rm(self, group, check=True):
        groups = self.get()
        if group in groups:
            groups.remove(group)
            debug(f'groups remove {self.key} from {group}')
            self.do_set(user=self.key, groups=groups, check=check)

    def do_set(self, *, user, groups, check):
        self.run(f'usermod --groups {",".join(groups)} {user}', check=check)


class FreeBSD(Distro):
    def do_set(self, *, user, groups, check):
        self.run(f'pw usermod -n {user} -G {",".join(groups)}', check=check)
