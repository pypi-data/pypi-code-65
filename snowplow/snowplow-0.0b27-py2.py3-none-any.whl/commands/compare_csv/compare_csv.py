import os
import csv
from ...core import Utils
from ..list_local import ListLocal


class CompareCsv:

    def __init__(self, path, csv_path, out_path=None):
        self.path = Utils.expand_path(path)
        self.csv_path = Utils.expand_path(csv_path)
        self._out_path = Utils.expand_path(out_path) if out_path else None
        self._csv_full_path = None
        self._csv_file = None
        self._csv_writer = None
        self._local_data = {}
        self._csv_data = {}

        if not os.path.isdir(self.path):
            raise ValueError('Path must be a directory: {0}'.format(self.path))

        if not os.path.isfile(self.csv_path):
            raise ValueError('Path must be a CSV file: {0}'.format(self.csv_path))

    CSV_HEADERS = ['path',
                   'reason']

    def execute(self):
        print('Comparing: {0} to: {1}'.format(self.path, self.csv_path))

        if self._out_path:
            self._csv_full_path = os.path.join(self._out_path, '{0}-compare-{1}.csv'.format(os.path.basename(self.path),
                                                                                            Utils.timestamp_str()))
            Utils.ensure_dirs(os.path.dirname(self._csv_full_path))
            self._csv_file = open(self._csv_full_path, mode='w')
            self._csv_writer = csv.DictWriter(self._csv_file,
                                              delimiter=',',
                                              quotechar='"',
                                              fieldnames=self.CSV_HEADERS,
                                              quoting=csv.QUOTE_ALL)
            self._csv_writer.writeheader()

        try:
            skip_md5 = True

            with open(self.csv_path, newline='') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    key = row['path']
                    if key in self._csv_data:
                        raise Exception('Duplicate path found: {0}'.format(key))
                    self._csv_data[key] = row
                    if skip_md5 is True and row['md5'] != '':
                        skip_md5 = False

            ListLocal(
                self.path,
                on_list=self._on_list_local,
                no_print=True,
                skip_md5=skip_md5
            ).execute()
            Utils.print_inplace('')
            print('Total Local Files Found: {0}'.format(len(self._local_data)))

            total_csv_compared = 0
            total_csv_missing = 0
            total_local_compared = 0
            total_local_missing = 0
            total_out_of_sync = 0

            for key, csv_row in self._csv_data.items():
                total_csv_compared += 1
                local_row = self._local_data.get(key, None)

                if not local_row:
                    total_local_missing += 1
                    reason = 'File not found locally: {0}'.format(key)
                    Utils.eprint(reason)
                    if self._csv_writer:
                        self._csv_writer.writerow({'path': key, 'reason': reason})
                else:
                    if csv_row['size'] != local_row['size']:
                        total_out_of_sync += 1
                        reason = 'Size mismatch: {0}, CSV: {1}, Local: {2} '.format(key, csv_row['size'],
                                                                                    local_row['size'])
                        Utils.eprint(reason)
                        if self._csv_writer:
                            self._csv_writer.writerow({'path': key, 'reason': reason})
                    else:
                        if not skip_md5 and csv_row['md5'] != local_row['md5']:
                            total_out_of_sync += 1
                            reason = 'MD5 mismatch: {0}, CSV: {1}, Local: {2} '.format(key, csv_row['md5'],
                                                                                       local_row['md5'])
                            Utils.eprint(reason)
                            if self._csv_writer:
                                self._csv_writer.writerow({'path': key, 'reason': reason})
                Utils.print_inplace('CSV Files Compared: {0}'.format(total_csv_compared))
            Utils.print_inplace('')
            print('Total CSV Files Compared: {0}'.format(total_csv_compared))

            for key, local_row in self._local_data.items():
                total_local_compared += 1

                # Skip the log file if it's in the same directory
                if self._csv_full_path is not None and Utils.expand_path(key) == self._csv_full_path:
                    continue
                if Utils.expand_path(key) == self.csv_path:
                    continue

                csv_row = self._csv_data.get(key, None)
                if not csv_row:
                    total_csv_missing += 1
                    reason = 'File not found in CSV: {0}'.format(key)
                    Utils.eprint(reason)
                    if self._csv_writer:
                        self._csv_writer.writerow({'path': key, 'reason': reason})

                Utils.print_inplace('Local Files Compared: {0}'.format(total_local_compared))
            Utils.print_inplace('')
            print('Total Local Files Compared: {0}'.format(total_local_compared))

            print('')
            print('Total Missing in CSV: {0}'.format(total_csv_missing))
            print('Total Missing Locally: {0}'.format(total_local_missing))
            print('Total Out of Sync: {0}'.format(total_out_of_sync))
        finally:
            if self._csv_file:
                self._csv_file.close()
            if self._csv_full_path:
                print('')
                print('CSV saved to: {0}'.format(self._csv_full_path))
            print('')
            print('Finished')

    def _on_list_local(self, item):
        key = item['path']
        if key in self._local_data:
            raise Exception('Duplicate path found: {0}'.format(key))
        self._local_data[key] = item
        if len(self._local_data) % 100 == 0:
            Utils.print_inplace('Local Files Found: {0}'.format(len(self._local_data)))
