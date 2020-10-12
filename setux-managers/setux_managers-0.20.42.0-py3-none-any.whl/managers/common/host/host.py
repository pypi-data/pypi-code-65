from pybrary.net import get_ip_adr
from pybrary.func import memo

from setux.core.manage import Manager


class Distro(Manager):
    manager = 'host'

    @property
    def name(self):
        attr = '_host_name_'
        try:
            val = getattr(self, attr)
        except AttributeError:
            ret, out, err = self.run('hostname')
            val = out[0]
            setattr(self, attr,  val)
        return val

    @name.setter
    def name(self, val):
        attr = '_host_name_'
        delattr(self, attr)
        ret, out, err = self.run(
            'hostname', val.replace('_', '')
        )
        return ret

    @memo
    def fqdn(self):
        ret, out, err = self.run('hostname -f')
        return out[0]

    @memo
    def addr(self):
        ok, adr = get_ip_adr()
        if ok:
            return adr
        else:
            debug(adr)
            return '!'

