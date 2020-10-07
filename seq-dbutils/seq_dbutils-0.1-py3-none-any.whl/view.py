import logging
import sys
from os.path import join, isdir, isfile

from seq_dbutils.connection import Connection

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")


class View:

    def __init__(self, view_dir, session_instance, commit):
        assert isdir(view_dir)
        assert hasattr(session_instance, 'execute')
        assert isinstance(commit, bool)

        self.view_dir = view_dir
        self.session_instance = session_instance
        self.commit = commit

    def drop_and_create_view(self, view_name):
        self.drop_view_if_exists(view_name)
        self.create_view(view_name)

    def drop_view_if_exists(self, view_name):
        drop_sql = f'DROP VIEW IF EXISTS {view_name};'
        logging.info(drop_sql)
        self.session_instance.execute(drop_sql)
        Connection.commit_changes(self.session_instance, self.commit)

    def create_view(self, view_name):
        view_fp = join(self.view_dir, view_name + '.sql')
        if isfile(view_fp):
            with open(view_fp, 'r') as reader:
                create_sql = reader.read()
                create_sql = f'CREATE VIEW {view_name} AS \n' + create_sql
                logging.info(create_sql)
                self.session_instance.execute(create_sql)
                Connection.commit_changes(self.session_instance, self.commit)
        else:
            logging.error(f'Unable to find file: {view_fp}')
            sys.exit(1)
