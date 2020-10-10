from datetime import datetime
import time
import uuid

class DataHolder(object):
    """Capture the data for a request-response."""
    def __init__(self):
        print('init data holder')

        self.response_chunks = None

        self.status = -1
        self.response_headers = None
        self.request_time = int(round(time.time() * 1000))

    def capture_response_status(self, status, response_headers):
        print('capture response status')
        self.status = status
        self.response_headers = response_headers

    def finish_response(self, response_chunks):
        print('finish response')
        print(response_chunks)
        self.response_time = int(round(time.time() * 1000))
        self.response_chunks = response_chunks
        new_response_chunks = []
        stored_response_chunks = []
        for line in response_chunks:
            print(line)
            new_response_chunks.append(line)
            stored_response_chunks.append(line)
        self.response_chunks = stored_response_chunks
        return new_response_chunks


