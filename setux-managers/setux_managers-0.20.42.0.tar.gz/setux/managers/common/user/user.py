from setux.logger import debug
from setux.core.manage import SpecChecker


class Distro(SpecChecker):
    manager = 'user'

    def get(self):
        user = self.key if self.key else self.spec['uid']
        ret, out, err = self.run(f'grep ^{user}: /etc/passwd')
        for line in out:
            name, x, uid, gid, rem, home, shell = line.split(':')
            if self.key:
                if name != self.key: continue
            else:
                if int(uid) != self.spec['uid']: continue
            return dict(
                name = name,
                uid = int(uid),
                gid = int(gid),
                home = home,
                shell = shell,
            )

    @property
    def group(self):
        return self.distro.group(
            self.key,
            gid = self.spec.get('gid')
        )

    @property
    def home(self):
        spec = self.get()
        home = self.distro.dir(
            spec['home'],
            user = spec['name'],
            group = self.group.name,
        )
        return home

    def chk(self, name, value, spec):
        if name=='home':
            return self.home.check()
        return value == spec

    def cre(self, check=True):
        debug(f'user create {self.key}')
        self.do_cre(user=self.key, check=check)
        self.home.set()

    def mod(self, key, val, check=True):
        debug(f'user {self.key} change {key} -> {val}')
        if key=='gid':
            self.distro.group(self.key, gid=val).set()
        if key=='home':
            self.home.set()
        self.do_mod(user=self.key, key=key, val=val, check=check)

    def rm(self, check=True):
        debug(f'user delete {self.key}')
        self.do_rm(user=self.key, check=check)

    def do_cre(self, *, user, check):
        self.run(f'useradd {user}', check=check)

    def do_mod(self, *, user, key, val, check):
        self.run(f'usermod --{key} {val} {user}', check=check)

    def do_rm(self, *, user, check):
        self.run(f'userdel -r {user}', check=check)


class FreeBSD(Distro):
    opts = dict(
        uid = 'u',
        gid = 'g',
        shell= 's',
        home= 'd',
    )

    def do_cre(self, *, user, check):
        self.run(f'pw useradd -n {user}', check=check)

    def do_mod(self, *, user, key, val, check):
        opt = self.opts[key]
        self.run(f'pw usermod -n {user} -{opt} {val}', check=check)

    def do_rm(self, *, user, check):
        self.run(f'pw userdel -n {user} -r', check=check)

