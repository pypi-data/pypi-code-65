from importlib import import_module

import pkg_resources

from humble_tools import cli

for entry_point in pkg_resources.iter_entry_points('toolz_plugins'):
        import_module(entry_point.module_name)

def main():
    cli()
