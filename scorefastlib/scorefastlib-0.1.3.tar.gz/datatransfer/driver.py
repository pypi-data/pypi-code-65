"""Data Transfer Driver"""
import argparse
import configparser
import json
import logging.config
import sys
from logging.handlers import TimedRotatingFileHandler

from datatransfer import constants
from datatransfer.local_data_transfer import LocalDataTransfer
from datatransfer.watcher import Watcher


class Driver:
    """Application's main program. Client has to provide configuration as an
    argument"""

    def __init__(self, arguments):
        """Load client and application configuration"""

        config = configparser.ConfigParser()
        config.read(arguments.conf)

        # initialize logger
        self.logger = logging.getLogger(
            constants.Constant.logger_module_name.value)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        logger_handler = logging.StreamHandler(sys.stdout)
        logger_handler.setLevel(logging.INFO)
        logger_handler.setFormatter(formatter)
        self.logger.addHandler(logger_handler)
        app_log = ""
        try:
            app_log = config.get(constants.Config.section_log_location.value,
                                 constants.Config.application_log.value)
        except Exception:
            pass
        if len(app_log) == 0:
            app_log = constants.Constant.app_log_path.value

        time_log_handler = TimedRotatingFileHandler(app_log, when="D",
                                                    interval=1, backupCount=10)
        time_log_handler.setFormatter(formatter)
        time_log_handler.setLevel(logging.INFO)
        self.logger.addHandler(time_log_handler)

        file_process_log = ""
        try:
            file_process_log = config.get(
                constants.Config.section_log_location.value,
                constants.Config.file_process_log.value)
        except Exception:
            pass
        if len(file_process_log) == 0:
            file_process_log = constants.Constant.file_checkpoint_path.value

        constants.SavedObj.config[
            constants.Config.file_process_log.value] = file_process_log

        user_name = config.get(
            constants.Config.section_client_credential.value,
            constants.Config.client_credential_user.value)
        password = config.get(constants.Config.section_client_credential.value,
                              constants.Config.client_credential_password.value)
        if len(user_name) == 0 or len(password) == 0:
            self.logger.error("Missing username and password")
            sys.exit(constants.Constant.exit_missing_credential.value)

        constants.SavedObj.config[constants.Config.client_credential_user.value] = user_name
        constants.SavedObj.config[constants.Config.client_credential_password.value] = password

        constants.SavedObj.config[constants.Config.dir_path_list.value] = json.loads(
            config.get(constants.Config.section_data_location.value,
                       constants.Config.dir_path_list.value))
        if type(constants.SavedObj.config[constants.Config.dir_path_list.value]).__name__ != 'list':
            self.logger.error(
                "Provide list of dir name in list [] format in config.conf file")
            sys.exit(constants.Constant.exit_data_path_location.value)
        if len(constants.SavedObj.config[constants.Config.dir_path_list.value]) == 0:
            self.logger.error("Provide dir name in configuration file")
            sys.exit(constants.Constant.exit_data_path_location.value)

        compression_type = ""
        try:
            compression_type = config.get(
                constants.Config.section_app_settings.value,
                constants.Config.compression_type.value)
        except Exception:
            pass
        if len(compression_type) == 0:
            compression_type = constants.Constant.default_compression_type.value
        constants.SavedObj.config[
            constants.Config.compression_type.value] = compression_type
        delete_file = False
        try:
            delete_file = config.getboolean(
                constants.Config.section_app_settings.value,
                constants.Config.delete_file.value)
        except Exception as ex:
            delete_file = False
            self.logger.warning(ex)
        constants.SavedObj.config[
            constants.Config.delete_file.value] = delete_file

    def load(self):
        """Load existing data and initiate watcher for any updates on given directory list"""
        try:
            # add existing data
            self.load_data()
            # add watcher
            w = Watcher()
            w.run()
        except Exception as ex:
            self.logger.error(ex)
            sys.exit("Stopped")

    @staticmethod
    def load_data():
        """Iterate all the given list of directories"""
        file_transfer = LocalDataTransfer()
        for dir_path in constants.SavedObj.config[constants.Config.dir_path_list.value]:
            file_transfer.upload(dir_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', action='store',
                        dest='conf',
                        help='Config file location.')

    args = parser.parse_args()

    if args.conf is None:
        parser.error("missing config file")
        sys.exit()
    driver = Driver(args)
    driver.load()
