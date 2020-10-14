
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal
from .core.exc import AppError
from .controllers.base import Base
from .controllers.show_projects import ShowProjects
from .controllers.show_tasks import ShowTasks
from .controllers.process_task import ProcessTask
from .controllers.show_workspaces import ShowWorkspaces
import os
from tinydb import TinyDB
from cement.utils import fs

# configuration defaults
CONFIG = init_defaults('codario')
CONFIG['codario']['foo'] = 'bar'
CONFIG['codario']['db_file'] = '~/.codario/data.json'

def extend_tinydb(app):
    db_file = app.config.get('codario', 'db_file')

    # ensure that we expand the full path
    db_file = fs.abspath(db_file)

    # ensure our parent directory exists
    db_dir = os.path.dirname(db_file)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    app.extend('db', TinyDB(db_file))

class App(App):
    """Codario CLI primary application."""

    base_url = 'https://api.codario.io/v1'

    class Meta:
        label = 'codario'

        # configuration defaults
        config_defaults = CONFIG

        # call sys.exit() on close
        exit_on_close = True

        # load additional framework extensions
        extensions = [
            'yaml',
            'colorlog',
            'jinja2',
            'tabulate'
        ]

        # configuration handler
        config_handler = 'yaml'

        # configuration file suffix
        config_file_suffix = '.yml'

        # set the log handler
        log_handler = 'colorlog'

        # set the output handler
        output_handler = 'tabulate'

        # register handlers
        handlers = [
            Base,
            ShowProjects,
            ShowTasks,
            ProcessTask,
            ShowWorkspaces,
        ]

        hooks = [
            ('post_setup', extend_tinydb),
        ]


class AppTest(TestApp,App):
    """A sub-class of App that is better suited for testing."""

    class Meta:
        label = 'codario'


def main():
    with App() as app:
        try:
            app.run()

        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except AppError as e:
            print('AppError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0


if __name__ == '__main__':
    main()
