from . import CommandBase

class ListCommand(CommandBase):
    def add_arguments(self, parser):
        parser.add_argument('--package')
        parser.add_argument('-f', '--file')

    def run(self, args):
        from ..runner import activate_project, execute
        from ..runner2 import empty_settings, SpiderSetting
        spec = empty_settings
        if args.file:
            spec = SpiderSetting.from_file(args.file)

        package = args.package or spec.package
        project_settings = activate_project(package)
        argv = ['scrapy', 'list']
        execute(argv, settings=project_settings)