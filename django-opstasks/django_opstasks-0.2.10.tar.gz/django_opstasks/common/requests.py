from json import dumps
from requests import request
from logging import getLogger
from opsadmin.settings import CONSUL_CONFIGS

LOGGER = getLogger('django')


class OpstasksRequests(object):
    def __init__(self, timeout=5):
        opstasks_hosts = CONSUL_CONFIGS.get(
            'OPSTASKS_HOST', 'opstasks-api.devops.svc.cluster.local')
        self.base_url = f'http://{opstasks_hosts}/'
        self.headers = {'Content-Type': 'application/json'}
        self.timeout = timeout

    def _request(self, method, url, data=None):
        try:
            LOGGER.info('"%s %s"', method, url)
            response = request(method, url, headers=self.headers, data=data, timeout=self.timeout)
            # if response.status_code == 200:
            #     LOGGER.info("return: %s", response.text)
            #     return response
            # LOGGER.error('Faild to run tasks, status code is %s', response.status_code)
            # return False
            LOGGER.info('%s %s', response.status_code, response.text)
            return response.status_code, response.text
        except Exception as error:
            LOGGER.error('Faild to run tasks.')
            LOGGER.exception(error)
            return 1000, error


class TasksRequests(OpstasksRequests):
    def __init__(self):
        super().__init__()
        self.base_url = self.base_url + 'tasks/'

    def database(self):
        kwargs = {
            "method": "GET",
            "url": self.base_url + 'database',
        }
        return self._request(**kwargs)


class NetworksRequests(OpstasksRequests):
    def __init__(self):
        super().__init__()
        self.base_url = self.base_url + 'networks/'

    def service_for_node(self, data):
        kwargs = {
            "method": "POST",
            "url": self.base_url + 'service_for_node',
            "data": dumps(data)
        }
        return self._request(**kwargs)

    def ipsec_tunnel(self, data):
        """
        - update the ipsec.conf、ipsec.secret file
        - then restart strongswan
        - finally check the status of all tunnel
        """
        kwargs = {
            "method": "POST",
            "url": self.base_url + 'ipsec_tunnel',
            "data": dumps(data)
        }
        return self._request(**kwargs)

    def firewalld_rule(self, data):
        kwargs = {
            "method": "POST",
            "url": self.base_url + 'firewalld_rule',
            "data": dumps(data)
        }
        return self._request(**kwargs)
