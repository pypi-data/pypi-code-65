import os
import csv
from ...core import Utils


class ListLocal:

    def __init__(self, path, out_path=None, on_list=None, no_print=False, skip_md5=False):
        self.path = Utils.expand_path(path)
        self._out_path = Utils.expand_path(out_path) if out_path else None
        self._csv_full_path = None
        self._csv_file = None
        self._csv_writer = None
        self._on_list = on_list
        self._no_print = no_print
        self._skip_md5 = skip_md5

        if not os.path.isdir(self.path):
            raise ValueError('Path must be a directory: {0}'.format(self.path))

    CSV_HEADERS = ['path',
                   'size',
                   'md5']

    def execute(self):
        if not self._no_print:
            print('Listing: {0}'.format(self.path))

        if self._out_path:
            self._csv_full_path = os.path.join(self._out_path, '{0}-list-{1}.csv'.format(os.path.basename(self.path),
                                                                                         Utils.timestamp_str()))
            Utils.ensure_dirs(os.path.dirname(self._csv_full_path))
            self._csv_file = open(self._csv_full_path, mode='w')
            self._csv_writer = csv.DictWriter(self._csv_file,
                                              delimiter=',',
                                              quotechar='"',
                                              fieldnames=self.CSV_HEADERS,
                                              quoting=csv.QUOTE_NONNUMERIC)
            self._csv_writer.writeheader()

        total_items = 0
        total_size = 0
        try:
            for root, dirs, files in os.walk(self.path):
                for name in files:
                    full_path = os.path.join(root, name)

                    # We only want files, not links or pipes.
                    if not os.path.isfile(full_path):
                        continue

                    # Skip the log file if it's in the same directory
                    if self._csv_full_path is not None and full_path == self._csv_full_path:
                        continue

                    truncated_path = full_path.replace('{0}{1}'.format(self.path, os.sep), '')
                    size = os.path.getsize(full_path)
                    md5 = '' if self._skip_md5 else Utils.get_md5(full_path)

                    total_items += 1
                    total_size += size

                    if not self._no_print:
                        md5_print = '' if self._skip_md5 else ' : {0}'.format(md5)
                        print('{0} : {1}{2}'.format(truncated_path, size, md5_print))

                    item = {
                        'path': truncated_path.replace('\\', '/'),  # Normalize the path separator for Posix.
                        'size': str(size),
                        'md5': md5
                    }

                    if self._on_list:
                        self._on_list(item)

                    if self._csv_writer:
                        self._csv_writer.writerow(item)
        finally:
            if self._csv_file:
                self._csv_file.close()
            if self._csv_full_path:
                if not self._no_print:
                    print('')
                    print('CSV saved to: {0}'.format(self._csv_full_path))
            if not self._no_print:
                print('')
                print('Total Items: {0}'.format(total_items))
                print('Total Size: {0} ({1})'.format(Utils.pretty_size(total_size), total_size))
                print('Finished')
