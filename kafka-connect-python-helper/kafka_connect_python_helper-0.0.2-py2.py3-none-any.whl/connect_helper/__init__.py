import requests
import time
import sys
import logging

class Connector:
    """ Controls single connector """

    __slots__ = 'session', 'base_url', 'name'

    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url
        self.name = None

    def _check_empty_name(self):
        if not self.name:
            logging.error(f"{self.__class__} attribute 'name' not set")
            sys.exit(1)

    def get_remote_config(self, retry=False):
        self._check_empty_name()
        backoff_seconds = 3
        url = f"{self.base_url}/connectors/{self.name}"
        try:
            r = self.session.get(url=url)
            r.raise_for_status() # Raise HTTP exception if the webserver responds with a HTTP exception
            return r
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:
                if not retry:
                    logging.warn(f"Concurrency error while getting remote config. Retrying in {backoff_seconds} seconds...")
                    logging.debug(e)
                    time.sleep(backoff_seconds)
                    return self.get_remote_config(True)
                else:
                    logging.error(f"Concurrency error occurred second time while retrieving remote config. Exiting...")
                    logging.error(e)
                    sys.exit(1)
            logging.error(e)
            sys.exit(1)
        except requests.exceptions.RequestException:
            logging.error(e)
            sys.exit(1)

    def delete(self):
        self._check_empty_name()
        logging.debug(f"Deleting {self.name}")
        url = f"{self.base_url}/connectors/{self.name}"
        try:
            self.session.delete(url=url)
        except self.session.exceptions.RequestException as e:
            logging.error(f"Error occurred in DELETE for {self.name}")
            logging.error(e)
            sys.exit(1)

    def put(self, body):
        self._check_empty_name()
        url = f"{self.base_url}/connectors/{self.name}/config"
        try:
            r = self.session.put(url=url, json=body)
            logging.info(f"Successfully created connect {self.name}")
            return r
        except self.session.exceptions.RequestException as e:
            logging.error(f"Error occurred in PUT for {self.name}")
            logging.error(e)
            sys.exit(1)

    def get_status(self):
        self._check_empty_name()
        url = f"{self.base_url}/connectors/{self.name}/status"
        return self.session.get(url=url)

    def poll_status(self, retry=False):
        i = 0
        max_retries = 90
        backoff_seconds = 2

        self._check_empty_name()
        logging.info(f"Waiting for connector {self.name} to become healthy. Max retries: {max_retries}")
        while i < max_retries:
            try:
                r = self.get_status()
                r.raise_for_status() # Raise HTTP exception if the webserver responds with a HTTP exception
                state = r.json()["connector"]["state"]
                if state == "RUNNING":
                    logging.info(f"Connector {self.name} created successfully in RUNNING state!")
                    return
                elif state == "FAILED":
                    logging.warn(f"Try {i} of {max_retries}: {self.name} created but still in FAILED state. Sleeping {backoff_seconds} seconds")
                else:
                    logging.warn(f"Connector state {state}, sleeping {backoff_seconds}...")
                i += 1
                time.sleep(backoff_seconds)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    if not retry:
                        logging.warn(f"Connector {self.name} doesn't exist yet. Retrying in {backoff_seconds} seconds...")
                        logging.debug(e)
                        time.sleep(backoff_seconds)
                        return self.poll_status(True)
                    else:
                        logging.error(f"Connector {self.name} doesn't exist after retry. Exiting...")
                        logging.error(e)
                        sys.exit(1)
                logging.error(e)
                sys.exit(1)
            except requests.exceptions.RequestException:
                logging.error(e)
                sys.exit(1)
        else:
            logging.error("Too many attempts waiting for connector to become healthy. Exiting...")
            sys.exit(1)

class ConnectHelper():
    """ Initialize Connect session """

    __slots__ = 'session', 'base_url', 'connector'

    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url
        self.connector = Connector(session, base_url)

    def get_connectors(self):
        url = f"{self.base_url}/connectors"
        return self.session.get(url=url)
