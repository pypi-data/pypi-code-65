'''
Utilities around programatic entry point.
'''


# PyLint doesn't recognize that the decorators for, e.g. munchify, change
# method signature.
# pylint: disable=no-value-for-parameter


import argparse
import logging
import os
from typing import Callable
from typeguard import typechecked
import yaml
import pyconfigurableml.azure
import pyconfigurableml.files
import pyconfigurableml.logging
import pyconfigurableml.munch


config_actions = [
    pyconfigurableml.logging.set_logger_levels,
    pyconfigurableml.azure.resolve_azure_secrets,
    pyconfigurableml.files.ensure_files_exist,
    pyconfigurableml.munch.munchify
]


@typechecked
def default_config_path(file: str) -> str:
    '''
    Returns `(directory containing file)/config.yml` as an absolute path.
    '''
    abs_path = os.path.abspath(file)
    directory = os.path.dirname(abs_path)
    result = os.path.join(directory, 'config.yml')
    return result


@typechecked
def run_no_parse_args(main: Callable[[object, logging.Logger], None],
                      file: str,
                      log_level: str = 'INFO',
                      config_path: str = None) -> None:
    '''
    Handle log levels and parsing a YAML configuration file, **without**
    attempting to parse any command line arguments. Use `default_config_path`
    to determine default configuration path.

        Parameters:
            main: programatic entry point for your program.
            file: should be __file__ in the entry point of your script.
            log_level: base log level.
            config_path: path to configuration object.
    '''
    if config_path is None:
        config_path = default_config_path(file)

    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)

    logging.basicConfig(level=log_level)

    for func in config_actions:
        config = func(config)

    logger = logging.getLogger()
    main(config, logger)


@typechecked
def run(main: Callable[[object, logging.Logger], None],
        file: str,
        name: str = '__main__') -> None:
    '''
    Handle log levels and parsing a YAML configuration file, obtaining path to
    config file using command line argument parsing. The default path to the
    configuration file is `<caller directory>/config.yml`.

        Parameters:
            main: programatic entry point for your program.
            file: should be __file__ in the entry point of your script.
            name: optionally __name__ in your script. This function will only
                  call main if __name__ == '__main__'.
    '''

    if name == '__main__':
        parser = argparse.ArgumentParser()

        parser.add_argument('--config', default=default_config_path(file))
        parser.add_argument('--level', default='INFO')
        args = parser.parse_args()

        run_no_parse_args(main, file, args.level, args.config)
