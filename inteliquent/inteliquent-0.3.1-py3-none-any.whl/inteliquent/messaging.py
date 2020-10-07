import os
import json
import requests
import logging

from .utils import as_list


logger = logging.getLogger(__name__)


class InteliquentMessaging:

    messaging_url = "https://messagebroker.inteliquent.com/msgbroker/rest"

    def __init__(self, token=None):
        self.token = token

    def parse_send_responses(self, response):
        """
        Accepts the response from a send() call and pulls out a list of the result responses
        """
        try:
            return response["result"]["resultResponses"]
        except KeyError as err:
            raise Exception(
                "Failed to parse out result responses (Missing {}), did the structure change?".format(
                    err
                )
            ) from None

    def send(self, from_number, to_number, text, media_urls=None):
        request_body = {
            "from": from_number,
            "to": as_list(to_number),
            "text": text,
        }
        if media_urls is not None:
            request_body["mediaUrls"] = as_list(media_urls)

        headers = {
            "Authorization": "Bearer {}".format(self.token),
            "Content-type": "application/json",
        }
        result = requests.post(
            os.path.join(self.messaging_url, "publishMessages"),
            data=json.dumps(request_body),
            headers=headers,
        )
        result_json = result.json()

        if not result_json.get("success"):
            error = "Error sending sms [{}]: {}".format(
                result_json.get("reason", "UNKOWN"),
                result_json.get("detail", "Unknown error"),
            )
            logger.warning(error)
            raise Exception(error)

        return result_json["result"]
