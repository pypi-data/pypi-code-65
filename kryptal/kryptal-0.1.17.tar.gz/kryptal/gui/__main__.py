from kryptal.gui import Application
import sys


def main() -> None:
    Application.create_prod_instance()
    app = Application.get_instance()
    app.setupUncaughtExceptionHandler()
    sys.exit(app.run())

if __name__ == '__main__':
    main()
