import sys
from . import CommandBase


class CrawlCommand(CommandBase):
    def add_arguments(self, parser):
        parser.add_argument('spider', nargs='?')
        parser.add_argument('--package')
        parser.add_argument('-s', '--set', nargs='*', dest='setting_set')
        parser.add_argument('-o', '--output')
        parser.add_argument('--output-format', '-t', dest='format')
        parser.add_argument('-f', '--file')
        parser.add_argument('--logfile')
        parser.add_argument('--ps', '--plugin-setting', nargs='*', dest='plugin_settings')
        parser.add_argument('--loglevel')
        parser.add_argument('--plugin', nargs='*', dest='plugins')

    def run(self, args):
        from ..runner import activate_project, execute
        from ..runner2 import empty_settings, SpiderSetting
        from ..plugin import perform, _pip_installer, load_plugin, _pip_install, _activate_distribution, install_plugin, load_plugins, ensure_plugin

        spec = empty_settings
        if args.file:
            spec = SpiderSetting.from_file(args.file)

        package = args.package or spec.package
        project_settings = activate_project(package)

        output_format = args.format
        output = args.output or spec.output
        
        spider_name = args.spider or spec.spider_name
        if not spider_name:
            print('No spider name specified.')
            sys.exit(1)
        argv = argv=['scrapy', 'crawl', spider_name]

        for setting_k, setting_v in spec.spider_parameters.items():
            project_settings.set(setting_k, setting_v)

        for setting_arg in args.setting_set or []:
            setting_k, setting_v = setting_arg.split('=', 1)
            project_settings.set(setting_k, setting_v)
        
        if output:
            argv += ['-o', output]
        if output_format:
            argv += ['-t', output_format]
        if args.logfile:
            argv += ['--logfile', args.logfile]
        if args.loglevel:
            argv += ['--loglevel', args.loglevel]

        
        # install derective plugins
        plugins_requires = spec.plugins
        if args.plugins:
            plugins_requires.extend(args.plugins)
        for plugin in plugins_requires:
            #dist = _pip_installer(plugin)
            #_activate_distribution(dist)
            ensure_plugin(plugin)
            #_pip_install(plugin)
        load_plugins()

        plugins_settings = spec.plugin_settings
        for plugin_setting in args.plugin_settings or []:
            ps_k, ps_v = plugin_setting.split('=', 1)
            ps_plugname, ps_setting_key = ps_k.split('.', 1)

            plug_set_dict = plugins_settings.get(ps_plugname)
            if plug_set_dict is None:
                plug_set_dict = {}
                plugins_settings[ps_plugname] = plug_set_dict
            plug_set_dict[ps_setting_key] = ps_v
        
        for plugin_name, plugin_settings_dict in plugins_settings.items():
            plugin = load_plugin(plugin_name)
            plugin.perform(project_settings, plugin_settings_dict)

        execute(argv, settings=project_settings)
