import logging
import os
import sys
from configparser import ConfigParser

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")


class Config:
    configParser = ConfigParser()

    @classmethod
    def initialize(cls, config_file_path):
        if not os.path.isfile(config_file_path):
            logging.error(f'Config file {config_file_path} does not exist. Exiting...')
            sys.exit(1)
        cls.configParser.read(config_file_path)

    @classmethod
    def get_section_config(cls, required_section, required_key):
        return cls.configParser.get(required_section, required_key)

    @staticmethod
    def get_yn_boolean(commit):
        commit_bool = False
        if commit == 'Y':
            commit_bool = True
        return commit_bool

    @staticmethod
    def get_db_config(args):
        assert args
        try:
            required_section = args.config[0]
            logging.info(f"Extracting config for '{required_section}'")
            user = Config.get_section_config(required_section, 'user')
            key = Config.get_section_config(required_section, 'key').encode()
            host = Config.get_section_config(required_section, 'host')
            db = Config.get_section_config(required_section, 'db')
            return user, key, host, db

        except Exception as ex:
            logging.error(str(ex))
            sys.exit(1)

    @staticmethod
    def get_script_config(args):
        assert args
        user, key, host, db = Config.get_db_config(args)
        commit = args.commit if 'commit' in args else None
        filepath = args.filepath if 'filepath' in args else None
        reporting = args.reporting if 'reporting' in args else None
        return user, key, host, db, commit, filepath, reporting

    @staticmethod
    def get_extract_config(args):
        assert args
        user, key, host, db = Config.get_db_config(args)
        reporting = args.reporting if 'reporting' in args else None
        return user, key, host, db, reporting
