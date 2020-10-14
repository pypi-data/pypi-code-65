import os
import sys
import glob
import argparse
import shutil
import tempfile
from subprocess import check_call
from . import CommandBase

_SETUP_PY_TEMPLATE = """
# Automatically created by: scrapydd
from setuptools import setup, find_packages
setup(
    name         = '%(project)s',
    version      = '1.0',
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = %(settings)s']},
    install_requires = [],
)
""".lstrip()


def _create_default_setup_py(**kwargs):
    with open('setup.py', 'w') as f:
        f.write(_SETUP_PY_TEMPLATE % kwargs)


class PackageCommand(CommandBase):
    def _build_egg(self, dist_dir=None):
        from scrapy.utils.python import retry_on_eintr
        from scrapy.utils.conf import get_config, closest_scrapy_cfg
        closest = closest_scrapy_cfg()
        os.chdir(os.path.dirname(closest))
        if not os.path.exists('setup.py'):
            scrapy_project_settings = get_config()
            settings = scrapy_project_settings.get('settings', 'default')
            project = scrapy_project_settings.get('deploy', 'project')
            _create_default_setup_py(settings=settings, project=project)
        d = dist_dir or 'dist'
        retry_on_eintr(check_call, [sys.executable, 'setup.py', 'clean', '-a', 'bdist_egg', '-d', d],
                    stdout=sys.stdout, stderr=sys.stderr)
        egg = glob.glob(os.path.join(d, '*.egg'))[0]
        return egg, d

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('-o', '--output')


    def run(self, args=None):
        from scrapy.utils.python import retry_on_eintr
        from scrapy.utils.conf import get_config, closest_scrapy_cfg

        output_dir = None
        if args.output:
            output_dir = tempfile.mkdtemp('pancli_pac')
        try:
            egg, d = self._build_egg(dist_dir=output_dir)
            if args.output:
                shutil.copy(egg, args.output)
        finally:
            if output_dir and os.path.exists(output_dir):
                shutil.rmtree(output_dir)
        
        print("Egg has been built: %s" % egg)
