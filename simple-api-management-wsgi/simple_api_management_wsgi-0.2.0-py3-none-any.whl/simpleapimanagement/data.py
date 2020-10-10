from datetime import datetime
import time
import uuid

class DataHolder(object):
    def __init__(self):
        self.response_chunks = None

        self.status = -1
        self.response_headers = None
        self.request_time = int(round(time.time() * 1000))

    def capture_response_status(self, status, response_headers):
        self.status = int(status.split(' ')[0])
        self.response_headers = response_headers

    def finish_response(self, response_chunks):
        self.response_time = int(round(time.time() * 1000))
        self.response_chunks = response_chunks
        new_response_chunks = []
        stored_response_chunks = []
        for line in response_chunks:
            new_response_chunks.append(line)
            stored_response_chunks.append(line)
        self.response_chunks = stored_response_chunks
        return new_response_chunks


