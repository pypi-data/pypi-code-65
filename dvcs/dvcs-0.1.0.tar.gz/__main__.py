# coding: utf-8

from __future__ import print_function, absolute_import, division, unicode_literals

import sys
import os                 # NOQA
# import argcomplete

from ruamel.std.argparse import ProgramBase, option, CountAction, \
    SmartFormatter, sub_parser, version  # , store_true, DateAction
from ruamel.appconfig import AppConfig
from .__init__ import __version__, _package_data


def to_stdout(*args):
    sys.stdout.write(' '.join(args))


class DvcsCmd(ProgramBase):
    def __init__(self):
        super(DvcsCmd, self).__init__(
            formatter_class=SmartFormatter,
            # aliases=True,
            # usage="""""",  # auto generated
            # description="""""",  # before options in help
            # epilog="""""",  # after options in help
            full_package_name=_package_data['full_package_name'],
        )

    # you can put these on __init__, but subclassing DvcsCmd
    # will cause that to break
    @option('--verbose', '-v',
            help='increase verbosity level', action=CountAction,
            const=1, nargs=0, default=0, global_option=True)
    @version('version: ' + __version__)
    def _pb_init(self):
        # special name for which attribs are included in help
        pass

    def run(self):
        from .dvcs import Dvcs
        self.dvcs = Dvcs(self._args, self._config)
        if hasattr(self._args, 'func'):  # not there if subparser selected
            return self._args.func()
        self._parse_args(['--help'])     # replace if you use not subparsers

    def parse_args(self):
        self._config = AppConfig(
            'dvcs',
            filename=AppConfig.check,
            parser=self._parser,  # sets --config option
            warning=to_stdout,
            add_save=False,  # add a --save-defaults (to config) option
        )
        # self._config._file_name can be handed to objects that need
        # to get other information from the configuration directory
        self._config.set_defaults()
        if len(sys.argv) > 1 and sys.argv[1] == '--version':
            self._version_information()
        # argcomplete.autocomplete(self._parser)
        self._parse_args(
            # default_sub_parser="",
        )

    @sub_parser(help='some command specific help')
    # @option('--session-name', default='abc')
    def show(self):
        # return self.redirect()
        pass

    def _version_information(self):
        version_data = [(_package_data['full_package_name'], __version__)]
        longest = len(version_data[0][0])
        if isinstance(_package_data['install_requires'], list):
            pkgs = _package_data['install_requires']
        else:
            pkgs = _package_data['install_requires'].get('any', [])
        for pkg in pkgs:
            try:
                version_data.append((pkg, sys.modules[pkg].__version__))
                longest = max(longest, len(pkg))
            except KeyError:
                pass
        for pkg, ver in version_data:
            print('{:{}s} {}'.format(pkg + ':', longest + 1, ver))
        sys.exit(0)

    def redirect(self, *args, **kw):
        """
        redirect to a method on self.develop, with the same name as the
        method name of calling method
        """
        return getattr(self.dvcs, sys._getframe(1).f_code.co_name)(*args, **kw)


def main():
    n = DvcsCmd()
    n.parse_args()
    sys.exit(n.run())


if __name__ == '__main__':
    main()
