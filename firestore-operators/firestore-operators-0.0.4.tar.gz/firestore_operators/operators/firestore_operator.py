import sys
import logging

import numpy as np

import csv
import json

from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.contrib.hooks.gcs_hook import GoogleCloudStorageHook


import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


class BaseIterator:
    def __init__(self, filename: str, n_rows: int):
        self.filename = filename
        self.n_rows = n_rows

    def read_next(self):
        pass


class CSVIterator(BaseIterator):
    def read_next(self):
        with open(self.filename, 'r') as csvfile:
            read = True

            header = next(csv.reader([next(csvfile)]))

            while read:
                lines = []
                for _ in range(self.n_rows):
                    try:
                        next_element = next(csvfile)
                        lines.append(next_element)
                    except StopIteration:
                        logging.info("Finished iterating")

                if len(lines) > 0:
                    reader = csv.DictReader(lines, fieldnames=header)

                    yield list(reader)
                else:
                    read = False

class JSONIterator(BaseIterator):
    def read_next(self):
        with open(self.filename, 'r') as jsonfile:
            read = True

            while read:
                lines = []
                for _ in range(self.n_rows):
                    try:
                        next_element = next(jsonfile)
                        lines.append(next_element)
                    except StopIteration:
                        logging.info("Finished iterating")

                if len(lines) > 0:
                    reader = [json.loads(x) for x in lines]

                    yield reader
                else:
                    read = False

class BaseFirestoreOperator(BaseOperator):
    """
    This is the base class for the Firestore operators

    Attributes:
        project_id (str): The project id where the Firestore database is located
        pattern (str): A pattern defines the path to the collection, e.g:
            The number of levels on the path, has to be an even number, so it maps to a document.
            'bar_{foo}//{baz}-{foz}' -> The fields sorrounded by {} will be taken from the record
            this is equivalent to: 'bar_{}/{}-{}'.format(record['foo'], record['baz'], record['foz'])
        map_field (Dict): Dictionary field to function, run function for each field.
    """
    @apply_defaults
    def __init__(self, name: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.name = name
        self.project_id = kwargs['project_id']
        self.pattern = kwargs['pattern']
        self.args = kwargs

    def load_records(self):
        pass

    def execute(self, context):
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {
            'projectId': self.project_id,
        })

        self.db = firestore.client()

        self.load_records()

        self.write_records(self.records, self.pattern)

    def pattern_to_document(self, pattern, record):
        pattern = pattern.format(**record)
        keys = pattern.split('//')
        doc = None

        for i, key in enumerate(keys):
            if doc == None:
                doc = self.db.collection(key)
            else:
                if i % 2 == 0:
                    doc = doc.collection(key)
                else:
                    doc = doc.document(key)
        return doc

    def map_fields(self, record):
        if self.args['map_fields']:
            for field, map_func in self.args['map_fields'].items():
                if field in record:
                    try:
                        record[field] = map_func(record[field])
                    except Exception as e:
                        logging.error(e)
        return record

    def write_records(self, records, pattern):
        try:
            for i, chunk in enumerate(self.records.read_next()):
                batch = self.db.batch()
                for j in range(len(chunk)):
                    record = chunk[j]

                    doc = self.pattern_to_document(pattern, record)

                    record = self.map_fields(record)

                    batch.set(doc, record)

                    logging.info("Writing record {}".format((i*j) + 1))
                batch.commit()
        except StopIteration:
            logging.info("Iterator ended")
        except Exception as e:
            logging.error(e)
            sys.exit(e)


class GCSToFirestoreOperator(BaseFirestoreOperator):
    """
    This operator downloads a file from GCS and uploads it's contents to Firestore

    Attributes:
        args (Dict):
            file_name (str): Name of the destination file
            bucket (str): GCS Bucket
            obj_name (str): Name of the file in GCS
    """
    def load_records(self):
        filename = self.args['file_name']

        hook = GoogleCloudStorageHook()

        hook.download(
            self.args['bucket'],
            self.args['obj_name'],
            filename
        )

        extension = filename.split('.')[-1]
        if extension == 'csv':
            self.records = CSVIterator(
                filename, self.args['batch_size'])
        elif extension == 'json':
            self.records = JSONIterator(
                filename, self.args['batch_size']
            )

class CSVToFirestoreOperator(BaseFirestoreOperator):
    def load_records(self):
        self.records = CSVIterator(
            self.args['filename'], self.args['batch_size'])


class JSONToFirestoreOperator(BaseFirestoreOperator):
    def load_records(self):
        self.records = JSONIterator(
            self.args['filename'], self.args['batch_size'])
