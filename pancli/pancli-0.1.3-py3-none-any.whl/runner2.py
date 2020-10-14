"""
    The runner2 module is designed to run spider in one command.
    To archive this all necessary information should be put into files.
    These files contains:
        * The spider package file. (spider.egg)
        * The spider setting file. (spider.json)
        * (Optional) Plugin packages. (`plugins/xxx.egg`)

    This module can also resolve uninstalled dependencies installation.
"""

import os
import logging
import json
import yaml
import string
import random
import tempfile
import sys
import shutil
from argparse import ArgumentParser
from .runner import main as runner_main
from .runner import activate_project, execute
from .plugin import perform, _pip_installer, load_plugin


logger = logging.getLogger(__name__)


class SpiderSetting(object):
    spider_name = None
    project_name = None
    extra_requirements = None
    spider_parameters = None
    base_settings_module = None
    output = None
    egg_path = None

    def __init__(self, spider_name, extra_requirements=None, spider_parameters=None, project_name=None,
                 base_settings_module=None,
                 output=None,
                 plugin_settings=None, **kwargs):
        self.spider_name = spider_name
        if extra_requirements and isinstance(extra_requirements, str):
            extra_requirements = [x for x in
                                  extra_requirements.split(';') if x]
        self.extra_requirements = extra_requirements or []
        self.spider_parameters = spider_parameters or {}
        self.project_name = project_name
        self.base_settings_module = base_settings_module
        self.output = output
        self.plugin_settings = plugin_settings or {}
        self.plugins = kwargs.get('plugins') or []
        self.package = kwargs.get('package')

    def to_json(self):
        d = {
            'spider_name': self.spider_name,
            'project_name': self.project_name,
            'extra_requirements': self.extra_requirements,
            'settings': self.spider_parameters,
            'base_settings_module': self.base_settings_module,
            'plugin_settings': self.plugin_settings,
        }
        if self.output:
            d['output'] = self.output
        return json.dumps(d)

    @classmethod
    def from_json(cls, json_str):
        parsed = json.loads(json_str)
        return SpiderSetting.from_dict(parsed)

    @classmethod
    def from_dict(cls, dic):
        """
        type: (cls, dict) -> SpiderSetting
        """
        spider_name = dic.get('spider_name') or dic.get('spider')
        project_name = dic.get('project_name')
        extra_requirements = dic.get('extra_requirements')
        spider_parameters = dic.get('settings') or dic.get('spider_parameters')
        base_settings_module = dic.get('base_settings_module')
        output = dic.get('output')
        plugin_settings = dic.get('plugin_settings')


        return cls(spider_name, extra_requirements, spider_parameters,
                   project_name,
                   base_settings_module=base_settings_module,
                   output=output,
                   plugin_settings=plugin_settings,
                   plugins=dic.get('plugins'), 
                   package=dic.get('package'))

    @classmethod
    def from_file(cls, file_path):
        if os.path.splitext(file_path)[-1].lower() in ('.yaml', '.yml'):
            return SpiderSetting.from_yaml(file_path)
        with open(file_path, 'r') as f:
            json_content = f.read()
            return SpiderSetting.from_json(json_content)

    @classmethod
    def from_yaml(cls, file_path):
        with open(file_path, 'r') as f:
            dic = yaml.safe_load(f)
            return SpiderSetting.from_dict(dic)

empty_settings = SpiderSetting.from_dict({})


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def plugin_perform_settings(settings, plugin_name, plugin_settings):
    plugin = load_plugin(plugin_name)
    plugin.perform(settings, plugin_settings)


def main():
    """
      Need put plugin packages(eggs) in the `plugin` folder first.
    :return:
    """
    parser = ArgumentParser()
    parser.add_argument('-f', '--file', dest='file', required=False,
                        default='spider.json', help='The spider settings json '
                                                    'file')
    args = parser.parse_args()
    file_ext = os.path.splitext(args.file)[1]
    if file_ext.lower() in ('.yaml', '.yml'):
        with open(args.file, 'r') as f:
            dic = yaml.load(f, yaml.Loader)
    elif file_ext.lower() == '.json':
        with open(args.file, 'r') as f:
            dic = json.load(f)
    else:
        raise Exception(f'Not supported file type : {args.file}')

    spider_setting = SpiderSetting.from_dict(dic)
    #plugin_settings = spider_setting.plugin_settings
    extra_requirements = spider_setting.extra_requirements
    output_file = spider_setting.output or 'items.jl'
    if extra_requirements:
        for requirement in extra_requirements:
            _pip_installer(requirement)
    # try:
        # settings_module = 'settings_' + randomString(6)
        # settings_package = tempfile.mkdtemp()
        #
        # settings_stream = open(os.path.join(settings_package,
        #                                     settings_module+'.py'), 'w')
        # if plugin_settings:
        #     perform(base_module=spider_setting.base_settings_module,
        #             output_file=settings_stream, input_file=plugin_settings)
        # settings_stream.close()
        # sys.path.append(settings_package)
        # os.environ['SCRAPY_EXTRA_SETTINGS_MODULE'] = settings_module
        # output_file = spider_setting.output_file or 'items.jl'
        # argv = ['scrapy', 'crawl', spider_setting.spider_name, '-o', output_file]
        # for param_key, param_value in spider_setting.spider_parameters.items():
        #     argv += [
        #         '-s',
        #         '%s=%s' % (param_key, param_value)
        #     ]
        # runner_main(argv)
    #     settings = activate_project()
    #     for plugin_name, plugin_settings in \
    #         spider_setting.plugin_settings.items():
    #         plugin_perform_settings(settings, plugin_name, plugin_settings)
    #
    #     for param_key, param_value in spider_setting.spider_parameters.items():
    #         settings.set(param_key, param_value)
    #
    #     execute(['scrapy', 'crawl', spider_setting.spider_name, '-o',
    #              output_file], settings)
    #
    #
    # except SystemExit:
    #     pass
    # finally:
    #     if os.path.exists(settings_package):
    #         shutil.rmtree(settings_package)

    settings = activate_project()
    if spider_setting.plugin_settings:
        for plugin_name, plugin_settings in \
                spider_setting.plugin_settings.items():
            plugin_perform_settings(settings, plugin_name, plugin_settings)

    for param_key, param_value in spider_setting.spider_parameters.items():
        settings.set(param_key, param_value)

    execute(['scrapy', 'crawl', spider_setting.spider_name, '-o',
             output_file], settings)

def print_usage():
    print("usage:")
    print('runner2 <command> [options]')
    print('available commands:')
    print('    crawl')
    print('    list')
    print('')
    print('options:')
    print('-g, --egg egg_file             : specify spider egg file. Default is spider.egg in working folder.')
    print('-s, --settings settings_file   : specify the spider settings json file. Default is spider.json in ')
    print('                                 working folder.')


if __name__ == '__main__':
    main()

