from . import CommandBase
from ..runner2 import empty_settings, SpiderSetting
from ..runner import activate_project, execute
from ..plugin import perform, _pip_installer, load_plugin, _pip_install


def apply_settings(settings, **kwargs):
    figure = kwargs.get('figure')

    plugins_requires = figure.plugins
    plugins = kwargs.get('plugins')
    if plugins:
        plugins_requires.extend(plugins)
    for plugin in plugins_requires:
        _pip_install(plugin)

    plugins_settings = figure.plugin_settings
    plugin_settings = kwargs.get('plugin_settings')
    for plugin_setting in plugin_settings or []:
        ps_k, ps_v = plugin_setting.split('=', 1)
        ps_plugname, ps_setting_key = ps_k.split('.', 1)

        plug_set_dict = plugins_settings.get(ps_plugname)
        if plug_set_dict is None:
            plug_set_dict = {}
            plugins_settings[ps_plugname] = plug_set_dict
        plug_set_dict[ps_setting_key] = ps_v
    
    for plugin_name, plugin_settings_dict in plugins_settings.items():
        plugin = load_plugin(plugin_name)
        plugin.perform(settings, plugin_settings_dict)


class SettingsCommand(CommandBase):
    def add_arguments(self, parser):
        parser.add_argument('--get')
        parser.add_argument('-f', '--file')
        parser.add_argument('--package')

    def run(self, args):
        figure_file = args.file
        figure = empty_settings
        if figure_file:
            figure = SpiderSetting.from_file(figure_file)
        
        package = args.package or figure.package
        project_settings = activate_project(package)

        apply_settings(project_settings, figure=figure)
        argv = ['scrapy', 'settings', '--get', args.get]
        execute(argv, settings=project_settings)

