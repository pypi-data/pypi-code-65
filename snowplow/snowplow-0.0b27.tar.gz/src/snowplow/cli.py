import argparse
from .commands.new_instance import cli as new_instance_cli
from .commands.list_local import cli as list_local_cli
from .commands.list_s3 import cli as list_local_s3
from .commands.compare_csv import cli as compare_csv_cli
from .commands.compare_s3 import cli as compare_s3_cli

ALL_ACTIONS = [
    list_local_cli,
    list_local_s3,
    compare_s3_cli,
    compare_csv_cli,
    new_instance_cli
]


def main(args=None):
    shared_parser = argparse.ArgumentParser(add_help=False)

    main_parser = argparse.ArgumentParser(description='S3 to Synapse Orchestration')
    subparsers = main_parser.add_subparsers(title='Commands', dest='command')
    for action in ALL_ACTIONS:
        action.create(subparsers, [shared_parser])

    cmd_args = main_parser.parse_args(args)

    if '_execute' in cmd_args:
        cmd_args._execute(cmd_args)
    else:
        main_parser.print_help()
