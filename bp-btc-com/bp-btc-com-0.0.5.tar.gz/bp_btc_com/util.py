import requests
import logging
from time import sleep


BTC_URL = 'https://chain.api.btc.com/v3/'
BCH_URL = 'https://bch-chain.api.btc.com/v3/'
BSV_URL = 'https://bsv-chain.api.btc.com/v3/'


sleep_time = 5

def get_url(chain):
    if chain == "btc":
        return BTC_URL
    if chain == "bch":
        return BCH_URL
    return BSV_URL

def call_api(resource, payload=None, chain="btc"):
    """
    Build URL and Make an API request
    :param str resource: url endpoint being called
    :return: json api response
    """
    url = get_url(chain) + resource
    logging.info("calling %s", url)
    if payload:
        response = requests.get(url, params=payload)
    else:
        response = requests.get(url)
    if response.status_code == 403:  # try waiting
        logging.warning("retrying when 403")
        sleep(sleep_time)
        if payload:
            response = requests.get(url, params=payload)
        else:
            response = requests.get(url)
    return handle_response(response)


def handle_response(response):
    """
    Correct the response datatype if returned incorrectly
    :response Requests.models.Response: a response from the api
    :return: response ready for consumption from wrapper
    """
    if response.status_code >= 400:
        logging.warning(response)
        return response.status_code

    data = response.json()
    if data['err_no'] == 0:
        return data['data']
    else:
        logging.info(data['message'])
        return data['message']