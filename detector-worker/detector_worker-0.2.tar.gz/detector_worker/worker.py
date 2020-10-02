import os
import datetime
import logging
import json
import uuid
import unicodedata
import hashlib
import base64
import traceback

from azure.storage.queue import QueueClient
from azure.storage.blob import BlobClient
from azure.cosmosdb.table import TableService

enough_workers_message = "There are already enough active workers"
workers_long_running = "Workers are active for too long. Going to process as well."
state_table = "workerState"
failure_table = "executionFailures"
wake_up_queue_name = "wake-up"

input_container = "input"
output_container = "output"


def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


class Worker:
    def __init__(self, queue_name, metadata_table_name, should_wake_up=True, worker_name=None):
        connection_string = os.environ['AzureWebJobsStorage']
        self.metadata_table_name = metadata_table_name
        self.table_client = TableService(connection_string=connection_string)
        self.queue = QueueClient.from_connection_string(conn_str=connection_string, queue_name=queue_name)
        self.wake_up_queue = QueueClient.from_connection_string(conn_str=connection_string, queue_name=wake_up_queue_name)
        self.worker_name = worker_name
        self.should_wake_up = should_wake_up
        if 'LtbCloudComponentsStorage' in os.environ:
            self.ltb_connection_string = os.environ['LtbCloudComponentsStorage']


    def trigger_blob(self, blob_name, data=None):
        request_id = self._insert_blob_metadata(blob_name, data)
        self._enqueue(request_id)
        self._wake_up()
        return request_id

    def trigger(self, data):
        request_id = self._insert_request_metadata(data)
        self._enqueue(request_id)
        self._wake_up()
        return request_id

    def process_messages_stateful(self, func, blob_func=None):
        state_row = list(self.table_client.query_entities(state_table))[0]
        now = datetime.datetime.now(datetime.timezone.utc)
        active_count = state_row['ActiveCount'].value
        max_count = state_row['MaxCount'].value
        if active_count >= max_count:
            logging.info(enough_workers_message)
            diff = now - state_row['UpdateDate']
            if diff.total_seconds() > 300:
                logging.info(workers_long_running)
            else:
                return
        else:
            state_row['ActiveCount'].value += 1
            state_row['UpdateDate'] = now
            self.table_client.update_entity(state_table, state_row)

        try:
            while True:
                response = self.queue.receive_messages(messages_per_page=32)
                messages = list(response)
                logging.info(str(len(messages)))
                if len(messages) == 0:
                    break
                for message in messages:
                    self.process_message(message.content, func, blob_func)
                    self.queue.delete_message(message)
        finally:
            state_row['ActiveCount'].value = 0
            state_row['UpdateDate'] = datetime.datetime.now(datetime.timezone.utc)
            self.table_client.update_entity(state_table, state_row)

    def process_message(self, request_id, func, blob_func=None):
        guid, request_hash = self._decode_id(request_id)
        request_entity = self.table_client.get_entity(self.metadata_table_name, guid, request_hash)
        try:
            self._process_request_body(request_entity, func)
            self._process_blob(request_entity, blob_func)
        except Exception as e:
            if 'LtbCloudComponentsStorage' in os.environ:
                track = traceback.format_exc()
                function_failure_entity = {"PartitionKey": self.worker_name, "RowKey": request_id, "FailureMessage": str(e), "StackTrace": track}
                TableService(connection_string=os.environ['LtbCloudComponentsStorage']).insert_entity(failure_table, function_failure_entity)
            else:
                raise

    def get_result(self, request_id):
        guid, request_hash = self._decode_id(request_id)
        entity = self.table_client.get_entity(self.metadata_table_name, guid, request_hash)
        if 'Result' not in entity:
            return ""
        return entity['Result']

    def _insert_request_metadata(self, data):
        serialized_body = json.dumps(data)
        guid, request_hash, request_id = self._generate_id(serialized_body)
        metadata = {"PartitionKey": guid, "RowKey": request_hash, "Request": serialized_body }
        self.table_client.insert_entity(self.metadata_table_name, metadata)
        return request_id

    def _insert_blob_metadata(self, blob_name, data=None):
        guid, request_hash, request_id = self._generate_id(blob_name)
        metadata_entity = {"PartitionKey": guid, "RowKey": request_hash, "BlobName": blob_name}
        if data:
            metadata_entity['Parameters'] = json.dumps(data)
        self.table_client.insert_entity(self.metadata_table_name, metadata_entity)
        return request_id

    def _enqueue(self, request_id):
        self.queue.send_message(base64.b64encode(request_id.encode()).decode())

    def _process_request_body(self, request_entity, func):
        if 'Request' not in request_entity:
            return
        request_body = json.loads(request_entity['Request'])
        response = func(request_body)
        request_entity['Result'] = json.dumps(response)
        self.table_client.update_entity(self.metadata_table_name, request_entity)

    def _process_blob(self, request_entity, func):
        if 'BlobName' not in request_entity:
            return

        blob_name = request_entity['BlobName']
        if 'Parameters' in request_entity:
            params = json.loads(request_entity['Parameters'])
        else:
            params = None

        in_blob = BlobClient.from_connection_string(self.ltb_connection_string, container_name=input_container, blob_name=blob_name)
        out_blob = BlobClient.from_connection_string(self.ltb_connection_string, container_name=output_container, blob_name="%s/%s" % (self.worker_name, blob_name))

        result = []
        for source_segments in self._read_blob_by_chunks(in_blob):
            dnts = func(source_segments, params)
            result.extend(dnts)
        serialized_result = "\n".join(json.dumps(dnts) for dnts in result)
        out_blob.upload_blob(serialized_result, timeout=600)

    def _wake_up(self):
        if self.should_wake_up:
            self.wake_up_queue.send_message("d2FrZSB1cA==")

    @staticmethod
    def _read_blob_by_chunks(input_blob):
        blob_data = input_blob.download_blob()
        last_piece = ""
        for chunk in blob_data.chunks():
            lines = [l.strip() for l in chunk.decode().split("\r\n") if len(l.strip()) > 0]
            lines[0] = last_piece + lines[0]
            last_piece = lines[-1]
            source_segments = [json.loads(unicodedata.normalize("NFKD", l))[0].strip() for l in lines[:-1]]
            yield source_segments

        last_piece = json.loads(unicodedata.normalize("NFKD", last_piece))[0].strip()
        if last_piece and len(last_piece) > 0:
            yield [last_piece]

    @staticmethod
    def _generate_id(data):
        request_id = str(uuid.uuid4()).replace("-", "")
        request_hash = str(hashlib.md5(data.encode()).hexdigest())
        response = "%s_%s" % (request_id, request_hash)
        return request_id, request_hash, response
    
    @staticmethod
    def _decode_id(request_id):
        guid, request_hash = request_id.split("_")
        return guid, request_hash
