
from cement import Controller, ex
from cement.utils.version import get_version_banner
from ..core.version import get_version

VERSION_BANNER = """
Codario CLI tool. %s
%s
""" % (get_version(), get_version_banner())


class Base(Controller):
    class Meta:
        label = 'base'

        # text displayed at the top of --help output
        description = 'Codario CLI tool.'

        # text displayed at the bottom of --help output
        epilog = '''Usage: codario cmd --foo bar

Instead "--key" argument you can use ENV variable "CODARIO_API_KEY".'''

        # controller level arguments. ex: 'codario --version'
        arguments = [
            ### add a version banner
            ( [ '-v', '--version' ],
              { 'action'  : 'version',
                'version' : VERSION_BANNER } ),
        ]


    def _default(self):
        """Default action if no sub-command is passed."""

        self.app.args.print_help()

