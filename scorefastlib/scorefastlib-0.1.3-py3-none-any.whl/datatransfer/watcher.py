"""Watcher"""
import logging
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from datatransfer import constants
from datatransfer.local_data_transfer import LocalDataTransfer


class Watcher:
    """File event based watcher"""

    def __init__(self):
        self.observer = Observer()
        self.logger = logging.getLogger(
            constants.Constant.logger_module_name.value)

    def run(self):
        """Start observer"""
        event_handler = Handler()
        for dir_path in constants.SavedObj.config[constants.Config.dir_path_list.value]:
            self.observer.schedule(event_handler, dir_path, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except Exception as ex:
            self.observer.stop()
            self.logger.error(ex)

        self.observer.join()


class Handler(FileSystemEventHandler):
    """File system handler"""

    @staticmethod
    def on_any_event(event):
        """Implicitly called on any file event"""

        logger = logging.getLogger(constants.Constant.logger_module_name.value)
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            logger.info("received created event - %s.", event.src_path)
            df = LocalDataTransfer()
            df.upload(event.src_path)
