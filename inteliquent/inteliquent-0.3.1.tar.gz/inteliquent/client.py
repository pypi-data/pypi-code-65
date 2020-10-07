from datetime import datetime, timedelta
import os
import json
import requests
import logging


logger = logging.getLogger(__name__)


class InteliquentClient:

    # config = {
    #     "trunk_group": "CHCGIL24TLR_1094",
    # }

    access_token = None
    client_id = None
    message_type = "SMSMMS"
    message_class = "P2P"
    desired_due_date_lead_time = 2
    user = {
        "name": "Telerest",
        "streetNum": "500",
        "streetPreDir": "W",
        "streetName": "Adams",
        "streetType": "St",
        "locationType1": "Ste",
        "locationValue1": "900",
        "city": "Chicago",
        "state": "IL",
        "postalCode": "60661",
        "typeOfService": "B",
    }

    def __init__(self, client_id=None, client_secret=None, **config):
        self.__session = requests.Session()
        # set the content type to json as expected by API
        self.__session.headers.update({"Content-type": "application/json"})

        self.api_url = config.get(
            "api_url", "https://services.inteliquent.com/Services/2.0.0/"
        )
        self.token_url = config.get(
            "token_url", "https://services-token.inteliquent.com/oauth2/token"
        )

        self.user.update(config.get("user", {}))

        if client_id is not None and client_secret is not None:
            self.authenticate(client_id, client_secret)

    def __require_auth(func):
        """
        A helper decorator to be able to throw an expection if client has not successfully authed
        """
        def __check_auth(self, *args, **kwargs):
            if not self.access_token or not self.client_id:
                print("WARNING! Invalid auth!")
                raise Exception("No auth credentials supplied")
            func(self, *args, **kwargs)

        return __check_auth

    def authenticate(self, client_id, client_secret, grant_type="client_credentials"):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "charset": "UTF-8",
        }
        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": grant_type,
        }

        result = requests.post(self.token_url, params=params, headers=headers)
        data = result.json()

        # check for bad creds
        if "error" in data:
            raise Exception(
                "Failed to authenticate: {}".format(
                    data.get("error_description", "Unknown")
                )
            )

        # need to save client ID because it is required by the API definition
        self.client_id = client_id

        self.access_token = data["access_token"]
        self.__session.headers.update(
            {"Authorization": "Bearer {}".format(self.access_token)}
        )
        return data["access_token"]

    def __make_request(self, path, method="post", params={}, data={}):
        url = os.path.join(self.api_url, path)

        # this can be used to ahdnle the missing credentials here
        # as opposed to relying on API to handle with a proper message
        # if not self.access_token or not self.client_id:
        #     raise Exception("No auth credentials supplied")

        return self.__session.request(method, url, params=params, data=json.dumps(data))

    def search_number(self, **opts):
        response_data = {}
        number_type = opts.get("type")

        if number_type in ["tollfree", "local"]:
            area_code = opts.get("area_code", None)
            contains = opts.get("contains", None)
            in_lata = opts.get("in_lata", None)
            in_rate_center = opts.get("in_rate_center", None)
            in_region = opts.get("region", None)
            quantity = 20

            request_body = {
                "privateKey": self.client_id,
                "tnMask": self.tn_mask_converter(area_code, contains),
                "tnWidlcard": area_code,
                "lata": in_lata,
                "rateCenter": in_rate_center,
                "province": in_region,
                "quantity": quantity,
            }
            result = self.__make_request("tnInventory", data=request_body)
            response_data = result.json()

            if response_data["statusCode"] == "200":
                return response_data["tnResult"]
            else:
                raise Exception(
                    "Error searching numbers: {}".format(
                        response_data.get("status", "Unknown")
                    )
                )

    def purchase_number(self, number, caller_id, trunk_group):
        response_data = {}

        formatted_number = number[2:]

        request_body = {
            "privateKey": self.client_id,
            "tnOrder": {
                "customerOrderReference": "TelerestOrder" + number,
                "tnList": {
                    "tnItem": [
                        {
                            "tn": int(formatted_number),
                            "trunkGroup": trunk_group,
                            "endUser": {
                                "name": self.user["name"],
                                "streetNum": self.user["streetNum"],
                                "streetPreDir": self.user["streetPreDir"],
                                "streetName": self.user["streetName"],
                                "streetType": self.user["streetType"],
                                "locationType1": self.user["locationType1"],
                                "locationValue1": self.user["locationValue1"],
                                "city": self.user["city"],
                                "state": self.user["state"],
                                "postalCode": self.user["postalCode"],
                                "typeOfService": self.user["typeOfService"],
                            },
                            "tnFeature": {
                                "callerId": {"callingName": caller_id[0:15]},
                                "messaging": {
                                    "messageType": self.message_type,
                                    "messageClass": self.message_class,
                                },
                            },
                        }
                    ]
                },
            },
        }

        result = self.__make_request("tnOrder", data=request_body)

        result_json = result.json()
        if result_json["statusCode"] == "200":
            response_data = {
                "status": 200,
                "id": result_json["orderId"],
                "number": number,
            }
        else:
            raise Exception(
                "Error purchasing number: {}".format(
                    response_data.get("status", "Unknown")
                )
            )

        return response_data

    def release_number(self, number):
        response_data = {}

        formatted_number = number[2:]

        lead_time = timedelta(days=self.desired_due_date_lead_time)
        desired_due_date = datetime.isoformat(datetime.today() + lead_time)

        request_body = {
            "privateKey": self.client_id,
            "customerOrderReference": "ReleaseNumberOrder{}".format(number),
            "desiredDueDate": str(desired_due_date),
            "tnList": {"tnItem": [{"tn": formatted_number}]},
        }
        result = self.__make_request("tnDisconnect", data=request_body)

        result_json = result.json()
        if result_json["statusCode"] == "200":
            response_data = {
                "status": 200,
                "id": result_json["orderId"],
                "number": number,
            }
        else:
            raise Exception(
                "Error releasing number: {}".format(
                    response_data.get("status", "Unknown")
                )
            )

        return response_data

    def convert_string_to_digits(self, word):
        conversion = ""
        for i in word:
            n = i.lower()
            if n.isdigit():
                conversion += n
            elif n == "*":
                conversion += "x"
            elif "a" <= n <= "c":
                conversion += "2"
            elif "d" <= n <= "f":
                conversion += "3"
            elif "g" <= n <= "i":
                conversion += "4"
            elif "j" <= n <= "l":
                conversion += "5"
            elif "m" <= n <= "o":
                conversion += "6"
            elif "p" <= n <= "s":
                conversion += "7"
            elif "t" <= n <= "v":
                conversion += "8"
            elif "w" <= n <= "z":
                conversion += "9"
        while len(conversion) < 10:
            conversion += "x"
        return conversion

    def tn_mask_converter(self, area_code, contains):
        return self.convert_string_to_digits(
            contains if contains is not None else (area_code or "")
        )
