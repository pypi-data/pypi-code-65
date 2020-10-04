import logging

from cliff.command import Command
from balic import Balic


class Hosts(Command):

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        """Add or update /etc/hosts entry for given site.
        """
        self.balic = Balic(parsed_args.name)
        self.balic.hosts(parsed_args.site)

    def get_description(self):
        return "add or update /etc/hosts entry for given container name and site"

    def get_parser(self, prog_name):
        parser = super(Hosts, self).get_parser(prog_name)
        parser.add_argument("-s", "--site", required=True)
        return Balic.get_parser(parser)
