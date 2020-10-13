# Utilities

import json
from general.variables import MAX_PACKAGE_LEN, ENCODING

def receive_message(client):
    enc_answer = client.recv(MAX_PACKAGE_LEN)
    if isinstance(enc_answer, bytes):
        response_json_format = enc_answer.decode(ENCODING)
        response_dict = json.loads(response_json_format)
        if isinstance(response_dict, dict):
            return response_dict
        raise ValueError
    raise ValueError


def send_message(sock, message):
    message_json_format = json.dumps(message)
    enc_message = message_json_format.encode(ENCODING)
    sock.send(enc_message)
