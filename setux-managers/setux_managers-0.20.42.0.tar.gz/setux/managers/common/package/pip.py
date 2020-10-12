from setux.logger import error, info
from setux.core.package import CommonPackager


# pylint: disable=no-member


class Distro(CommonPackager):
    manager = 'pip'

    def ls(self):
        ret, out, err = self.run('python3 -m pip list')
        for line in self.out:
            try:
                n, v = line.split()
                v = v.replace('(', '')
                v = v.replace(')', '')
                yield n, v
            except:
                error(line)

    def do_init(self):
        self.target.distro.Package.install('setuptools')
        self.target.distro.Package.install('pip')
        self.run(f'python3 -m pip install -qU pip')

    def do_install(self, pkg, ver=None):
        ret, out, err = self.run(f'python3 -m pip install -qU {pkg}')
        for o in out:
            if 'already satisfied' in o:
                break
            if 'Successfully installed' in o:
                info('\t--> %s %s', pkg, ver or '')
                break
        else:
            if any(line.strip() for line in out):
                error('\n'.join(out))

    def do_installed(self):
        for n, v in self.ls():
            yield n , v

    def do_available(self):
        for n, v in self.ls():
            yield n , v

    def do_remove(self, pkg):
        self.run(f'python3 -m pip uninstall -y {pkg}')

    def do_cleanup(self):
        pass

    def do_update(self):
        pass

