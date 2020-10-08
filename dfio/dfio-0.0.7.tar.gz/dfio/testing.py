import base64
import json
import logging
import os

from dfio.utilities import get_local_json_file_as_dict


def if_local_then_test_with_local_pubsub_payload(path_to_payload_json: str):

    # check if environment variable is set to indicate local testing environment
    try:
        test_flag = os.environ.get('DF_LOCAL_TEST_FLAG')
    except:
        test_flag = 0

    # get json payload from local config file
    try:
        test_payload = get_local_json_file_as_dict(path_to_payload_json)
    except:
        test_payload = None

    # assuming main function is called 'main_function' then:
    if test_flag == 1 and test_payload is not None:
        try:
            test_payload_bytes = base64.b64encode(json.dumps(test_payload).encode(encoding='utf-8'))
            test_event = {'data': test_payload_bytes}
            main_function(test_event, 'context')

        except Exception as e:
            logging.exception(e)
    pass
