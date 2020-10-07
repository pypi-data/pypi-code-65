import logging
import sys
from os.path import join, isdir, isfile, splitext

from seq_dbutils.connection import Connection

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")


class Trigger:

    def __init__(self, trigger_dir, session_instance, commit):
        assert isdir(trigger_dir)
        assert hasattr(session_instance, 'execute')
        assert isinstance(commit, bool)

        self.trigger_dir = trigger_dir
        self.session_instance = session_instance
        self.commit = commit

    def drop_and_create_trigger(self, trigger_filename):
        self.drop_trigger_if_exists(trigger_filename)
        self.create_trigger(trigger_filename)

    def drop_trigger_if_exists(self, trigger_filename):
        trigger_name = splitext(trigger_filename)[0]
        drop_sql = f'DROP TRIGGER IF EXISTS {trigger_name};'
        logging.info(drop_sql)
        self.session_instance.execute(drop_sql)
        Connection.commit_changes(self.session_instance, self.commit)

    def create_trigger(self, trigger_filename):
        trigger_fp = join(self.trigger_dir, trigger_filename)
        if isfile(trigger_fp):
            with open(trigger_fp, 'r') as reader:
                create_sql = reader.read()
                logging.info(create_sql)
                self.session_instance.execute(create_sql)
                Connection.commit_changes(self.session_instance, self.commit)
        else:
            logging.error(f'Unable to find file: {trigger_fp}')
            sys.exit(1)
