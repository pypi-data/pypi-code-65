from typing import BinaryIO
from logging import LogRecord, Handler
import os, pathlib, gzip
from datetime import datetime, timedelta


class CompressedLogger(Handler):
    """
    Simple Logging Handler for the python logging module
    Writes logging records into logfiles and automatically
    rotates old log files into gziped archives.
    Number of archives can be limited by days and/or overall archives size.

    """
    def __init__(self,
                 log_path: str,
                 filename: str,
                 live_log_minutes: int = 60 * 3,
                 live_log_count: int = 3,
                 max_archive_size_mb: int = 500,
                 archive_days: int = 14,
                 header: str = ""):
        """
        :param log_path: path where the log files should be stored
        :param filename: base name of the logfile
        :param live_log_minutes: minutes after which a live log is rotated
        :param live_log_count: number of live logs to keep before rotating them into *.gz archives
        :param max_archive_size_mb: maximum cumulative size of all written archive, in megabyte
        :param archive_days: delete logs that are older than the maximum_days limit. Any value <= 0 disables this
        :param header: header that is written into every new logfile on rotation
        """
        Handler.__init__(self)
        self.base_path = self.ensure_path(log_path)
        self.filename = filename
        self.live_log_minutes = live_log_minutes
        self.max_live_logs = live_log_count
        self.max_archive_size: int = max_archive_size_mb * 1024 * 1024
        self.maximum_days = archive_days
        self.header: str = header

        self.log_file: BinaryIO = None
        self.next_log_rotate: datetime = None
        self._open_new_log_file()
        self._delete_old_logs()

    @staticmethod
    def ensure_path(path: str):
        if not os.path.exists(path):
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        return pathlib.Path(path)

    def close(self):
        self._delete_old_logs()
        if self.log_file is not None:
            self.log_file.close()

    def emit(self, record: LogRecord) -> None:
        """
        Emit the record

        Output the record to the file, rotates the log file if necessary
        """

        if self.next_log_rotate < datetime.now():
            self._open_new_log_file()
            self._rotate_live_logs()
            self._delete_old_logs()

        self.log_file.write((self.format(record) + "\n").encode())
        self.log_file.flush()

    def _open_new_log_file(self):
        """
        Close the current logfile and open a new one
        """
        if self.log_file is not None:
            self.log_file.close()
        self.log_file = open(self._next_logfile_name(), 'ab')
        self.next_log_rotate = self._get_next_rotation_ts()

    def _rotate_live_logs(self):
        """
        This iterates through the live log files and moves them into archive
        Also writes the header at the beginning of a new archive.
        """
        live_logs = [str(x) for x in self.base_path.glob(f"{self.filename}*.log")]
        live_logs.sort(key=lambda x: os.path.getctime(x), reverse=True)

        if len(live_logs) > self.max_live_logs:
            old_log = live_logs.pop()
            archive_file = self._get_archive_for_log(old_log)
            include_header = False
            if not os.path.exists(archive_file) and len(self.header) > 0:
                include_header = True

            with open(old_log, "rb") as f_in:
                with gzip.open(archive_file, "ab") as f_out:
                    if include_header:
                        f_out.write((self.header + "\n").encode())
                    f_out.write(f_in.read())

            os.remove(old_log)

    def _get_archive_for_log(self, log_file: str):
        """
        :param log_file: path of the log file that shall be archived
        :return: returns the filename of the archive this log_file should be archived into
        """

        date = datetime.fromtimestamp(os.path.getctime(log_file))
        filename = str(self.base_path / self.filename) + date.strftime("%Y-%m-%d") + ".log.gz"
        return filename

    def _delete_old_logs(self):
        """
        Remove old log files if either the max_archive_size is reached
        or if there are archived older than maximum_days

        This function removes the oldest log files until the
        cumulative size of all log files is below the max_archive_size
        """

        if self.max_archive_size == -1:
            return
        total_size = 0
        log_files = [str(x) for x in self.base_path.glob(f"{self.filename}*.gz")]
        last_day = datetime.today() - timedelta(days=self.maximum_days)
        removed = []

        for file in log_files:
            if self.maximum_days > 0:
                modified_date = datetime.fromtimestamp(os.path.getmtime(file))
                if modified_date < last_day:
                    os.remove(file)
                    removed.append(file)
                    continue
            total_size += os.path.getsize(file)

        for deleted in removed:
            log_files.remove(deleted)

        if len(log_files) == 0:
            return

        log_files.sort(key=lambda x: os.path.getctime(x), reverse=True)
        while total_size > self.max_archive_size:
            del_file = log_files.pop()
            total_size -= os.path.getsize(del_file)
            os.remove(del_file)

    def _get_next_rotation_ts(self) -> datetime:
        """
        :return: timestamp of the next log rotation

        Calculation starts at 00:00:00 of the current day and adds the self.live_log_minutes
        until a time > now() is reached. This will be the new rotation timestamp.
        If this timestamp would be on the next day, rotation will be made at 00:00:00.
        """
        now = datetime.now()
        next_ts = datetime.combine(now.date(), datetime.min.time())     # start at today - 00:00:00
        while next_ts < now:
            next_ts += timedelta(minutes=self.live_log_minutes)

        midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        return min(next_ts, midnight)

    def _next_logfile_name(self) -> str:
        """
        Creates a logname base on the filename given on init.
        This creates a file name based on following scheme:
            {filename}-{current_timestamp}.log
            e.g. logfile-11_35.log
        """
        timestamp = datetime.now().strftime("%H_%M")
        return str(self.base_path / self.filename) + "-" + timestamp + ".log"


