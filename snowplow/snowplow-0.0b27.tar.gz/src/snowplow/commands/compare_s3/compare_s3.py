import os
import csv
import boto3
from ...core import Utils
from ..list_local import ListLocal

from ..list_s3 import ListS3


class CompareS3:

    def __init__(self, path, bucket, prefix=None, out_path=None, profile=None):
        self.path = Utils.expand_path(path)
        self.bucket = bucket
        self.prefix = prefix
        self.profile = profile
        self._out_path = Utils.expand_path(out_path) if out_path else None
        self._csv_full_path = None
        self._csv_file = None
        self._csv_writer = None
        self._local_data = {}
        self._s3_data = {}
        self._session = None
        self._client = None

        if not os.path.isdir(self.path):
            raise ValueError('Path must be a directory: {0}'.format(self.path))

    CSV_HEADERS = ['path',
                   'reason']

    def execute(self):
        full_s3_path = self.bucket
        if self.prefix is not None:
            full_s3_path = '/'.join([full_s3_path, self.prefix])

        print('Comparing: {0} to: s3://{1}'.format(self.path, full_s3_path))

        self._session = boto3.Session(profile_name=self.profile)
        self._client = self._session.client('s3')

        if self._out_path:
            self._csv_full_path = os.path.join(self._out_path,
                                               '{0}-compare-s3-{1}.csv'.format(os.path.basename(self.path),
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
            ListS3(
                self.bucket,
                prefix=self.prefix,
                out_path=self._out_path,
                profile=self.profile,
                on_list=self._on_list_s3,
                no_print=True
            ).execute()
            Utils.print_inplace('')
            print('Total S3 Files Found: {0}'.format(len(self._s3_data)))

            ListLocal(
                self.path,
                on_list=self._on_list_local,
                no_print=True,
                skip_md5=True
            ).execute()
            Utils.print_inplace('')
            print('Total Local Files Found: {0}'.format(len(self._local_data)))

            total_s3_compared = 0
            total_s3_missing = 0
            total_local_compared = 0
            total_local_missing = 0
            total_out_of_sync = 0

            for key, s3_row in self._s3_data.items():
                total_s3_compared += 1
                local_row = self._local_data.get(key, None)

                if not local_row:
                    total_local_missing += 1
                    reason = 'File not found locally: {0}'.format(key)
                    Utils.eprint(reason)
                    if self._csv_writer:
                        self._csv_writer.writerow({'path': key, 'reason': reason})
                else:
                    if s3_row['size'] != local_row['size']:
                        total_out_of_sync += 1
                        reason = 'Size mismatch: {0}, S3: {1}, Local: {2} '.format(key, s3_row['size'],
                                                                                   local_row['size'])
                        Utils.eprint(reason)
                        if self._csv_writer:
                            self._csv_writer.writerow({'path': key, 'reason': reason})
                Utils.print_inplace('S3 Files Compared: {0}'.format(total_s3_compared))
            Utils.print_inplace('')
            print('Total S3 Files Compared: {0}'.format(total_s3_compared))

            for key, local_row in self._local_data.items():
                total_local_compared += 1
                # Skip the log file if it's in the same directory
                if self._csv_full_path is not None and Utils.expand_path(key) == self._csv_full_path:
                    pass
                else:
                    s3_row = self._s3_data.get(key, None)
                    if not s3_row:
                        total_s3_missing += 1
                        reason = 'File not found in S3: {0}'.format(key)
                        Utils.eprint(reason)
                        if self._csv_writer:
                            self._csv_writer.writerow({'path': key, 'reason': reason})

                Utils.print_inplace('Local Files Compared: {0}'.format(total_local_compared))
            Utils.print_inplace('')
            print('Total Local Files Compared: {0}'.format(total_local_compared))

            print('')
            print('Total Missing in S3: {0}'.format(total_s3_missing))
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

    def _on_list_s3(self, item):
        key = item['path']
        if key in self._s3_data:
            raise Exception('Duplicate path found: {0}'.format(key))
        self._s3_data[key] = item
        if len(self._s3_data) % 100 == 0:
            Utils.print_inplace('S3 Files Found: {0}'.format(len(self._s3_data)))

    def _on_list_local(self, item):
        key = item['path']
        if key in self._local_data:
            raise Exception('Duplicate path found: {0}'.format(key))
        self._local_data[key] = item
        if len(self._local_data) % 100 == 0:
            Utils.print_inplace('Local Files Found: {0}'.format(len(self._local_data)))
