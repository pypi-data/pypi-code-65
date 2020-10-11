import libvirt
import textwrap

from enough import settings
from enough.common.retry import retry
from enough.common.dotenough import Hosts

log = logging.getLogger(__name__)


class Libvirt(object):

    EXTERNAL_NETWORK = 'enough-external'
    EXTERNAL_NETWORK_PREFIX = '10.23.10'
    INTERNAL_NETWORK = 'enough-internal'
    INTERNAL_NETWORK_PREFIX = '10.23.90'

    def __init__(self, config_dir, **kwargs):
        self.args = kwargs
        self.config_dir = config_dir
        self.l = libvirt.open('qemu:///system')

    def get_stack_definitions(self, share_dir=settings.SHARE_DIR):
        args = ['-i', f'{share_dir}/inventory',
                '-i', f'{self.config_dir}/inventory']
        if self.args.get('inventory'):
            args.extend([f'--inventory={i}' for i in self.args['inventory']])
        args.extend(['--vars', '--list'])
        password_file = f'{self.config_dir}.pass'
        if os.path.exists(password_file):
            args.extend(['--vault-password-file', password_file])
        r = sh.ansible_inventory(*args)
        inventory = json.loads(r.stdout)
        return inventory['_meta']['hostvars']

    def get_stack_definition(self, host):
        h = self.get_stack_definitions()[host]
        if h.get('network_internal_only', False):
            network_interface_unconfigured = h.get('network_primary_interface', 'eth0')
            network_interface_routed = h.get('network_secondary_interface', 'eth1')
            network_interface_not_routed = 'noname'
        else:
            network_interface_unconfigured = 'noname'
            network_interface_routed = h.get('network_primary_interface', 'eth0')
            network_interface_not_routed = h.get('network_secondary_interface', 'eth1')
        definition = {
            'name': host,
            'port': h.get('ansible_port', '22'),
            'network': h.get('libvirt_network', Libvirt.EXTERNAL_NETWORK),
            'network_prefix': h.get('libvirt_network_prefix', Libvirt.EXTERNAL_NETWORK_PREFIX),
            'network_internal_only': h.get('network_internal_only', False),
            'network_interface_unconfigured': network_interface_unconfigured,
            'network_interface_routed': network_interface_routed,
            'network_interface_not_routed': network_interface_not_routed,
            'internal_network': h.get('libvirt_network_internal', Libvirt.INTERNAL_NETWORK),
            'internal_network_prefix': h.get('libvirt_network_internal_prefix', Libvirt.INTERNAL_NETWORK_PREFIX),
        }
        if 'openstack_volumes' in h:
            definition['volumes'] = h['openstack_volumes']
        return definition

    def create_network(self, name, prefix):
        if name not in self.l.listNetworks():
            definition = textwrap.dedent(f"""
            <network>
              <name>{name}</name>
              <forward mode='nat'/>
              <bridge name='virbr{name}' stp='on' delay='0'/>
              <ip address='{prefix}.1' netmask='255.255.255.0'>
                <dhcp>
                  <range start='{prefix}.2' end='{prefix}.254'/>
                </dhcp>
              </ip>
            </network>
            """)
            network = self.l.networkDefineXML(network)
            network.create()
            network.autostart()
        else:
            network = self.l.networkLookupByName(name)
        return network

    def destroy_network(self, name):
        if name in self.l.listNetworks():
            self.l.networkLookupByName(network).destroy()
            return True
        else:
            return False

    def destroy_everything(self, prefix):
        for network in self.l.listNetworks():
            if prefix in network:
                self.destroy_network(name)

