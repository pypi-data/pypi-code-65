"""
MeaPy - Python API Wrapper for Measurement Data
"""
import json

import requests

from .loadingconfig import LoadingConfig
from .measurement import Measurement
from .signaldata import SignalData


class MeaPy:
    """Wrapper object for the MaDaM system. Requires an url string and an auth string for creation."""

    def __init__(self, url: str, auth: str):
        """Creates a MaDaM wrapper object. Requires an url and auth parameter.

        Parameters
        ----------
        url : str
            the URL to the MaDaM system
        auth : str
            authentication info which can either be a sessionId oder accessToken
        """
        self.url = url
        self.auth = auth
        self.offset = None
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': self.auth
        }
        self.sessionId = None

    def search(self, query: str, limit=100, offset=None, clearOffset=False) -> list:
        """Searches for a query string in the MaDaM system and returns a list of found measurements.

        Parameters
        ----------

        Returns
        -------
        list
            a list of measurements that are found for the given query
        """
        newOffset = offset
        if not clearOffset:
            newOffset = self.offset

        payload = {
            'queryString': query,
            'limit': limit,
            'offset': newOffset,
            'expansionOptions': {
                'base': {
                    'type': 'all',
                    'includeTopLevelFields': True,
                    'includeRecursiveFields': False,
                    'includeTopLevelLabels': False,
                    'includeRecursiveLabels': False,
                    'ignoreReferenceLists': True,
                    'recursionDepth': 1
                }
            }
        }
        response = requests.post(self.url + 'backend/api/v1/search/search',
                                 data=json.dumps(payload), headers=self.headers)
        responseJson = response.json()

        # raise exception if we got an error from the backend
        if responseJson.get('errorId') is not None:
            raise Exception(responseJson.get('errorId')+': ' +
                            responseJson.get('localizedErrorMessage'))

        self.offset = responseJson.get('offset')
        documentGraph = responseJson.get('documentGraph')
        documents = {} if documentGraph.get(
            'documents') is None else documentGraph.get('documents')
        documentRefs = [] if documentGraph.get(
            'documentRefs') is None else documentGraph.get('documentRefs')
        return list(map(
            lambda docRef: Measurement(documents.get(
                docRef.get('type')).get(docRef.get('id'))),
            documentRefs
        ))

    def loadList(self, measurements: list, config: LoadingConfig, newSession=False) -> dict:
        # current webservice endpoint only supports loading of signals of a single measurement
        result = {}
        for m in measurements:
            result[m] = self.load(m, config, newSession)
        return result

    def load(self, measurement: Measurement, config: LoadingConfig, newSession=False) -> list:
        dataItems = list(map(
            lambda x: {
                "id": x,
                "name": x,
            },
            config.getSignals()
        ))
        imports = [{
            "documentRef": {
                "type": measurement.getType(),
                "id": measurement.getId()
            },
            "importId": "Importer_1"
        }]

        sessionId = self.sessionId
        if newSession:
            sessionId = None
        payload = {
            "action": "channelData",
            "sessionId": sessionId,
            "imports": imports,
            "dataItems": dataItems
        }
        response = requests.post(self.url + 'backend/api/v1/jbeam/actions',
                                 data=json.dumps(payload), headers=self.headers)
        responseJson = response.json()
        self.sessionId = responseJson.get('sessionId')
        return [SignalData(x) for x in responseJson.get('dataItems').values()]
