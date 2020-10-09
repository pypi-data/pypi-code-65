import os
import csv
import boto3
from ...core import Utils


class ListS3:

    def __init__(self, bucket, prefix=None, out_path=None, profile=None, on_list=None, no_print=False):
        self.bucket = bucket
        self.prefix = prefix
        self.profile = profile
        self._out_path = Utils.expand_path(out_path) if out_path else None
        self._csv_full_path = None
        self._csv_file = None
        self._csv_writer = None
        self._on_list = on_list
        self._no_print = no_print
        self._session = None
        self._client = None

    CSV_HEADERS = ['path',
                   'size']

    def execute(self):
        full_s3_path = self.bucket
        if self.prefix is not None:
            full_s3_path = '/'.join([full_s3_path, self.prefix])

        if not self._no_print:
            print('Listing: s3://{0}'.format(full_s3_path))

        self._session = boto3.Session(profile_name=self.profile)
        self._client = self._session.client('s3')

        if self._out_path:
            self._csv_full_path = os.path.join(self._out_path, '{0}-list-s3-{1}.csv'.format(full_s3_path,
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
            paginator = self._client.get_paginator('list_objects')

            iter_args = {'Bucket': self.bucket}
            if self.prefix:
                iter_args['Prefix'] = self.prefix

            page_iter = paginator.paginate(**iter_args)
            for page in page_iter:
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    if self.prefix is not None:
                        key = key.replace(self.prefix, '')[1:]
                    size = obj['Size']

                    total_items += 1
                    total_size += size

                    if not self._no_print:
                        print('{0} : {1}'.format(key, size))

                    item = {
                        'path': key,
                        'size': str(size)
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
