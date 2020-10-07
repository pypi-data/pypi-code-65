import argparse


class Args:

    @classmethod
    def initialize_args(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument('config', type=str, nargs=1, help='the relevant config section, e.g. LOCAL')
        parser.add_argument('--commit', type=str, nargs='?', choices=['Y', 'N'],
                            help='commit changes to the database')
        parser.add_argument('--filepath', type=str, nargs='?', help='the path to the csv file(s) to load')
        parser.add_argument('--reporting', type=str, nargs='?', help='the directory to save reports to')
        return parser.parse_args()
